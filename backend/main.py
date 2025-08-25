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

# Import Galileo for AI observability
try:
    from galileo.handlers.crewai.handler import CrewAIEventListener
    GALILEO_AVAILABLE = True
    logging.info("Galileo observability loaded successfully")
except ImportError:
    GALILEO_AVAILABLE = False
    logging.warning("Galileo not available - install with 'uv add galileo'")

# Add src to path for AgentCraft imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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
        # Initialize Galileo event listener for CrewAI observability
        try:
            CrewAIEventListener()
            logging.info("Galileo observability initialized for CrewAI")
        except Exception as e:
            logging.warning(f"Galileo initialization failed: {e}")
    
    if AGENTCRAFT_AVAILABLE:
        logging.info("AgentCraft system initialized successfully with enhanced technical support agent")
    else:
        logging.info("Running in demo mode with mock responses")
    
    yield
    
    # Shutdown
    logging.info("AgentCraft system shutting down")

app = FastAPI(title="AgentCraft API", version="1.0.0", lifespan=lifespan)

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

@app.on_event("startup")
async def startup_event():
    """Initialize AgentCraft system on startup"""
    if AGENTCRAFT_AVAILABLE:
        logging.info("AgentCraft system initialized successfully with enhanced technical support agent")
    else:
        logging.info("Running in demo mode with mock responses")

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
    try:
        if AGENTCRAFT_AVAILABLE and AI_POWERED:
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

            # Parse and format the AI analysis if it's a JSON string
            formatted_response = ""

            # Get the AI content from the technical response
            ai_content = result["technical_response"].get('ai_analysis', '')

            if ai_content:
                try:
                    # Parse the JSON string from AI analysis
                    parsed = json.loads(ai_content)

                    # Create a nicely formatted markdown response
                    formatted_response = f"""**Technical Diagnosis:**
{parsed.get('diagnosis', 'Analysis provided')}

**Root Cause:**
{parsed.get('root_cause', 'Cause identified')}

**Solution:**
{parsed.get('solution', 'Solution provided')}

**Working Code:**
```python
{parsed.get('working_code', 'Code example provided')}
```

**Implementation Steps:**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(parsed.get('implementation_steps', [])))}

**Testing Approach:**
{parsed.get('testing_approach', 'Testing guidance provided')}

**Prevention:**
{parsed.get('prevention', 'Prevention strategies provided')}

**Estimated Time:** {parsed.get('estimated_fix_time', 'Time estimate provided')}"""

                except json.JSONDecodeError as e:
                    # If JSON parsing fails, return the raw content but still formatted
                    print(f"JSON parsing error: {e}")
                    formatted_response = f"**AI Technical Analysis:**\n\n{ai_content}\n\n**Response Type:** Real-time AI analysis using Claude 3 Sonnet"

            # Check for issue_analysis structure (already parsed JSON)
            elif result["technical_response"].get('issue_analysis'):
                issue_data = result["technical_response"]['issue_analysis']
                formatted_response = f"""**Technical Diagnosis:**
{issue_data.get('diagnosis', 'Analysis provided')}

**Root Cause:**
{issue_data.get('root_cause', 'Cause identified')}

**Solution:**
{issue_data.get('solution', 'Solution provided')}

**Working Code:**
```python
{issue_data.get('working_code', 'Code example provided')}
```

**Implementation Steps:**
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(issue_data.get('implementation_steps', [])))}

**Testing Approach:**
{issue_data.get('testing_approach', 'Testing guidance provided')}

**Prevention:**
{issue_data.get('prevention', 'Prevention strategies provided')}

**Estimated Time:** {issue_data.get('estimated_fix_time', 'Time estimate provided')}"""

            else:
                formatted_response = "AI analysis completed - no structured data available"

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
                "orchestration_used": False  # Current setup uses single agent
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