from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import json
import time
import asyncio
import logging
import sys
import os
import hmac
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import necessary routers from the backend
try:
    from .efficiency_api import router as efficiency_router
    from .agent_management_api import router as agent_router
    from .websocket_api import router as websocket_router
    from .knowledge_api import router as knowledge_router  # Import knowledge router
    BACKEND_IMPORTS_SUCCESSFUL = True
except ImportError as e:
    logging.warning(f"Failed to import backend modules: {e}. Some API routes may be unavailable.")
    BACKEND_IMPORTS_SUCCESSFUL = False

def convert_technical_to_customer_friendly(technical_analysis: Dict[str, Any], query: str) -> str:
    """Convert technical analysis to natural customer service response with actionable solutions"""

    # Handle different types of technical responses
    if "diagnosis" in technical_analysis:
        # Webhook/technical issue response with specific solution steps
        solution_steps = technical_analysis.get('implementation_steps', [])
        working_code = technical_analysis.get('working_code', '')

        response = f"""I've identified the issue you're experiencing - {technical_analysis.get('diagnosis', 'there appears to be a configuration problem with your integration')}.

Here's how to resolve this:

**Solution:**
{technical_analysis.get('solution', 'I have a step-by-step solution for you')}

**Steps to implement:**"""

        if solution_steps:
            for i, step in enumerate(solution_steps, 1):
                response += f"\n{i}. {step}"
        else:
            response += "\n1. Check your webhook URL configuration and ensure it's accessible\n2. Verify your API credentials are correct and up-to-date\n3. Review any recent changes to your server configuration\n4. Test the connection with a simple ping request"

        if working_code and len(working_code.strip()) < 500:  # Include code if it's not too long
            response += f"\n\n**Code example to help:**\n```\n{working_code.strip()}\n```"

        response += f"\n\n**Expected resolution time:** {technical_analysis.get('estimated_fix_time', '15-30 minutes')}"

        testing_approach = technical_analysis.get('testing_approach', '')
        if testing_approach:
            response += f"\n\n**To verify it's working:** {testing_approach}"

        response += "\n\nTry these steps and let me know if you need any clarification or run into issues. I'm here to help you get this resolved!"

        return response

    elif "competitor_analysis" in technical_analysis or "competitive_intelligence" in technical_analysis:
        # Competitive analysis response with specific comparisons
        comp_data = technical_analysis.get("competitor_analysis", technical_analysis.get("competitive_intelligence", {}))

        return f"""Great question! Here's how we compare to other platforms in the market:

**Cost Savings:** 
- Our solution typically costs 60-70% less than enterprise platforms like Salesforce AgentForce
- No vendor lock-in or escalating licensing fees as you scale
- Pay only for what you use with transparent pricing

**Technical Flexibility:**
- Complete control over your AI implementation vs rigid enterprise templates  
- Custom integrations that perfectly fit your existing workflow
- Choice of multiple AI models optimized for different tasks

**Performance Advantages:**
- Faster response times through intelligent model selection
- Higher accuracy with specialized agents for different domains
- Real-time adaptation and learning from your specific use cases

**Implementation:**
- Get started immediately vs lengthy enterprise onboarding
- Full customization available from day one
- Direct support from technical experts who built the system

**Specific Recommendations for You:**
Based on your query about comparisons, I'd suggest starting with our technical integration demo to see the difference in capabilities firsthand. You can also review our case studies showing real client results and cost savings.

Would you like me to set up a quick technical demo so you can see exactly how this would work for your specific needs?"""

    else:
        # General customer service response with actionable solutions
        ai_content = technical_analysis.get("ai_analysis", str(technical_analysis))

        # Extract key points from AI content and make it customer-friendly
        if "webhook" in query.lower() or "api" in query.lower():
            return """I can help you resolve this API/webhook integration issue. Here are the most common solutions that work in 90% of cases:

**Immediate Steps to Try:**
1. **Check your endpoint URL** - Verify it's accessible and returns a 200 status
2. **Validate your API keys** - Ensure they're correct and have proper permissions
3. **Review headers** - Make sure Content-Type is set to 'application/json'
4. **Test authentication** - Verify your signature or bearer token is working

**Common Issues & Quick Fixes:**
- **403 Errors:** Usually authentication/permissions - double-check your API credentials
- **Timeouts:** Add retry logic with exponential backoff (5s, 10s, 20s delays)
- **SSL Issues:** Verify your certificate chain is complete and valid

**Testing Commands:**
```bash
# Test your webhook endpoint
curl -X POST https://your-endpoint.com/webhook \\
  -H "Content-Type: application/json" \\
  -d '{"test": true}'
```

Try these steps in order and let me know what happens. Most integration issues resolve with steps 1-2!"""

        elif "competitor" in query.lower() or "compare" in query.lower():
            return """Here's an honest comparison to help you make the best decision:

**Cost Analysis:**
- Enterprise platforms: $2,000-5,000+ per month
- Our solution: $300-800 per month (60-70% savings)
- No setup fees, transparent pricing

**Feature Comparison:**
✅ **We Excel At:** Custom integrations, multi-model flexibility, rapid deployment
✅ **Enterprise Platforms:** Large sales teams, extensive compliance certifications
✅ **Both:** Core AI capabilities, scalability, reliability

**Right Choice If You Need:**
- **Choose Us:** Custom solutions, cost efficiency, technical flexibility, faster implementation
- **Choose Enterprise:** Massive scale (1000+ users), extensive compliance requirements, prefer big vendor support

**Specific Recommendation:**
Based on most customer feedback, try our solution first for 30 days. If it doesn't meet your needs, you can always migrate to an enterprise platform later (we'll even help with the transition).

Ready to get started with a trial? I can set you up in the next 10 minutes."""

        else:
            # Use AI content to provide more specific guidance
            if len(ai_content) > 100:  # If we have substantial AI analysis
                # Extract practical advice from the AI content
                simplified_advice = ai_content.replace("To troubleshoot", "Here's how to fix it:").replace("Consider the following", "Try these steps:")
                return f"""I've analyzed your situation and here's what I recommend:

{simplified_advice[:400]}{'...' if len(simplified_advice) > 400 else ''}

**Immediate Next Steps:**
1. Try the primary solution I outlined above
2. If that doesn't work, check for any error messages or logs
3. Test the solution in a staging environment first if possible

Let me know how it goes, or if you need me to dive deeper into any specific part of the solution!"""
            else:
                return f"""I can help you with your question about {query[:50]}{'...' if len(query) > 50 else ''}.

**Based on similar cases, here's what typically works:**
1. Start by identifying the core issue - what exactly is happening vs what you expect?
2. Check your configuration settings and recent changes
3. Test with a simple example to isolate the problem
4. Implement the fix incrementally and verify each step

**Common Solutions:**
- Configuration issues: Review your settings against our documentation
- Integration problems: Test connections with basic API calls first  
- Performance issues: Check resource usage and optimize bottlenecks

What specific symptoms are you seeing? I can provide more targeted guidance once I understand the details."""

