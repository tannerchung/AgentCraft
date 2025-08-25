"""
Efficiency API Endpoints
Additional endpoints to make AgentCraft more efficient and usable
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
import asyncio
import logging
from datetime import datetime, timedelta

from backend.enhanced_backend import enhanced_backend
from src.agents.realtime_agent_tracker import realtime_tracker
from database.models import learning_manager, agent_manager

router = APIRouter(tags=["efficiency"])
logger = logging.getLogger(__name__)

# Pydantic models
class BulkChatRequest(BaseModel):
    messages: List[str] = Field(..., min_items=1, max_items=10)
    agent_type: str = Field(default="multi-agent")
    context: Optional[Dict[str, Any]] = Field(default={})
    priority: Optional[str] = Field(default="normal")  # low, normal, high

class ChatTemplate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    template: str = Field(..., min_length=1, max_length=2000)
    variables: List[str] = Field(default=[])
    category: str = Field(default="general")
    description: Optional[str] = Field(default="")

class AgentPreset(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    agent_ids: List[str] = Field(..., min_items=1)
    use_case: str = Field(default="general")
    priority_order: List[int] = Field(default=[])

class SystemOptimization(BaseModel):
    optimization_type: str = Field(..., pattern="^(cache|performance|learning|agents)$")
    parameters: Dict[str, Any] = Field(default={})

# Dependency to ensure backend is initialized
async def get_enhanced_backend():
    if not enhanced_backend.initialized:
        await enhanced_backend.initialize()
    return enhanced_backend

@router.post("/bulk-chat")
async def bulk_chat_processing(
    request: BulkChatRequest,
    background_tasks: BackgroundTasks,
    backend = Depends(get_enhanced_backend)
):
    """Process multiple chat messages efficiently"""
    try:
        results = []
        session_ids = []
        
        # Process messages in parallel for better efficiency
        async def process_message(message: str, index: int):
            try:
                result = await backend.process_chat_request(
                    message=message,
                    agent_type=request.agent_type,
                    context={
                        **request.context,
                        "bulk_request": True,
                        "bulk_index": index,
                        "priority": request.priority
                    }
                )
                return {"index": index, "message": message, "result": result}
            except Exception as e:
                logger.error(f"Error processing bulk message {index}: {e}")
                return {
                    "index": index, 
                    "message": message, 
                    "result": {"success": False, "error": str(e)}
                }
        
        # Execute in parallel with concurrency limit
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests
        
        async def limited_process(message: str, index: int):
            async with semaphore:
                return await process_message(message, index)
        
        tasks = [
            limited_process(msg, i) 
            for i, msg in enumerate(request.messages)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Sort results by index to maintain order
        results.sort(key=lambda x: x["index"])
        
        # Extract session IDs for tracking
        session_ids = [
            r["result"].get("database_session_id") 
            for r in results 
            if r["result"].get("success") and r["result"].get("database_session_id")
        ]
        
        return {
            "success": True,
            "processed_count": len(results),
            "results": results,
            "session_ids": session_ids,
            "bulk_processing": True
        }
        
    except Exception as e:
        logger.error(f"Bulk chat processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_chat_templates():
    """Get predefined chat templates for common queries"""
    templates = [
        {
            "name": "webhook_troubleshooting",
            "template": "I'm having issues with webhook {webhook_url}. The error is: {error_message}. Can you help diagnose the problem?",
            "variables": ["webhook_url", "error_message"],
            "category": "technical",
            "description": "Template for webhook integration issues"
        },
        {
            "name": "billing_inquiry", 
            "template": "I have a question about my billing for {service_name}. The issue is: {issue_description}. My account ID is {account_id}.",
            "variables": ["service_name", "issue_description", "account_id"],
            "category": "billing",
            "description": "Template for billing-related inquiries"
        },
        {
            "name": "security_audit",
            "template": "I need a security audit for {system_component}. Please check for vulnerabilities in {specific_areas}. Priority level: {priority}.",
            "variables": ["system_component", "specific_areas", "priority"],
            "category": "security", 
            "description": "Template for security audit requests"
        },
        {
            "name": "performance_optimization",
            "template": "Our {system_type} is experiencing performance issues. Response time is {current_time} but should be {target_time}. Database queries: {query_info}.",
            "variables": ["system_type", "current_time", "target_time", "query_info"],
            "category": "performance",
            "description": "Template for performance optimization requests"
        },
        {
            "name": "competitive_analysis",
            "template": "I need a competitive analysis comparing our {product_feature} against {competitor_name}. Focus on: {analysis_areas}.",
            "variables": ["product_feature", "competitor_name", "analysis_areas"], 
            "category": "analysis",
            "description": "Template for competitive intelligence requests"
        }
    ]
    
    return {
        "success": True,
        "templates": templates,
        "total_count": len(templates)
    }

@router.post("/templates/{template_name}/generate")
async def generate_from_template(
    template_name: str,
    variables: Dict[str, str],
    backend = Depends(get_enhanced_backend)
):
    """Generate and process a message from a template"""
    try:
        # Get templates
        templates_response = await get_chat_templates()
        templates = {t["name"]: t for t in templates_response["templates"]}
        
        if template_name not in templates:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template = templates[template_name]
        
        # Validate required variables
        missing_vars = [var for var in template["variables"] if var not in variables]
        if missing_vars:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required variables: {missing_vars}"
            )
        
        # Generate message from template
        message = template["template"].format(**variables)
        
        # Process the generated message
        result = await backend.process_chat_request(
            message=message,
            agent_type="multi-agent",
            context={
                "template_used": template_name,
                "template_variables": variables,
                "category": template["category"]
            }
        )
        
        return {
            "success": True,
            "template_name": template_name,
            "generated_message": message,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-presets")
async def get_agent_presets(backend = Depends(get_enhanced_backend)):
    """Get predefined agent combinations for specific use cases"""
    try:
        # Get current agents
        agents_response = await backend.get_agent_library()
        if not agents_response.get("success"):
            raise HTTPException(status_code=500, detail="Failed to get agents")
        
        agents = agents_response["agents"]
        
        # Create smart presets based on available agents
        presets = []
        
        # Technical Support Preset
        tech_agents = [
            agent_id for agent_id, agent in agents.items()
            if agent["domain"] in ["technical", "security", "database"]
        ]
        if tech_agents:
            presets.append({
                "name": "technical_support",
                "description": "Best agents for technical troubleshooting and integration issues",
                "agent_ids": tech_agents[:3],  # Top 3
                "use_case": "API issues, webhook problems, integration troubleshooting",
                "priority_order": [0, 1, 2]  # Orchestrator first, then specialists
            })
        
        # Business Operations Preset
        business_agents = [
            agent_id for agent_id, agent in agents.items()
            if agent["domain"] in ["business", "legal", "billing"]
        ]
        if business_agents:
            presets.append({
                "name": "business_operations",
                "description": "Agents specialized in business processes and compliance",
                "agent_ids": business_agents[:3],
                "use_case": "Billing issues, legal compliance, business process optimization",
                "priority_order": [0, 1, 2]
            })
        
        # Analysis & Intelligence Preset
        analysis_agents = [
            agent_id for agent_id, agent in agents.items()
            if agent["domain"] in ["analysis", "competitive", "marketing"]
        ]
        if analysis_agents:
            presets.append({
                "name": "analysis_intelligence", 
                "description": "Agents for market analysis and competitive intelligence",
                "agent_ids": analysis_agents[:3],
                "use_case": "Competitive analysis, market research, data insights",
                "priority_order": [0, 1, 2]
            })
        
        return {
            "success": True,
            "presets": presets,
            "total_presets": len(presets)
        }
        
    except Exception as e:
        logger.error(f"Error getting agent presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-insights")
async def get_performance_insights(
    days: int = Query(default=7, ge=1, le=90),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get performance insights and optimization recommendations"""
    try:
        # Get system metrics
        backend_metrics = await enhanced_backend.get_system_metrics()
        
        # Get query patterns
        patterns = await agent_manager.analyze_query_patterns(limit)
        
        # Get learning insights
        insights = await learning_manager.get_pending_insights()
        
        # Calculate performance scores
        performance_score = 85.0  # Base score
        
        if backend_metrics.get("success"):
            system_status = backend_metrics["system_status"]
            if system_status.get("system_healthy"):
                performance_score += 5.0
            
            cache_stats = system_status.get("cache_performance", {})
            if cache_stats.get("total_agents", 0) > 0:
                performance_score += 5.0
        
        # Generate recommendations
        recommendations = []
        
        if len(insights) > 5:
            recommendations.append({
                "type": "learning",
                "priority": "high",
                "title": "Review Learning Insights",
                "description": f"You have {len(insights)} pending insights that could improve system performance"
            })
        
        if patterns:
            top_pattern = patterns[0]
            if top_pattern.get("avg_satisfaction", 0) < 4.0:
                recommendations.append({
                    "type": "optimization",
                    "priority": "medium", 
                    "title": "Optimize Common Query Pattern",
                    "description": f"Pattern '{top_pattern.get('pattern_description', 'Unknown')}' has low satisfaction ({top_pattern.get('avg_satisfaction', 0):.1f}/5)"
                })
        
        return {
            "success": True,
            "performance_score": performance_score,
            "time_period_days": days,
            "insights": {
                "query_patterns": patterns[:5],
                "learning_insights": [
                    {
                        "title": insight["title"],
                        "type": insight["insight_type"],
                        "confidence": insight["confidence_score"],
                        "data_points": insight["data_points"]
                    } for insight in insights[:5]
                ],
                "recommendations": recommendations
            },
            "system_health": backend_metrics.get("system_status", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize")
async def optimize_system(
    optimization: SystemOptimization,
    background_tasks: BackgroundTasks,
    backend = Depends(get_enhanced_backend)
):
    """Trigger system optimization tasks"""
    try:
        optimization_results = {}
        
        if optimization.optimization_type == "cache":
            # Refresh agent cache
            cache_result = await backend.refresh_agent_cache()
            optimization_results["cache_refresh"] = cache_result
            
        elif optimization.optimization_type == "performance":
            # Performance optimization
            background_tasks.add_task(run_performance_optimization)
            optimization_results["performance"] = {"status": "scheduled"}
            
        elif optimization.optimization_type == "learning":
            # Generate learning insights
            background_tasks.add_task(run_learning_optimization)
            optimization_results["learning"] = {"status": "scheduled"}
            
        elif optimization.optimization_type == "agents":
            # Agent optimization
            background_tasks.add_task(run_agent_optimization)
            optimization_results["agents"] = {"status": "scheduled"}
        
        return {
            "success": True,
            "optimization_type": optimization.optimization_type,
            "results": optimization_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"System optimization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage-statistics")
async def get_usage_statistics(
    days: int = Query(default=7, ge=1, le=90)
):
    """Get comprehensive usage statistics"""
    try:
        # This would normally query the database for real statistics
        # For now, return mock data based on the structure we have
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Mock statistics - in real implementation, query from database
        stats = {
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "conversation_stats": {
                "total_conversations": 156,
                "successful_conversations": 142,
                "success_rate": 91.0,
                "avg_response_time": "2.3s",
                "avg_user_satisfaction": 4.2
            },
            "agent_usage": {
                "most_used_agent": "Technical Integration Specialist", 
                "avg_agents_per_query": 2.1,
                "collaboration_rate": 68.0
            },
            "performance_metrics": {
                "cache_hit_rate": 89.5,
                "database_response_time": "45ms",
                "memory_efficiency": 92.3
            },
            "learning_metrics": {
                "insights_generated": 23,
                "insights_implemented": 18,
                "improvement_rate": 78.3
            }
        }
        
        return {
            "success": True,
            "statistics": stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting usage statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-check")
async def comprehensive_health_check(backend = Depends(get_enhanced_backend)):
    """Comprehensive system health check"""
    try:
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Database check
        try:
            from database.models import db_manager
            health_status["checks"]["database"] = {
                "status": "healthy" if db_manager.pool else "disconnected",
                "pool_size": len(db_manager.pool._holders) if db_manager.pool else 0
            }
        except Exception as e:
            health_status["checks"]["database"] = {"status": "error", "error": str(e)}
        
        # Agent cache check
        try:
            from src.agents.crew_db_integration import crew_agent_pool
            cache_stats = crew_agent_pool.get_cache_stats()
            health_status["checks"]["agent_cache"] = {
                "status": "healthy" if cache_stats["total_agents"] > 0 else "empty",
                "stats": cache_stats
            }
        except Exception as e:
            health_status["checks"]["agent_cache"] = {"status": "error", "error": str(e)}
        
        # WebSocket check
        try:
            ws_stats = realtime_tracker.get_active_sessions_summary()
            health_status["checks"]["websockets"] = {
                "status": "healthy",
                "active_sessions": ws_stats["total_sessions"]
            }
        except Exception as e:
            health_status["checks"]["websockets"] = {"status": "error", "error": str(e)}
        
        # CrewAI check
        try:
            from src.agents.crewai_callbacks import CREWAI_PATCHED
            health_status["checks"]["crewai"] = {
                "status": "healthy" if CREWAI_PATCHED else "not_patched",
                "patched": CREWAI_PATCHED
            }
        except Exception as e:
            health_status["checks"]["crewai"] = {"status": "error", "error": str(e)}
        
        # Determine overall status
        failed_checks = [
            check for check in health_status["checks"].values() 
            if check.get("status") not in ["healthy", "not_patched"]
        ]
        
        if failed_checks:
            health_status["overall_status"] = "degraded" if len(failed_checks) < 2 else "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "overall_status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Background task functions
async def run_performance_optimization():
    """Background task for performance optimization"""
    try:
        logger.info("Starting performance optimization...")
        
        # Refresh caches
        await enhanced_backend.refresh_agent_cache()
        
        # Could add more optimization tasks here
        
        logger.info("Performance optimization completed")
    except Exception as e:
        logger.error(f"Performance optimization error: {e}")

async def run_learning_optimization():
    """Background task for learning optimization"""
    try:
        logger.info("Starting learning optimization...")
        
        # Generate insights based on recent data
        # This would analyze patterns and generate recommendations
        
        logger.info("Learning optimization completed")
    except Exception as e:
        logger.error(f"Learning optimization error: {e}")

async def run_agent_optimization():
    """Background task for agent optimization"""
    try:
        logger.info("Starting agent optimization...")
        
        # Analyze agent performance and update scores
        # This would update specialization scores based on recent performance
        
        logger.info("Agent optimization completed")
    except Exception as e:
        logger.error(f"Agent optimization error: {e}")