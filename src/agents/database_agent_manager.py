"""
Database-backed agent manager for AgentCraft
Replaces static agent configurations with dynamic database-driven agents
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.models import agent_manager, metrics_manager, learning_manager, db_manager
from src.agents.adaptive_llm_system import AdaptiveLLMSystem

logger = logging.getLogger(__name__)

class DatabaseAgentManager:
    """Manages agents using PostgreSQL database for persistence"""
    
    def __init__(self):
        self.adaptive_llm = AdaptiveLLMSystem()
        self._agents_cache = {}
        self._last_cache_update = None
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    async def initialize(self):
        """Initialize database connections"""
        try:
            await db_manager.initialize()
            await self._refresh_agents_cache()
            logger.info("Database agent manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database agent manager: {e}")
            raise
    
    async def _refresh_agents_cache(self):
        """Refresh the agents cache from database"""
        try:
            agents = await agent_manager.get_all_agents()
            self._agents_cache = {agent['name']: agent for agent in agents}
            self._last_cache_update = asyncio.get_event_loop().time()
            logger.info(f"Refreshed agents cache with {len(agents)} agents")
        except Exception as e:
            logger.error(f"Failed to refresh agents cache: {e}")
            raise
    
    async def get_all_agents(self) -> Dict[str, Dict]:
        """Get all active agents from database (with caching)"""
        current_time = asyncio.get_event_loop().time()
        if (not self._last_cache_update or 
            current_time - self._last_cache_update > self.cache_ttl):
            await self._refresh_agents_cache()
        
        return self._agents_cache
    
    async def get_agent_by_name(self, name: str) -> Optional[Dict]:
        """Get agent by name"""
        agents = await self.get_all_agents()
        return agents.get(name)
    
    async def get_agent_by_id(self, agent_id: UUID) -> Optional[Dict]:
        """Get agent by ID"""
        return await agent_manager.get_agent_by_id(agent_id)
    
    async def select_agents_for_query(self, query: str) -> List[Dict]:
        """Select optimal agents for a given query using database analysis"""
        try:
            # Extract keywords from query
            keywords = self._extract_keywords(query)
            
            # Get agents from database that match keywords
            matching_agents = await agent_manager.get_agents_by_keywords(keywords)
            
            # Always include orchestrator
            orchestrator = await self.get_agent_by_name("Orchestration Agent")
            if orchestrator and orchestrator not in matching_agents:
                matching_agents.insert(0, orchestrator)
            
            # If no matches, use technical specialist as fallback
            if len(matching_agents) <= 1:
                technical = await self.get_agent_by_name("Technical Integration Specialist")
                if technical and technical not in matching_agents:
                    matching_agents.append(technical)
            
            # Limit to top 3 agents to avoid overwhelming
            selected_agents = matching_agents[:3]
            
            logger.info(f"Selected {len(selected_agents)} agents for query: {[a['name'] for a in selected_agents]}")
            return selected_agents
            
        except Exception as e:
            logger.error(f"Error selecting agents for query: {e}")
            # Fallback to default agents
            return await self._get_fallback_agents()
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query for agent matching"""
        query_lower = query.lower()
        
        # Common keywords for different domains
        keyword_mappings = {
            'webhook': ['webhook', 'api', 'integration', 'ssl', 'certificate', 'endpoint'],
            'billing': ['billing', 'payment', 'subscription', 'invoice', 'refund', 'charge'],
            'security': ['security', 'vulnerability', 'hack', 'breach', 'encryption', 'compliance'],
            'database': ['database', 'sql', 'query', 'migration', 'performance', 'timeout'],
            'deployment': ['deployment', 'docker', 'kubernetes', 'ci/cd', 'pipeline', 'infrastructure'],
            'legal': ['legal', 'contract', 'compliance', 'gdpr', 'privacy', 'terms'],
            'competitive': ['competitor', 'competitive', 'market', 'analysis', 'strategy'],
            'marketing': ['marketing', 'campaign', 'email', 'lead', 'nurturing'],
            'support': ['customer', 'support', 'onboarding', 'training', 'help']
        }
        
        extracted = []
        for category, keywords in keyword_mappings.items():
            if any(keyword in query_lower for keyword in keywords):
                extracted.extend(keywords)
        
        # Add direct words from query
        query_words = [word.strip('.,!?()[]') for word in query_lower.split() if len(word) > 3]
        extracted.extend(query_words)
        
        return list(set(extracted))  # Remove duplicates
    
    async def _get_fallback_agents(self) -> List[Dict]:
        """Get fallback agents when selection fails"""
        try:
            orchestrator = await self.get_agent_by_name("Orchestration Agent")
            technical = await self.get_agent_by_name("Technical Integration Specialist")
            
            fallback = []
            if orchestrator:
                fallback.append(orchestrator)
            if technical:
                fallback.append(technical)
            
            return fallback
        except Exception as e:
            logger.error(f"Error getting fallback agents: {e}")
            return []
    
    async def create_agent(self, agent_data: Dict) -> UUID:
        """Create a new agent"""
        try:
            agent_id = await agent_manager.create_agent(agent_data)
            await self._refresh_agents_cache()  # Refresh cache
            logger.info(f"Created new agent: {agent_data['name']}")
            return agent_id
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            raise
    
    async def update_agent(self, agent_id: UUID, updates: Dict) -> bool:
        """Update an existing agent"""
        try:
            success = await agent_manager.update_agent(agent_id, updates)
            if success:
                await self._refresh_agents_cache()  # Refresh cache
                logger.info(f"Updated agent {agent_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating agent: {e}")
            return False
    
    async def process_query_with_agents(self, query: str, selected_agents: List[Dict]) -> Dict:
        """Process query using selected agents and record metrics"""
        session_id = None
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create conversation session
            session_data = {
                'query': query,
                'agents_selected': [agent['name'] for agent in selected_agents],
                'metadata': {
                    'agent_selection_method': 'database_keywords',
                    'total_agents_available': len(await self.get_all_agents())
                }
            }
            session_id = await metrics_manager.create_conversation_session(session_data)
            
            # Process with adaptive LLM system
            result = await self.adaptive_llm.process_multi_agent_query(
                query=query,
                selected_agents=selected_agents,
                session_id=session_id
            )
            
            # Record metrics for each agent
            end_time = asyncio.get_event_loop().time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            for agent in selected_agents:
                await self._record_agent_metrics(
                    agent_id=agent['id'],
                    session_id=session_id,
                    query=query,
                    response_time_ms=response_time_ms,
                    success=result.get('success', True),
                    result=result
                )
            
            # Update session completion
            if session_id:
                await metrics_manager.update_session_completion(
                    session_id,
                    result.get('response', ''),
                    None  # User satisfaction will be updated separately
                )
            
            # Add session_id to result for frontend
            result['session_id'] = str(session_id)
            result['response_time_ms'] = response_time_ms
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query with database agents: {e}")
            
            # Record error metrics
            if session_id:
                for agent in selected_agents:
                    await self._record_agent_metrics(
                        agent_id=agent['id'],
                        session_id=session_id,
                        query=query,
                        success=False,
                        error_message=str(e)
                    )
            
            raise
    
    async def _record_agent_metrics(self, agent_id: UUID, session_id: UUID, 
                                   query: str, response_time_ms: int = 0,
                                   success: bool = True, result: Dict = None,
                                   error_message: str = None):
        """Record performance metrics for an agent"""
        try:
            metrics_data = {
                'agent_id': agent_id,
                'session_id': session_id,
                'query_text': query,
                'response_time_ms': response_time_ms,
                'success': success,
                'error_message': error_message,
                'context': {
                    'llm_selection': result.get('llm_selection') if result else None,
                    'processing_steps': result.get('processing_steps') if result else None
                }
            }
            
            # Add quality score if available
            if result and 'quality_score' in result:
                metrics_data['response_quality'] = result['quality_score']
            
            # Add cost information if available
            if result and 'cost_info' in result:
                metrics_data['cost_per_request'] = result['cost_info'].get('total_cost', 0.0)
                metrics_data['tokens_used'] = result['cost_info'].get('total_tokens', 0)
            
            await metrics_manager.record_agent_performance(metrics_data)
            
        except Exception as e:
            logger.error(f"Error recording agent metrics: {e}")
    
    async def record_user_feedback(self, session_id: UUID, rating: int, comment: str = ""):
        """Record user feedback for learning"""
        try:
            # Update session with user satisfaction
            await metrics_manager.update_session_completion(
                UUID(session_id) if isinstance(session_id, str) else session_id,
                None,  # Don't update final_response
                rating
            )
            
            # Generate learning insights if rating is very low or high
            if rating <= 2:
                await self._generate_improvement_insight(session_id, rating, comment)
            elif rating >= 4:
                await self._generate_success_insight(session_id, rating, comment)
            
            logger.info(f"Recorded user feedback: {rating}/5 for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error recording user feedback: {e}")
    
    async def _generate_improvement_insight(self, session_id: UUID, rating: int, comment: str):
        """Generate learning insight for improvement opportunities"""
        try:
            insight_data = {
                'insight_type': 'user_dissatisfaction',
                'title': f'Low user satisfaction (Rating: {rating}/5)',
                'description': f'User feedback indicates dissatisfaction. Comment: "{comment}"',
                'confidence_score': 0.8,
                'data_points': 1,
                'recommended_actions': [
                    'Review agent selection for similar queries',
                    'Analyze response quality metrics',
                    'Consider agent retraining or LLM parameter adjustment'
                ]
            }
            
            await learning_manager.generate_learning_insight(insight_data)
            
        except Exception as e:
            logger.error(f"Error generating improvement insight: {e}")
    
    async def _generate_success_insight(self, session_id: UUID, rating: int, comment: str):
        """Generate learning insight for successful patterns"""
        try:
            insight_data = {
                'insight_type': 'user_satisfaction',
                'title': f'High user satisfaction (Rating: {rating}/5)',
                'description': f'User expressed high satisfaction. Comment: "{comment}"',
                'confidence_score': 0.9,
                'data_points': 1,
                'recommended_actions': [
                    'Reinforce successful agent selection patterns',
                    'Analyze what worked well for similar queries',
                    'Consider this as a positive training example'
                ]
            }
            
            await learning_manager.generate_learning_insight(insight_data)
            
        except Exception as e:
            logger.error(f"Error generating success insight: {e}")
    
    async def get_performance_summary(self) -> Dict:
        """Get overall system performance summary"""
        try:
            agents = await self.get_all_agents()
            summary = {
                'total_agents': len(agents),
                'active_agents': sum(1 for a in agents.values() if a.get('is_active', True)),
                'agent_performance': {}
            }
            
            # Get performance for each agent
            for agent_name, agent in agents.items():
                agent_summary = await metrics_manager.get_agent_performance_summary(
                    agent['id'], days=30
                )
                summary['agent_performance'][agent_name] = agent_summary
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    async def close(self):
        """Close database connections"""
        await db_manager.close()

# Global instance
database_agent_manager = DatabaseAgentManager()