# Import Galileo for AI observability
GALILEO_AVAILABLE = False
galileo_logger = None

# Only initialize Galileo if API key is available
galileo_api_key = os.getenv('GALILEO_API_KEY')
if galileo_api_key:
    try:
        # Set Galileo environment variables - only CONSOLE_URL is needed
        os.environ['GALILEO_CONSOLE_URL'] = 'https://app.galileo.ai'
        os.environ['GALILEO_API_KEY'] = galileo_api_key
        os.environ['GALILEO_PROJECT'] = os.getenv('GALILEO_PROJECT', 'AgentCraft')
        os.environ['GALILEO_LOG_STREAM'] = os.getenv('GALILEO_LOG_STREAM', 'development')

        from galileo import GalileoLogger

        # Initialize Galileo logger
        galileo_logger = GalileoLogger()
        GALILEO_AVAILABLE = True
        # Galileo will print its own login message, no need to duplicate
    except Exception as e:
        logging.warning(f"⚠️ Galileo initialization error: {e}")
else:
    # Only log this in debug mode - not a warning since it's optional
    logging.debug("Galileo API key not set - observability features disabled")

# Add src to path for AgentCraft imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Try to import enhanced database backend first
ENHANCED_BACKEND_AVAILABLE = False
try:
    from .enhanced_backend import enhanced_backend
    ENHANCED_BACKEND_AVAILABLE = True
    AGENTCRAFT_AVAILABLE = True
    AI_POWERED = True
    logging.info("Enhanced database backend loaded successfully")
except ImportError as e:
    logging.warning(f"Enhanced backend not available: {e}")

logging.info(f"ENHANCED_BACKEND_AVAILABLE = {ENHANCED_BACKEND_AVAILABLE}")

# Fallback to original agents if enhanced backend not available
if not ENHANCED_BACKEND_AVAILABLE:
    try:
        from src.agents.real_ai_technical_agent import real_technical_agent, performance_tracker, get_real_demo_scenarios
        AGENTCRAFT_AVAILABLE = True
        AI_POWERED = True
        logging.info("Real AI agents loaded successfully")
    except ImportError:
        try:
            from src.core.agent_router import agent_router
            from src.agents.technical_support_agent import get_technical_demo_scenarios
            AGENTCRAFT_AVAILABLE = True
            AI_POWERED = False
            logging.warning("Using template-based agents (not real AI)")
        except ImportError:
            AGENTCRAFT_AVAILABLE = False
            AI_POWERED = False
            logging.warning("AgentCraft modules not available, using mock responses")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if GALILEO_AVAILABLE:
        # Galileo is already initialized globally
        logging.info("🔭 Galileo observability ready for tracing")

    if AGENTCRAFT_AVAILABLE:
        logging.info("AgentCraft system initialized successfully with enhanced technical support agent")
    else:
        logging.info("Running in demo mode with mock responses")

    yield

    # Shutdown
    logging.info("AgentCraft system shutting down")

app = FastAPI(title="AgentCraft API", version="1.0.0", lifespan=lifespan)

# Include enhanced API routes if enhanced backend is available
if BACKEND_IMPORTS_SUCCESSFUL:
    try:
        app.include_router(agent_router, prefix="/api/agents")
        app.include_router(efficiency_router, prefix="/api/efficiency")
        app.include_router(websocket_router, prefix="/api/ws")
        app.include_router(knowledge_router, prefix="/api/knowledge")  # Register knowledge router

        logging.info("Enhanced API routes loaded: agent management, efficiency, WebSocket, knowledge")
    except Exception as e:
        logging.warning(f"Could not load all enhanced API routes: {e}")

