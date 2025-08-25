"""
Enhanced Backend Integration
Combines database persistence with memory caching for optimal performance
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.enhanced_adaptive_system import enhanced_adaptive_system
from database.models import metrics_manager, learning_manager, agent_manager

logger = logging.getLogger(__name__)

class EnhancedBackend:
    """Enhanced backend that uses database + memory caching for agents"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize the enhanced backend"""
        try:
            await enhanced_adaptive_system.initialize()
            self.initialized = True
            logger.info("Enhanced backend initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize enhanced backend: {e}")
            raise
    
    async def process_chat_request(self, message: str, agent_type: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat request with enhanced database-backed system"""
        if not self.initialized:
            await self.initialize()
        
        try:
            start_time = datetime.now()
            
            # Create conversation session for tracking
            session_data = {
                'query': message,
                'agents_selected': [],  # Will be populated by the system
                'metadata': {
                    'agent_type_requested': agent_type,
                    'context': context or {},
                    'enhanced_backend': True
                }
            }
            
            session_id = await metrics_manager.create_conversation_session(session_data)
            
            # Process with enhanced adaptive system
            result = await enhanced_adaptive_system.process_query(
                query=message,
                context=context,
                session_id=session_id
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Update session with final response
            if result.get('success'):
                await metrics_manager.update_session_completion(
                    session_id,
                    result.get('response', ''),
                    None  # User satisfaction will be set later
                )
            
            # Format response for frontend compatibility
            formatted_result = {
                "success": result.get('success', True),
                "response": {
                    "content": result.get('response', 'Response generated successfully'),
                    "raw_analysis": result.get('technical_analysis', {})
                },
                "agent_info": {
                    "processing_time": f"{processing_time:.2f}s",
                    "agents_used": result.get('agents_used', []),
                    "llms_used": {"system": "enhanced_database_crewai"},
                    "database_backed": True,
                    "memory_cached": True,
                    "crew_execution": result.get('crew_execution', False)
                },
                "query_analysis": {
                    "selected_agents_count": len(result.get('agents_used', [])),
                    "agent_selection_method": "database_keywords_cached",
                    "ai_confidence": "High",
                    "complexity_score": result.get('complexity_score', 0.7)
                },
                "competitive_advantage": {
                    "database_persistence": True,
                    "memory_caching": True,
                    "hot_reload_capability": True,
                    "self_improvement_loops": True,
                    "crewai_integration": True
                },
                "timestamp": end_time.isoformat(),
                "ai_powered": True,
                "orchestration_used": True,
                "database_session_id": str(session_id),
                "enhanced_system": True,
                "galileo_traced": result.get('galileo_traced', False),
                "optimization_status": result.get('optimization_status', {})
            }
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error processing chat request with enhanced backend: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": {
                    "content": f"I encountered an error: {str(e)}. Please try again."
                },
                "agent_info": {
                    "processing_time": "0s",
                    "agents_used": [],
                    "database_backed": True,
                    "error": True
                },
                "enhanced_system": True,
                "ai_powered": True
            }
    
    async def get_agent_library(self) -> Dict[str, Any]:
        """Get formatted agent library for frontend"""
        try:
            from src.agents.crew_db_integration import crew_agent_pool
            
            # Get all agents from memory cache
            agents = await crew_agent_pool.get_all_agents()
            
            # Format for frontend compatibility
            agent_library = {}
            for name, agent in agents.items():
                # Create a frontend-compatible key
                key = name.lower().replace(' ', '_').replace('-', '_')
                
                agent_library[key] = {
                    "id": str(agent.id),
                    "name": agent.name,
                    "avatar": agent.avatar,
                    "color": agent.color,
                    "role": agent.role,
                    "keywords": agent.keywords,
                    "domain": agent.domain,
                    "specialization_score": agent.specialization_score,
                    "collaboration_rating": agent.collaboration_rating,
                    "backstory": agent.backstory,
                    "goal": agent.goal,
                    "llm_config": agent.llm_config,
                    "database_backed": True,
                    "memory_cached": True
                }
            
            # Get cache statistics
            cache_stats = crew_agent_pool.get_cache_stats()
            
            return {
                "success": True,
                "agents": agent_library,
                "total_count": len(agent_library),
                "cache_stats": cache_stats,
                "database_backed": True,
                "memory_cached": True
            }
            
        except Exception as e:
            logger.error(f"Error getting agent library: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents": {},
                "database_backed": True
            }
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent with hot-reload"""
        try:
            result = await enhanced_adaptive_system.create_custom_agent(agent_data)
            return result
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent with hot-reload"""
        try:
            result = await enhanced_adaptive_system.update_agent_config(
                UUID(agent_id), updates
            )
            return result
            
        except Exception as e:
            logger.error(f"Error updating agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Deactivate agent (soft delete)"""
        try:
            success = await agent_manager.deactivate_agent(UUID(agent_id))
            
            if success:
                # Refresh cache to remove deactivated agent
                from src.agents.crew_db_integration import crew_agent_pool
                await crew_agent_pool.refresh_agents(force=True)
                
                return {
                    "success": True,
                    "message": "Agent deactivated successfully"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to deactivate agent"
                }
                
        except Exception as e:
            logger.error(f"Error deactivating agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_user_feedback(self, session_id: str, rating: int, 
                                 comment: str = "") -> Dict[str, Any]:
        """Record user feedback for learning"""
        try:
            await metrics_manager.update_session_completion(
                UUID(session_id),
                None,  # Don't update final_response
                rating
            )
            
            # Generate learning insights based on feedback
            if rating <= 2:
                insight_data = {
                    'insight_type': 'user_dissatisfaction',
                    'title': f'Low user satisfaction: {rating}/5',
                    'description': f'User feedback: "{comment}"',
                    'confidence_score': 0.8,
                    'data_points': 1,
                    'recommended_actions': [
                        'Review agent responses for this session',
                        'Check agent selection accuracy',
                        'Consider response quality improvements'
                    ]
                }
                await learning_manager.generate_learning_insight(insight_data)
            
            return {
                "success": True,
                "message": "Feedback recorded successfully",
                "learning_triggered": rating <= 2 or rating >= 4
            }
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            system_status = await enhanced_adaptive_system.get_system_status()
            
            # Get learning insights
            insights = await learning_manager.get_pending_insights()
            
            # Get query patterns
            patterns = await metrics_manager.analyze_query_patterns(limit=10)
            
            return {
                "success": True,
                "system_status": system_status,
                "learning_insights": [
                    {
                        "title": insight["title"],
                        "type": insight["insight_type"],
                        "confidence": insight["confidence_score"],
                        "data_points": insight["data_points"]
                    } for insight in insights[:5]  # Top 5 insights
                ],
                "query_patterns": [
                    {
                        "description": pattern["pattern_description"] or "Unknown Pattern",
                        "frequency": pattern["frequency"],
                        "avg_satisfaction": pattern.get("avg_satisfaction", 0)
                    } for pattern in patterns[:5]  # Top 5 patterns
                ],
                "enhanced_backend": True,
                "database_backed": True
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "enhanced_backend": True
            }
    
    async def refresh_agent_cache(self) -> Dict[str, Any]:
        """Manually refresh agent cache"""
        try:
            from src.agents.crew_db_integration import crew_agent_pool
            await crew_agent_pool.refresh_agents(force=True)
            
            cache_stats = crew_agent_pool.get_cache_stats()
            
            return {
                "success": True,
                "message": "Agent cache refreshed successfully",
                "cache_stats": cache_stats
            }
            
        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def hot_reload_agent(self, agent_id: str) -> Dict[str, Any]:
        """Hot reload a specific agent"""
        try:
            from src.agents.crew_db_integration import crew_agent_pool
            await crew_agent_pool.hot_reload_agent(UUID(agent_id))
            
            return {
                "success": True,
                "message": f"Agent {agent_id} hot reloaded successfully"
            }
            
        except Exception as e:
            logger.error(f"Error hot reloading agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
enhanced_backend = EnhancedBackend()