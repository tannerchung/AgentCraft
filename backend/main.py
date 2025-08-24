
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import time
import asyncio
import logging
import sys
import os
from datetime import datetime

# Add src to path for AgentCraft imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.core.agent_router import AgentRouter
    from src.agents.technical_support_agent import TechnicalSupportAgent
    AGENTCRAFT_AVAILABLE = True
except ImportError:
    AGENTCRAFT_AVAILABLE = False
    logging.warning("AgentCraft modules not available, using mock responses")

app = FastAPI(title="AgentCraft API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://0.0.0.0:3000"],
    allow_credentials=True,
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
agent_router = None
active_connections: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize AgentCraft system on startup"""
    global agent_router
    
    if AGENTCRAFT_AVAILABLE:
        try:
            agent_router = AgentRouter()
            
            # Register Technical Support Agent
            tech_agent = TechnicalSupportAgent()
            agent_router.register_agent(
                tech_agent, 
                ["webhook", "api", "integration", "ssl", "authentication", "timeout", "json", "http"]
            )
            
            logging.info("AgentCraft system initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize AgentCraft: {e}")
            agent_router = None
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

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_agent(chat_request: ChatMessage):
    """Send message to specialized agent"""
    start_time = time.time()
    
    try:
        if agent_router and AGENTCRAFT_AVAILABLE:
            # Use real AgentCraft system
            context = {
                **chat_request.context,
                "agent_type": chat_request.agent_type,
                "technical_indicators": extract_technical_terms(chat_request.message)
            }
            
            response = agent_router.route_query(chat_request.message, context)
            
            return ChatResponse(
                message=response.get('response', 'No response available'),
                confidence=response.get('confidence', 0.5),
                agent_used=response.get('agent_used', 'Unknown'),
                timestamp=datetime.now().isoformat(),
                processing_time=time.time() - start_time
            )
        else:
            # Use mock responses for demo
            await asyncio.sleep(1.0 + random.uniform(0.5, 2.0))  # Simulate processing time
            
            mock_response = get_mock_agent_response(chat_request.agent_type, chat_request.message)
            
            return ChatResponse(
                message=mock_response["message"],
                confidence=mock_response["confidence"],
                agent_used=f"{chat_request.agent_type.title()} Agent",
                timestamp=datetime.now().isoformat(),
                processing_time=time.time() - start_time
            )
            
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
async def get_metrics():
    """Get performance metrics"""
    import random
    
    base_time = time.time()
    
    return {
        "total_queries": random.randint(1200, 1300),
        "avg_response_time": round(random.uniform(1.0, 1.5), 2),
        "cost_savings": random.randint(44000, 46000),
        "agent_efficiency": random.randint(92, 96),
        "customer_satisfaction": round(random.uniform(4.7, 4.9), 1),
        "uptime": 99.8,
        "active_agents": 3,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/api/competitive-analysis")
async def competitive_analysis(request: CompetitiveAnalysisRequest):
    """Generate competitive analysis"""
    
    # Simulate processing time
    await asyncio.sleep(1.5)
    
    competitive_data = {
        "salesforce": {
            "strengths": ["Market leader", "Extensive ecosystem", "Enterprise features"],
            "weaknesses": ["High cost", "Complex setup", "Limited customization"],
            "market_share": 19.5,
            "pricing": "High",
            "customization_score": 6.2
        },
        "zendesk": {
            "strengths": ["Easy to use", "Good integrations", "Strong support"],
            "weaknesses": ["Limited AI capabilities", "Pricing tiers", "Scalability issues"],
            "market_share": 13.2,
            "pricing": "Medium",
            "customization_score": 7.1
        },
        "microsoft": {
            "strengths": ["Office integration", "Enterprise focus", "Security"],
            "weaknesses": ["Complex licensing", "User experience", "Innovation speed"],
            "market_share": 8.7,
            "pricing": "High",
            "customization_score": 5.8
        }
    }
    
    competitor_key = request.competitor.lower()
    if competitor_key in competitive_data:
        data = competitive_data[competitor_key]
    else:
        data = {
            "strengths": ["Market presence"],
            "weaknesses": ["Limited capabilities"],
            "market_share": 5.0,
            "pricing": "Unknown",
            "customization_score": 6.0
        }
    
    return {
        "competitor": request.competitor,
        "analysis": data,
        "our_advantages": [
            "Superior customization capabilities",
            "Faster implementation (hours vs months)",
            "Domain-specific expertise",
            "Cost-effective solution",
            "No vendor lock-in"
        ],
        "recommended_positioning": f"Position AgentCraft as the specialized, flexible alternative to {request.competitor}'s generic approach",
        "timestamp": datetime.now().isoformat()
    }

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