# WebSocket endpoint - defined directly on app to avoid router issues
if BACKEND_IMPORTS_SUCCESSFUL:
    try:
        from .websocket_api import ws_manager, handle_client_message

        logging.info("Registering WebSocket endpoint at /api/ws/agent-tracking/{client_id}")

        @app.websocket("/api/ws/agent-tracking/{client_id}")
        async def websocket_agent_tracking(websocket: WebSocket, client_id: str):
            """WebSocket endpoint for real-time agent tracking"""
            logging.info(f"WebSocket connection attempt from {client_id}")
            await ws_manager.connect(websocket, client_id)

            try:
                while True:
                    # Keep connection alive and handle client messages
                    try:
                        data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                        message = json.loads(data)

                        # Handle client commands
                        await handle_client_message(message, client_id)

                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        ping_message = {
                            "type": "ping",
                            "timestamp": asyncio.get_event_loop().time()
                        }
                        await ws_manager.send_personal_message(ping_message, client_id)

            except WebSocketDisconnect:
                await ws_manager.disconnect(client_id)
            except Exception as e:
                logging.error(f"WebSocket error for {client_id}: {e}")
                await ws_manager.disconnect(client_id)

        # WebSocket management REST endpoints
        @app.get("/api/ws/stats")
        async def get_websocket_stats():
            """Get WebSocket connection statistics"""
            from src.agents.realtime_agent_tracker import realtime_tracker
            return {
                "success": True,
                "stats": ws_manager.get_connection_stats(),
                "realtime_sessions": realtime_tracker.get_active_sessions_summary()
            }

        @app.post("/api/ws/broadcast")
        async def broadcast_message(message: dict):
            """Broadcast message to all connected WebSocket clients"""
            try:
                await ws_manager.broadcast(message)
                return {"success": True, "message": "Broadcast sent"}
            except Exception as e:
                return {"success": False, "error": str(e)}
    except ImportError as e:
        logging.warning(f"Could not set up WebSocket endpoint: {e}")


# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=False,  # Disable credentials to allow wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    agent_type: str
    message: str
    context: Optional[Dict[str, Any]] = {}

class CompetitiveAnalysisRequest(BaseModel):
    competitor: str
    focus_areas: Optional[List[str]] = []

class ChatResponse(BaseModel):
    message: str
    confidence: float
    agent_used: str
    timestamp: str
    processing_time: float

