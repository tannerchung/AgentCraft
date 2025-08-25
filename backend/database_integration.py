"""
Database integration for FastAPI backend
Replaces static agent handling with database-backed agent management
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.database_agent_manager import database_agent_manager

logger = logging.getLogger(__name__)

class BackendDatabaseIntegration:
    """Integration layer between FastAPI and database agent management"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize database integration"""
        try:
            await database_agent_manager.initialize()
            self.initialized = True
            logger.info("Backend database integration initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database integration: {e}")
            raise
    
    async def process_chat_request(self, message: str, agent_type: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process chat request using database-backed agents"""
        if not self.initialized:
            raise RuntimeError("Database integration not initialized")
        
        try:
            start_time = datetime.now()
            
            # Select optimal agents for the query
            selected_agents = await database_agent_manager.select_agents_for_query(message)
            
            if not selected_agents:
                return {
                    "success": False,
                    "error": "No suitable agents found for query",
                    "response": {
                        "content": "I'm sorry, but I couldn't find appropriate agents to handle your request. Please try rephrasing your question or contact support."
                    }
                }
            
            # Process query with selected agents
            result = await database_agent_manager.process_query_with_agents(
                query=message,
                selected_agents=selected_agents
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Format response for frontend
            formatted_result = {
                "success": True,
                "response": {
                    "content": result.get('response', 'Response generated successfully'),
                    "raw_analysis": result.get('technical_response', {})
                },
                "agent_info": {
                    "processing_time": f"{processing_time:.2f}s",
                    "agents_used": [agent['name'] for agent in selected_agents],
                    "llms_used": result.get('llm_selection', {}),
                    "database_backed": True
                },
                "query_analysis": {
                    "selected_agents_count": len(selected_agents),
                    "agent_selection_method": "database_keywords",
                    "ai_confidence": result.get('quality_score', 'High')
                },
                "competitive_advantage": {
                    "database_persistence": True,
                    "adaptive_learning": True,
                    "metrics_collection": True
                },
                "timestamp": end_time.isoformat(),
                "ai_powered": True,
                "orchestration_used": True,
                "database_session_id": result.get('session_id'),
                "galileo_traced": result.get('galileo_logged', False)
            }
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error processing chat request with database: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": {
                    "content": f"I encountered an error processing your request: {str(e)}. Please try again or contact support if the issue persists."
                },
                "agent_info": {
                    "processing_time": "0s",
                    "agents_used": [],
                    "database_backed": True,
                    "error": True
                },
                "ai_powered": True,
                "orchestration_used": False
            }
    
    async def get_agent_list(self) -> Dict[str, Any]:
        """Get list of all available agents from database"""
        try:
            agents = await database_agent_manager.get_all_agents()
            
            # Format for frontend compatibility
            agent_library = {}
            for name, agent in agents.items():
                agent_library[name.lower().replace(' ', '_')] = {
                    "id": str(agent['id']),
                    "name": agent['name'],
                    "avatar": agent.get('avatar', '🤖'),
                    "color": agent.get('color', 'blue'),
                    "role": agent['role'],
                    "keywords": agent.get('keywords', []),
                    "domain": agent.get('domain', 'general'),
                    "specialization_score": agent.get('specialization_score', 0.0),
                    "collaboration_rating": agent.get('collaboration_rating', 0.0),
                    "is_active": agent.get('is_active', True)
                }
            
            return {
                "success": True,
                "agents": agent_library,
                "total_count": len(agent_library),
                "database_backed": True
            }
            
        except Exception as e:
            logger.error(f"Error getting agent list: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents": {},
                "database_backed": True
            }
    
    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent"""
        try:
            agent_id = await database_agent_manager.create_agent(agent_data)
            
            return {
                "success": True,
                "agent_id": str(agent_id),
                "message": f"Agent '{agent_data['name']}' created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing agent"""
        try:
            success = await database_agent_manager.update_agent(UUID(agent_id), updates)
            
            return {
                "success": success,
                "message": f"Agent updated successfully" if success else "Agent update failed"
            }
            
        except Exception as e:
            logger.error(f"Error updating agent: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def record_user_feedback(self, session_id: str, rating: int, 
                                 comment: str = "") -> Dict[str, Any]:
        """Record user feedback for learning"""
        try:
            await database_agent_manager.record_user_feedback(
                UUID(session_id), rating, comment
            )
            
            return {
                "success": True,
                "message": "Feedback recorded successfully"
            }
            
        except Exception as e:
            logger.error(f"Error recording user feedback: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            summary = await database_agent_manager.get_performance_summary()
            
            return {
                "success": True,
                "metrics": summary,
                "database_backed": True
            }
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                "success": False,
                "error": str(e),
                "database_backed": True
            }
    
    async def close(self):
        """Close database connections"""
        if self.initialized:
            await database_agent_manager.close()
            self.initialized = False
            logger.info("Database integration closed")

# Global instance
backend_db_integration = BackendDatabaseIntegration()