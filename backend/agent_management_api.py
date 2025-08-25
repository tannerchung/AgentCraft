"""
Agent Management API Endpoints
FastAPI endpoints for CRUD operations on database agents
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from uuid import UUID

from backend.enhanced_backend import enhanced_backend

# Create router
router = APIRouter(prefix="/api/agents", tags=["agents"])

# Pydantic models for requests
class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(..., min_length=1, max_length=500)
    domain: str = Field(default="custom", max_length=100)
    backstory: Optional[str] = Field(default="", max_length=2000)
    goal: Optional[str] = Field(default="", max_length=1000)
    keywords: List[str] = Field(default=[])
    avatar: str = Field(default="🤖", max_length=10)
    color: str = Field(default="blue", max_length=50)
    llm_config: Dict[str, Any] = Field(default={"model": "claude-3-5-sonnet", "temperature": 0.2})
    tools: List[str] = Field(default=[])
    specialization_score: float = Field(default=0.0, ge=0.0, le=1.0)

class AgentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = Field(None, min_length=1, max_length=500)
    domain: Optional[str] = Field(None, max_length=100)
    backstory: Optional[str] = Field(None, max_length=2000)
    goal: Optional[str] = Field(None, max_length=1000)
    keywords: Optional[List[str]] = None
    avatar: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = Field(None, max_length=50)
    llm_config: Optional[Dict[str, Any]] = None
    tools: Optional[List[str]] = None
    specialization_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None

class FeedbackRequest(BaseModel):
    session_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(default="", max_length=1000)

# Dependency to ensure backend is initialized
async def get_enhanced_backend():
    """Dependency to get initialized enhanced backend"""
    if not enhanced_backend.initialized:
        await enhanced_backend.initialize()
    return enhanced_backend

@router.get("/list")
async def list_agents(backend = Depends(get_enhanced_backend)):
    """Get list of all agents"""
    try:
        result = await backend.get_agent_library()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
async def create_agent(agent_data: AgentCreateRequest, 
                      backend = Depends(get_enhanced_backend)):
    """Create a new agent"""
    try:
        result = await backend.create_agent(agent_data.dict())
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create agent"))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{agent_id}")
async def update_agent(agent_id: str, updates: AgentUpdateRequest,
                      backend = Depends(get_enhanced_backend)):
    """Update an existing agent"""
    try:
        # Convert UUID string
        UUID(agent_id)  # Validate UUID format
        
        # Filter out None values
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        result = await backend.update_agent(agent_id, update_data)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to update agent"))
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, backend = Depends(get_enhanced_backend)):
    """Delete (deactivate) an agent"""
    try:
        # Validate UUID format
        UUID(agent_id)
        
        result = await backend.delete_agent(agent_id)
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to delete agent"))
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def record_feedback(feedback: FeedbackRequest,
                         backend = Depends(get_enhanced_backend)):
    """Record user feedback for a conversation session"""
    try:
        # Validate session ID format
        UUID(feedback.session_id)
        
        result = await backend.record_user_feedback(
            feedback.session_id, 
            feedback.rating, 
            feedback.comment
        )
        
        return result
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_system_metrics(backend = Depends(get_enhanced_backend)):
    """Get comprehensive system metrics"""
    try:
        result = await backend.get_system_metrics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/refresh")
async def refresh_cache(backend = Depends(get_enhanced_backend)):
    """Manually refresh agent cache"""
    try:
        result = await backend.refresh_agent_cache()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/reload")
async def hot_reload_agent(agent_id: str, backend = Depends(get_enhanced_backend)):
    """Hot reload a specific agent"""
    try:
        # Validate UUID format
        UUID(agent_id)
        
        result = await backend.hot_reload_agent(agent_id)
        return result
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_agent_status(backend = Depends(get_enhanced_backend)):
    """Get agent system status"""
    try:
        from src.agents.crew_db_integration import crew_agent_pool
        
        cache_stats = crew_agent_pool.get_cache_stats()
        agents = await crew_agent_pool.get_all_agents()
        
        return {
            "success": True,
            "total_agents": len(agents),
            "cache_stats": cache_stats,
            "agents_by_domain": _group_agents_by_domain(agents),
            "database_connected": True,
            "memory_cached": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _group_agents_by_domain(agents: Dict) -> Dict:
    """Helper function to group agents by domain"""
    domains = {}
    for agent in agents.values():
        domain = agent.domain
        if domain not in domains:
            domains[domain] = []
        
        domains[domain].append({
            "name": agent.name,
            "id": str(agent.id),
            "specialization_score": agent.specialization_score,
            "collaboration_rating": agent.collaboration_rating
        })
    
    return domains

# Example usage endpoints for testing
@router.get("/examples/create-technical-agent")
async def example_create_technical_agent():
    """Example of how to create a technical agent"""
    return {
        "example_request": {
            "name": "Custom Security Analyst",
            "role": "Advanced cybersecurity analysis and threat detection",
            "domain": "security",
            "backstory": "You are an expert cybersecurity analyst with years of experience in threat detection, vulnerability assessment, and incident response.",
            "goal": "Identify security threats, analyze vulnerabilities, and provide actionable security recommendations",
            "keywords": ["security", "vulnerability", "threat", "malware", "breach", "compliance", "audit"],
            "avatar": "🔒",
            "color": "red",
            "llm_config": {
                "model": "claude-3-5-sonnet",
                "temperature": 0.1
            },
            "specialization_score": 0.9
        },
        "endpoint": "POST /api/agents/create"
    }

@router.get("/examples/update-agent")
async def example_update_agent():
    """Example of how to update an agent"""
    return {
        "example_request": {
            "role": "Enhanced cybersecurity analysis with AI-powered threat detection",
            "keywords": ["security", "ai", "machine-learning", "threat-detection"],
            "specialization_score": 0.95,
            "llm_config": {
                "model": "gpt-4",
                "temperature": 0.05
            }
        },
        "endpoint": "PUT /api/agents/{agent_id}"
    }