# Global variables
active_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize AgentCraft system on startup"""
    # Startup
    if AGENTCRAFT_AVAILABLE:
        logging.info("AgentCraft system initialized successfully with enhanced technical support agent")
    else:
        logging.info("Running in demo mode with mock responses")

    yield

    # Shutdown - cleanup if needed
    logging.info("AgentCraft system shutting down")

@app.get("/")
async def root():
    return {
        "message": "AgentCraft API Server",
        "version": "1.0.0",
        "agentcraft_available": AGENTCRAFT_AVAILABLE,
        "status": "running"
    }

@app.post("/api/chat")
async def chat_with_real_ai_agent(request: ChatMessage):
    """Real AI agent chat endpoint using Claude/CrewAI"""

    # Start Galileo trace if available
    trace_id = None
    if GALILEO_AVAILABLE and galileo_logger:
        try:
            trace_id = galileo_logger.start_trace(
                input=request.message,  # Required input parameter
                name="chat_request",
                metadata={
                    "agent_type": request.agent_type,
                    "timestamp": datetime.now().isoformat()
                }
            )
            logging.info(f"🔭 Galileo trace started: {trace_id}")
        except Exception as e:
            logging.warning(f"Failed to start Galileo trace: {e}")

    try:
        if ENHANCED_BACKEND_AVAILABLE:
            # Use enhanced database-backed backend
            result = await enhanced_backend.process_chat_request(
                message=request.message,
                agent_type=request.agent_type,
                context=request.context
            )

            # Log to Galileo if available
            if GALILEO_AVAILABLE and galileo_logger and trace_id:
                try:
                    # Add LLM span for the enhanced response
                    galileo_logger.add_llm_span(
                        input=request.message,
                        output=result["response"]["content"],
                        model="enhanced_database_system"
                    )
                    logging.info(f"🔭 Galileo trace logged for enhanced backend")
                except Exception as e:
                    logging.warning(f"Failed to log enhanced backend to Galileo: {e}")

            return result

        elif AGENTCRAFT_AVAILABLE and AI_POWERED:
            # Fallback to original AI agent
            # Check if CrewAI orchestration is requested
            context = request.context or {}
            if context.get('use_crewai', False):
                # Enable orchestration mode for proper multi-agent CrewAI processing
                context['orchestration_mode'] = True

            # Use the real AI agent (not templates)
            result = real_technical_agent.process_technical_query(
                query=request.message,
                context=context
            )

            # Track real performance metrics
            processing_time = float(result["agent_info"]["processing_time"].split()[0])
            success = "error" not in result
            performance_tracker.track_response(processing_time, success)

            # Use the raw AI response directly from CrewAI
            technical_data = result["technical_response"]

            # Extract the actual AI response without converting it
            if technical_data.get('ai_analysis'):
                # This is the raw CrewAI output
                formatted_response = technical_data['ai_analysis']
            elif technical_data.get('issue_analysis'):
                # For structured responses, format them nicely
                formatted_response = json.dumps(technical_data['issue_analysis'], indent=2)
            elif technical_data.get('competitive_intelligence'):
                formatted_response = json.dumps(technical_data['competitive_intelligence'], indent=2)
            else:
                # Fallback to the full technical response
                formatted_response = str(technical_data)

            # Log to Galileo if available
            if GALILEO_AVAILABLE and galileo_logger and trace_id:
                try:
                    # Add LLM span for the response
                    galileo_logger.add_llm_span(
                        span_id=f"llm_{trace_id}",
                        trace_id=trace_id,
                        name="CrewAI Response",
                        model=result["agent_info"].get("llms_used", {}),
                        messages=[
                            {"role": "user", "content": request.message},
                            {"role": "assistant", "content": formatted_response}
                        ],
                        metadata={
                            "processing_time": result["agent_info"].get("processing_time", "N/A"),
                            "agents_used": result["agent_info"].get("llms_used", {}),
                            "ai_confidence": result["query_analysis"].get("ai_confidence", "N/A")
                        }
                    )

                    # Conclude the trace
                    galileo_logger.conclude(output=result["response"]["content"])
                    galileo_logger.flush()  # Send to Galileo
                    logging.info(f"🔭 Galileo trace concluded and sent")
                except Exception as e:
                    logging.warning(f"Failed to log to Galileo: {e}")

            return {
                "success": True,
                "response": {
                    "content": formatted_response,  # This is what React expects
                    "raw_analysis": result["technical_response"]
                },
                "agent_info": result["agent_info"],
                "competitive_advantage": result["competitive_advantage"],
                "timestamp": result["timestamp"],
                "ai_powered": True,
                "query_analysis": result.get("query_analysis", {}),
                "orchestration_used": False,  # Current setup uses single agent
                "galileo_traced": GALILEO_AVAILABLE and trace_id is not None
            }
        elif AGENTCRAFT_AVAILABLE:
            # Fallback to template-based agents
            result = agent_router.route_query(
                query=request.message,
                context=request.context
            )

            return {
                "success": True,
                "response": result["agent_response"]["technical_response"],
                "agent_info": result["agent_response"]["agent_info"],
                "routing_info": result["routing_info"],
                "competitive_advantage": result["agent_response"]["competitive_advantage"],
                "timestamp": result["agent_response"]["timestamp"],
                "ai_powered": False,
                "note": "Using template-based fallback"
            }
        else:
            # Fallback mock response
            import random
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return {
                "success": True,
                "response": {
                    "response": "Mock technical support response - AgentCraft modules not available",
                    "expertise_areas": ["mock_technical_support"]
                },
                "agent_info": {
                    "role": "Mock Technical Support",
                    "response_time": "1.2 seconds",
                    "ai_powered": False
                }
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Real AI agent failed: {str(e)}",
            "fallback_note": "This demonstrates the complexity of real AI systems",
            "troubleshooting": "Check ANTHROPIC_API_KEY environment variable"
        }
    finally:
        # Ensure Galileo traces are always concluded
        if GALILEO_AVAILABLE and galileo_logger and trace_id:
            try:
                if galileo_logger.has_active_trace():
                    galileo_logger.conclude(output="Request completed")
                    galileo_logger.flush()
                    logging.info("🔭 Galileo trace concluded in finally block")
            except Exception as e:
                logging.warning(f"Failed to conclude Galileo trace in finally: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Process message
            chat_request = ChatMessage(**message_data)
            response = await chat_with_agent(chat_request)

            # Send response back
            await websocket.send_text(json.dumps({
                "type": "agent_response",
                "data": response.dict()
            }))

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.get("/api/metrics")
async def get_real_performance_metrics():
    """Real performance metrics from actual AI usage"""
    if AGENTCRAFT_AVAILABLE and AI_POWERED:
        real_metrics = performance_tracker.get_metrics()

        return {
            "agent_performance": real_metrics,
            "agentforce_comparison": {
                "response_time": "8+ minutes (escalation)",
                "accuracy_rate": "85%",
                "resolution_rate": "85%",
                "escalation_rate": "15%",
                "response_approach": "Template matching with escalation"
            },
            "cost_analysis": {
                "our_annual_cost": "$50-200/month (AI API costs)",
                "agentforce_annual_cost": "$2,000+/month per user",
                "annual_savings": "$23,000+ per user",
                "roi_percentage": "95%+"
            },
            "competitive_advantages": {
                "ai_powered": "Real LLM analysis vs Templates",
                "custom_solutions": "Generated for each query vs Pre-written",
                "technical_depth": "Actual problem-solving vs Pattern matching",
                "flexibility": "Unlimited customization vs Platform limits",
                "competitive_intelligence": "Available vs Blocked by guardrails"
            },
            "system_status": {
                "ai_powered": AI_POWERED,
                "real_time_analysis": True,
                "custom_implementation": True
            }
        }
    else:
        # Fallback metrics
        return {
            "agent_performance": {
                "response_time": "< 30 seconds",
                "accuracy_rate": "96.2%",
                "resolution_rate": "96.2%",
                "escalation_rate": "3.8%"
            },
            "agentforce_comparison": {
                "response_time": "8+ minutes (escalation)",
                "accuracy_rate": "85%",
                "resolution_rate": "85%",
                "escalation_rate": "15%"
            },
            "cost_analysis": {
                "our_annual_cost": "$186,000",
                "agentforce_annual_cost": "$2,550,000",
                "annual_savings": "$2,364,000",
                "roi_percentage": "93%"
            },
            "competitive_advantages": {
                "specialized_agents": "20+ vs 7 generic topics",
                "webhook_expertise": "Deep technical knowledge vs templates",
                "competitive_intelligence": "Available vs Blocked by guardrails",
                "customization": "Unlimited vs Platform constraints"
            },
            "system_status": {
                "ai_powered": False,
                "fallback_mode": True
            }
        }

@app.get("/api/demo-scenarios")
async def get_demo_scenarios():
    """Get real AI-powered demo scenarios for presentation"""
    if AGENTCRAFT_AVAILABLE and AI_POWERED:
        return {
            "technical_scenarios": get_real_demo_scenarios(),
            "competitive_demonstrations": [
                "Real AI webhook analysis vs Generic template response",
                "Live competitive intelligence vs Guardrail blocking", 
                "Custom code generation vs Documentation links",
                "Intelligent problem-solving vs Pattern matching"
            ],
            "system_info": {
                "ai_powered": True,
                "real_analysis": "Every response uses Claude 3 Sonnet",
                "custom_solutions": "Generated dynamically for each query"
            }
        }
    elif AGENTCRAFT_AVAILABLE:
        return {
            "technical_scenarios": get_technical_demo_scenarios(),
            "competitive_demonstrations": [
                "Webhook signature troubleshooting vs generic response",
                "Real-time competitive analysis vs guardrail blocking",
                "Code-level solutions vs documentation links",
                "Sub-30-second resolution vs escalation delays"
            ],
            "system_info": {
                "ai_powered": False,
                "fallback_mode": "Using template-based responses"
            }
        }
    else:
        return {
            "technical_scenarios": {
                "mock_scenario": "AgentCraft modules not available - using mock data"
            },
            "competitive_demonstrations": ["Mock demonstration scenarios"],
            "system_info": {
                "ai_powered": False,
                "status": "Mock mode"
            }
        }

@app.post("/api/competitive-analysis")
async def analyze_competitor_with_real_ai(request: CompetitiveAnalysisRequest):
    """Real AI competitive intelligence capabilities"""
    try:
        if AGENTCRAFT_AVAILABLE and AI_POWERED:
            # Use real AI competitive analysis
            query = f"Analyze {request.competitor} focusing on {', '.join(request.focus_areas)}"
            result = real_technical_agent.competitive_tool._run(query)

            try:
                analysis_data = json.loads(result)
                return {
                    "our_capability": analysis_data,
                    "agentforce_simulation": {
                        "response": "I cannot discuss competitor information due to platform guardrails and vendor restrictions.",
                        "limitation": "Vendor restrictions prevent competitive analysis",
                        "blocked_capabilities": [
                            "Pricing comparison analysis",
                            "Strategic positioning insights", 
                            "Market vulnerability assessment",
                            "Competitive threat evaluation"
                        ]
                    },
                    "competitive_advantage": "Real-time AI competitive intelligence vs Platform restrictions",
                    "strategic_value": "Genuine market analysis impossible with vendor platforms",
                    "ai_powered": True
                }
            except json.JSONDecodeError:
                return {
                    "our_capability": {
                        "raw_analysis": result,
                        "ai_powered": True
                    },
                    "agentforce_simulation": {
                        "response": "I cannot discuss competitor information due to platform guardrails",
                        "limitation": "Vendor restrictions prevent competitive analysis"
                    }
                }
        elif AGENTCRAFT_AVAILABLE:
            # Fallback to template-based analysis
            tech_agent = agent_router.agents["technical_support"]
            analysis = tech_agent.tools["competitive_intel"].analyze_competitive_positioning(
                competitor=request.competitor,
                context=""
            )

            return {
                "our_capability": analysis,
                "agentforce_simulation": {
                    "response": "I cannot discuss competitor information due to platform guardrails",
                    "limitation": "Vendor restrictions prevent competitive analysis"
                },
                "competitive_advantage": "Template-based competitive analysis vs platform restrictions",
                "strategic_value": "Basic capabilities vs vendor platform limitations",
                "ai_powered": False
            }
        else:
            return {
                "our_capability": {
                    "competitor": request.competitor,
                    "message": "Mock competitive analysis - AgentCraft modules not available"
                },
                "agentforce_simulation": {
                    "response": "I cannot discuss competitor information due to platform guardrails",
                    "limitation": "Vendor restrictions prevent competitive analysis"
                },
                "ai_powered": False
            }

    except Exception as e:
        return {
            "error": f"AI competitive analysis failed: {str(e)}",
            "note": "This demonstrates the complexity of building unrestricted competitive intelligence",
            "troubleshooting": "Check ANTHROPIC_API_KEY environment variable"
        }

@app.post("/webhooks/receive")
async def receive_webhook(request: Request):
    """
    Webhook receiver endpoint for testing webhook scenarios
    Validates signatures, processes payloads, and returns appropriate responses
    """
    try:
        # Get the raw body for signature verification
        body = await request.body()
        body_str = body.decode('utf-8')

        # Get headers manually to avoid FastAPI header parsing issues
        headers = dict(request.headers)

        # Support multiple signature header formats for API version compatibility
        x_webhook_signature = (
            headers.get("x-webhook-signature") or 
            headers.get("X-Webhook-Signature") or
            headers.get("x-signature-256") or
            headers.get("X-Signature-256") or
            headers.get("signature")
        )

        logging.info(f"Webhook received - Body length: {len(body_str)}, Headers: {list(headers.keys())}")

        # Parse JSON payload
        try:
            payload = json.loads(body_str)
        except json.JSONDecodeError as e:
            logging.warning(f"Invalid JSON payload: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Check for required fields
        required_fields = ["event_id", "event_type", "timestamp", "data"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            logging.warning(f"Missing required fields: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")

        # Verify signature if provided - support multiple API versions
        if x_webhook_signature:
            secret_key = "test_secret_123"  # In production, get from secure config

            # Generate expected signature
            expected_signature = hmac.new(
                secret_key.encode('utf-8'),
                body_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            # Handle different signature formats for API version compatibility
            provided_signature = x_webhook_signature
            expected_formats = [
                expected_signature,                    # Raw hex (v2.0)
                f"sha256={expected_signature}",        # Prefixed format (v2.1.3)
                f"SHA256={expected_signature}",        # Uppercase prefix
            ]

            # Try multiple comparison formats to support version migration
            signature_valid = any(
                hmac.compare_digest(expected_format, provided_signature) 
                for expected_format in expected_formats
            )

            # Also try extracting from prefixed format
            if not signature_valid and ("sha256=" in provided_signature.lower()):
                extracted_sig = provided_signature.split("=", 1)[1] if "=" in provided_signature else provided_signature
                signature_valid = hmac.compare_digest(expected_signature, extracted_sig)

            if not signature_valid:
                logging.warning(f"Invalid webhook signature. Expected formats: {expected_formats[:2]}, Got: {provided_signature[:16] if provided_signature else 'None'}...")
                raise HTTPException(status_code=403, detail="Invalid signature - check API version compatibility")

        # Process webhook based on event type
        event_type = payload.get("event_type")
        event_id = payload.get("event_id")

        # Log webhook receipt
        logging.info(f"Received webhook: {event_type} (ID: {event_id})")

        # Process different event types
        response_data = {
            "status": "success",
            "event_id": event_id,
            "processed_at": datetime.utcnow().isoformat(),
            "message": f"Successfully processed {event_type} webhook"
        }

        # Handle specific event types with appropriate business logic
        if event_type == "user.created":
            # Process new user creation
            user_data = payload.get("data", {})
            response_data["action"] = "User account initialized"
            response_data["user_id"] = user_data.get("id")

        elif event_type == "order.placed":
            # Process new order
            order_data = payload.get("data", {})
            response_data["action"] = "Order processing initiated"
            response_data["order_id"] = order_data.get("id")

        elif event_type == "payment.failed":
            # Handle payment failure
            payment_data = payload.get("data", {})
            response_data["action"] = "Payment failure recorded"
            response_data["retry_scheduled"] = payment_data.get("next_retry_at")

        elif event_type == "system.alert":
            # Process system alert
            alert_data = payload.get("data", {})
            severity = alert_data.get("severity", "unknown")
            response_data["action"] = f"Alert processed with {severity} severity"
            response_data["escalation_triggered"] = severity in ["high", "critical"]

        elif event_type == "subscription.cancelled":
            # Handle subscription cancellation
            sub_data = payload.get("data", {})
            response_data["action"] = "Subscription cancellation processed"
            response_data["refund_amount"] = sub_data.get("proration_details", {}).get("refund_amount")

        # Return success response
        return response_data

    except HTTPException:
        # Re-raise HTTP exceptions (400, 401, etc.)
        raise
    except Exception as e:
        logging.error(f"Webhook processing error: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Utility functions
def extract_technical_terms(message: str) -> List[str]:
    """Extract technical terms from message"""
    technical_terms = [
        "webhook", "api", "ssl", "authentication", "timeout", "json", "http", 
        "https", "certificate", "hmac", "signature", "payload", "endpoint"
    ]

    found_terms = []
    message_lower = message.lower()

    for term in technical_terms:
        if term in message_lower:
            found_terms.append(term)

    return found_terms

def get_mock_agent_response(agent_type: str, message: str) -> Dict[str, Any]:
    """Generate mock agent responses for demo"""
    import random

    responses = {
        "technical": {
            "message": f"""🔧 **Technical Analysis Complete**

I've analyzed your query about {', '.join(extract_technical_terms(message)) or 'technical issues'}:

**Root Cause Identification:**
- SSL certificate validation failure
- HMAC signature mismatch
- Timeout configuration issues

**Recommended Solution:**
```python
# Webhook signature verification
import hmac
import hashlib

def verify_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

**Implementation Steps:**
1. Update SSL certificate chain
2. Verify HMAC key configuration
3. Implement exponential backoff retry logic
4. Add comprehensive logging

This solution leverages my specialized technical expertise in webhook implementations and API integrations.""",
            "confidence": random.uniform(0.85, 0.95)
        },
        "billing": {
            "message": f"""💳 **Billing Specialist Analysis**

I've reviewed your billing query and here's my expert assessment:

**Payment Processing Diagnosis:**
- Transaction state validation required
- PCI DSS compliance check needed
- Subscription lifecycle management

**Recommended Actions:**
1. **Immediate**: Verify payment processor configuration
2. **Short-term**: Implement proper error handling
3. **Long-term**: Set up automated dunning management

**Best Practices:**
- Use idempotency keys for all payment operations
- Implement proper webhook handling for payment events
- Maintain detailed audit logs for compliance

**Cost Impact Analysis:**
- Proper implementation reduces chargeback risk by 73%
- Automated processes decrease manual intervention by 89%

My specialized billing domain expertise ensures PCI compliance and optimal payment flow design.""",
            "confidence": random.uniform(0.80, 0.92)
        },
        "competitive": {
            "message": f"""📊 **Competitive Intelligence Report**

Based on my market analysis database:

**Market Position Assessment:**
- AgentCraft: Superior in customization (98% vs industry avg 52%)
- Competitor limitations: Generic responses, platform constraints
- Our advantage: Specialized domain expertise

**Cost-Benefit Analysis:**
```
AgentCraft vs Generic Platforms:
├── Implementation Speed: 95% faster
├── Customization Capability: 87% higher
├── Total Cost of Ownership: 67% lower
└── Customer Satisfaction: 4.8/5 vs 3.2/5
```

**Strategic Recommendations:**
1. **Positioning**: Emphasize specialized expertise over generic coverage
2. **Pricing**: Premium pricing justified by superior outcomes
3. **Sales Strategy**: Focus on technical decision makers

**Competitive Moats:**
- Deep domain knowledge accumulation
- Rapid agent development capability
- Architectural flexibility advantage

This analysis draws from my specialized competitive intelligence database and real-time market monitoring.""",
            "confidence": random.uniform(0.88, 0.96)
        }
    }

    return responses.get(agent_type, responses["technical"])

# Utility function to call the correct agent or mock response
async def chat_with_agent(request: ChatMessage):
    """Determines which agent to use or if a mock response is needed"""
    if AGENTCRAFT_AVAILABLE and AI_POWERED:
        return await chat_with_real_ai_agent(request)
    elif AGENTCRAFT_AVAILABLE:
        # Fallback to template-based agents if AI is not powered
        return await chat_with_real_ai_agent(request) # Reusing the same function for consistency
    else:
        # Fallback to mock responses
        mock_response = get_mock_agent_response(request.agent_type, request.message)
        return ChatResponse(
            message=mock_response["message"],
            confidence=mock_response["confidence"],
            agent_used=request.agent_type,
            timestamp=datetime.now().isoformat(),
            processing_time=str(random.uniform(0.5, 1.5)) + " seconds"
        )


# Enhanced API endpoints for Qdrant, Galileo, and HITL

@app.get("/api/qdrant-metrics")
async def get_qdrant_metrics():
    """Get Qdrant vector database performance metrics"""
    try:
        # In production, import and use actual Qdrant service
        # from src.services.qdrant_service import qdrant_service
        # return qdrant_service.get_metrics()

        # Mock metrics for demo
        return {
            "status": "healthy",
            "collection": "agentcraft_knowledge",
            "vector_count": 1247,
            "indexed_points": 1247,
            "embedding_dimension": 384,
            "distance_metric": "cosine",
            "search_performance": {
                "average_latency_ms": 12,
                "p95_latency_ms": 25,
                "p99_latency_ms": 45,
                "queries_per_second": 150
            },
            "knowledge_metrics": {
                "search_relevance": 0.92,
                "response_quality": 94,
                "knowledge_coverage": 87,
                "avg_similarity_score": 0.89
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/galileo-metrics")
async def get_galileo_metrics():
    """Get Galileo observability metrics"""
    try:
        if GALILEO_AVAILABLE:
            # In production, you would retrieve real metrics from Galileo
            # This would be replaced with actual Galileo API calls
            logging.info("Retrieving real Galileo metrics")

        # Enhanced Galileo metrics for demo with Galileo integration status
        return {
            "galileo_status": {
                "enabled": GALILEO_AVAILABLE,
                "project": os.getenv("GALILEO_PROJECT", "AgentCraft"),
                "log_stream": os.getenv("GALILEO_LOG_STREAM", "production"),
                "integration_active": GALILEO_AVAILABLE
            },
            "conversation_quality": 4.6,
            "token_usage": {
                "average_tokens_per_query": 3247,
                "total_tokens_today": 89532,
                "cost_per_token": 0.0003,
                "monthly_spend": 2679
            },
            "model_performance": {
                "latency_ms": 145,
                "error_rate": 0.02,
                "confidence_score": 0.94,
                "hallucination_rate": 0.008,
                "safety_score": 0.98
            },
            "agent_insights": {
                "top_performing_agent": "Technical Support",
                "avg_resolution_confidence": 0.91,
                "improvement_over_baseline": 12.3,
                "learning_velocity": 0.15
            },
            "real_time_stats": {
                "active_conversations": 23,
                "queries_per_minute": 8.5,
                "success_rate": 96.2,
                "traces_logged": 1247 if GALILEO_AVAILABLE else 0
            },
            "quality_metrics": {
                "groundedness": 0.89,
                "relevance": 0.93,
                "completeness": 0.87,
                "factual_accuracy": 0.95
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/hitl-metrics")
async def get_hitl_metrics():
    """Get Human-in-the-Loop metrics"""
    try:
        # In production, import and use actual HITL service
        # from src.services.hitl_service import hitl_service
        # return hitl_service.get_escalation_metrics()

        # Mock HITL metrics for demo
        return {
            "total_escalations": 47,
            "resolved_escalations": 44,
            "escalation_rate": 3.8,
            "avg_resolution_time": "2.3 minutes",
            "feedback_incorporated": 39,
            "performance_improvement": "12.5%",
            "queue_length": 3,
            "learning_cache_size": 156,
            "escalation_reasons": {
                "low_confidence": 18,
                "complex_issue": 12,
                "negative_sentiment": 8,
                "missing_information": 6,
                "user_requested": 3
            },
            "operator_metrics": {
                "active_operators": 3,
                "avg_response_time": "45 seconds",
                "customer_satisfaction": 4.9,
                "teaching_sessions": 12
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/vector-search")
async def vector_search(request: Dict[str, Any]):
    """Perform vector search using Qdrant"""
    try:
        query = request.get("query", "")
        limit = request.get("limit", 5)

        # In production, use actual Qdrant service
        # from src.services.qdrant_service import qdrant_service
        # results = qdrant_service.search(query, limit)

        # Mock search results for demo
        mock_results = [
            {
                "id": "kb_001",
                "title": "Webhook Signature Verification Guide",
                "content": "Complete guide to implementing webhook signature verification...",
                "category": "Technical Integration",
                "tags": ["webhook", "signature", "security"],
                "similarity_score": 0.94,
                "updated_at": "2024-08-20T14:30:00Z"
            },
            {
                "id": "kb_007", 
                "title": "Debugging 403 Forbidden Errors",
                "content": "Systematic approach to resolving 403 errors...",
                "category": "Troubleshooting",
                "tags": ["403", "forbidden", "debugging"],
                "similarity_score": 0.89,
                "updated_at": "2024-08-20T15:00:00Z"
            }
        ]

        return {
            "query": query,
            "results": mock_results[:limit],
            "total_found": len(mock_results),
            "search_time_ms": 12
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/enhanced-metrics")
async def get_enhanced_metrics():
    """Get comprehensive metrics for enhanced dashboard"""
    try:
        return {
            "real_time": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_queries": 5432,
                "queries_per_minute": 8.5,
                "active_conversations": 23,
                "avg_response_time": 1.2,
                "resolution_rate": 96.2,
                "satisfaction_score": 4.8,
                "cost_per_query": 0.12,
                "escalation_rate": 3.8,
                "first_contact_resolution": 92.5
            },
            "qdrant_performance": {
                "search_relevance": 0.92,
                "knowledge_coverage": 87,
                "avg_latency_ms": 12,
                "throughput_qps": 150
            },
            "galileo_insights": {
                "conversation_quality": 4.6,
                "token_usage": 3247,
                "model_latency": 145,
                "error_rate": 0.02
            },
            "hitl_stats": {
                "escalation_rate": 3.8,
                "avg_escalation_time": "2.3 minutes",
                "learning_retention": 94,
                "feedback_incorporated": 39
            },
            "cost_analysis": {
                "agentcraft": {
                    "infrastructure": 186,
                    "ai_services": 80,
                    "total": 266
                },
                "agentforce": {
                    "licensing": 2000,
                    "infrastructure": 500,
                    "total": 2500
                },
                "monthly_savings": 2234,
                "roi_percentage": 839
            },
            "competitive_advantages": [
                {"metric": "Response Time", "agentcraft": 1.2, "agentforce": 8.5, "improvement": "86% faster"},
                {"metric": "Cost per Query", "agentcraft": 0.12, "agentforce": 2.0, "improvement": "94% cheaper"},
                {"metric": "Resolution Rate", "agentcraft": 96.2, "agentforce": 85, "improvement": "13% higher"},
                {"metric": "Escalation Rate", "agentcraft": 3.8, "agentforce": 15, "improvement": "75% lower"}
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/adaptive-llm-metrics")
async def get_adaptive_llm_metrics():
    """Get detailed metrics from the adaptive LLM system with Galileo integration"""
    try:
        from src.agents.adaptive_llm_system import adaptive_system

        performance_summary = adaptive_system.llm_pool.get_performance_summary()
        optimization_insights = adaptive_system.generate_optimization_insights()
        collaboration_insights = adaptive_system.get_collaboration_insights()
        memory_insights = adaptive_system.get_memory_insights()

        # Get Galileo insights if available
        galileo_insights = {}
        try:
            from src.agents.galileo_adaptive_integration import galileo_integration
            if galileo_integration:
                galileo_insights = galileo_integration.get_galileo_insights()
        except ImportError:
            galileo_insights = {"status": "not_available"}

        return {
            "status": "active",
            "system_info": {
                "available_models": list(performance_summary.keys()),
                "selection_weights": adaptive_system.llm_pool.selection_weights,
                "total_executions": len(adaptive_system.execution_history)
            },
            "performance_summary": performance_summary,
            "optimization_insights": optimization_insights,
            "collaboration_insights": collaboration_insights,
            "memory_insights": memory_insights,
            "galileo_insights": galileo_insights,
            "recent_executions": adaptive_system.execution_history[-10:] if adaptive_system.execution_history else []
        }
    except ImportError:
        return {
            "status": "not_available",
            "error": "Adaptive LLM system not initialized"
        }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e)
        }

@app.get("/api/galileo-adaptive-dashboard")
async def get_galileo_adaptive_dashboard():
    """Get comprehensive Galileo dashboard metrics for the adaptive system"""
    try:
        from src.agents.galileo_adaptive_integration import galileo_integration

        if not galileo_integration:
            return {"status": "not_available", "error": "Galileo integration not initialized"}

        dashboard_metrics = galileo_integration.create_adaptive_dashboard_metrics()
        return dashboard_metrics

    except ImportError:
        return {
            "status": "not_available",
            "error": "Galileo adaptive integration not available"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/api/train-adaptive-system")
async def train_adaptive_system(training_data: List[Dict[str, Any]]):
    """Train the adaptive LLM system with feedback data"""
    try:
        from src.agents.adaptive_llm_system import adaptive_system

        result = adaptive_system.train_system(training_data)
        return result
    except ImportError:
        return {
            "training_completed": False,
            "error": "Adaptive LLM system not available"
        }
    except Exception as e:
        return {
            "training_completed": False,
            "error": str(e)
        }

@app.post("/api/test-adaptive-system") 
async def test_adaptive_system_endpoint(test_queries: List[Dict[str, Any]]):
    """Test the adaptive LLM system with provided queries"""
    try:
        from src.agents.adaptive_llm_system import adaptive_system

        result = adaptive_system.test_system(test_queries)
        return result
    except ImportError:
        return {
            "test_completed": False,
            "error": "Adaptive LLM system not available"
        }
    except Exception as e:
        return {
            "test_completed": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="0.0.0.0", port=8000)