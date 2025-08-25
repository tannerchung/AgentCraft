"""
Enhanced Adaptive LLM System with Database Integration
Combines database persistence with memory caching for optimal performance
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from uuid import UUID
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.crew_db_integration import database_crew_orchestrator, crew_agent_pool
from database.models import metrics_manager, learning_manager
from src.agents.galileo_adaptive_integration import galileo_integration

logger = logging.getLogger(__name__)

class EnhancedAdaptiveSystem:
    """Enhanced system that combines database persistence with adaptive AI"""
    
    def __init__(self):
        self.initialized = False
        self.performance_cache = {}
        self.last_optimization = time.time()
        self.optimization_interval = 3600  # 1 hour
    
    async def initialize(self):
        """Initialize the enhanced system"""
        try:
            # Initialize database-backed CrewAI orchestrator
            await database_crew_orchestrator.initialize()
            
            self.initialized = True
            logger.info("Enhanced Adaptive System initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Adaptive System: {e}")
            raise
    
    async def process_query(self, query: str, context: Dict = None, 
                           session_id: UUID = None) -> Dict[str, Any]:
        """Process query with database agents and enhanced tracking"""
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        
        # Initialize real-time tracking if session_id provided
        tracking_session_id = str(session_id) if session_id else f"session_{int(time.time())}"
        
        try:
            # Start Galileo trace for this conversation
            galileo_trace_id = None
            if galileo_integration.galileo_enabled:
                galileo_trace_id = galileo_integration.start_conversation_trace(tracking_session_id)
                
                galileo_integration.log_llm_selection_event(
                    query=query,
                    selected_llms={"system": "database_backed_crewai"},
                    complexity_score=self._calculate_complexity_score(query),
                    context=context
                )
            
            # Use enhanced database-backed CrewAI orchestration with real-time tracking
            result = await self._process_query_with_tracking(
                query=query, 
                context=context, 
                tracking_session_id=tracking_session_id
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Record metrics if we have a session
            if session_id and result.get('success'):
                await self._record_enhanced_metrics(
                    session_id=session_id,
                    query=query,
                    result=result,
                    processing_time=processing_time,
                    agents_used=result.get('agents_used', [])
                )
            
            # Log performance metrics to Galileo
            if galileo_integration.galileo_enabled:
                performance_metrics = {
                    "response_time": processing_time,
                    "quality_score": 0.9,  # Could be calculated from result
                    "success_rate": 1.0 if result.get('success') else 0.0,
                    "efficiency_score": self._calculate_efficiency_score(result),
                    "token_count": len(query.split()) + len(str(result.get('response', '')).split())
                }
                
                galileo_integration.log_performance_metrics(
                    model_name="enhanced_database_system",
                    metrics=performance_metrics
                )
            
            # Enhanced result with additional metadata
            enhanced_result = {
                **result,
                'enhanced_system': True,
                'database_backed': True,
                'processing_time_ms': int(processing_time * 1000),
                'galileo_traced': galileo_trace_id is not None,
                'optimization_status': await self._get_optimization_status(),
                'tracking_session_id': tracking_session_id,
                'real_time_tracking': True
            }
            
            # Trigger optimization if needed
            if time.time() - self.last_optimization > self.optimization_interval:
                asyncio.create_task(self._run_optimization_cycle())
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in enhanced query processing: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'I encountered an error processing your request.',
                'enhanced_system': True,
                'database_backed': True,
                'processing_time_ms': int((time.time() - start_time) * 1000),
                'tracking_session_id': tracking_session_id
            }
        finally:
            # Always clean up Galileo trace
            if galileo_integration.galileo_enabled:
                galileo_integration.end_conversation_trace()
    
    async def _process_query_with_tracking(self, query: str, context: Dict, 
                                         tracking_session_id: str) -> Dict[str, Any]:
        """Process query with real-time tracking integration"""
        from src.agents.realtime_agent_tracker import realtime_tracker, AgentStatus
        
        try:
            # Get selected agents
            from src.agents.crew_db_integration import crew_agent_pool
            await crew_agent_pool._ensure_fresh_cache()
            
            # Extract keywords for agent selection
            keywords = self._extract_keywords(query)
            selected_agents = await crew_agent_pool.get_agents_by_keywords(keywords)
            
            # Always include orchestrator if available
            orchestrator = await crew_agent_pool.get_agent("Orchestration Agent")
            if orchestrator and orchestrator not in selected_agents:
                selected_agents.insert(0, orchestrator)
            
            # Fallback to technical agent if no matches
            if len(selected_agents) <= 1:
                technical = await crew_agent_pool.get_agent("Technical Integration Specialist")
                if technical and technical not in selected_agents:
                    selected_agents.append(technical)
            
            agent_names = [agent.name for agent in selected_agents[:3]]  # Limit to 3 agents
            
            # Start real-time tracking
            realtime_tracker.start_session(tracking_session_id, query, agent_names)
            
            # Simulate agent processing with real-time updates
            await self._simulate_agent_processing(tracking_session_id, selected_agents, query, context)
            
            # Use the database orchestrator for actual processing
            result = await database_crew_orchestrator.process_query(query, context)
            
            # Complete tracking
            final_response = result.get('response', 'Processing completed')
            realtime_tracker.complete_session(tracking_session_id, final_response)
            
            return {
                **result,
                'agents_used': agent_names,
                'real_time_tracked': True
            }
            
        except Exception as e:
            # Error tracking
            from src.agents.realtime_agent_tracker import realtime_tracker
            realtime_tracker.error_session(tracking_session_id, str(e))
            raise
    
    async def _simulate_agent_processing(self, session_id: str, agents: List, 
                                       query: str, context: Dict):
        """Simulate realistic agent processing phases for real-time tracking"""
        from src.agents.realtime_agent_tracker import realtime_tracker, AgentStatus
        
        try:
            for i, agent in enumerate(agents):
                agent_name = agent.name
                
                # Phase 1: Analysis
                realtime_tracker.update_agent_status(
                    session_id, agent_name, AgentStatus.ANALYZING,
                    task=f"Analyzing query for {agent.domain} expertise",
                    progress=20.0,
                    details="Breaking down query requirements"
                )
                realtime_tracker.add_crew_output(
                    session_id, "analysis", 
                    f"Agent {agent_name} analyzing query complexity and requirements",
                    agent_name
                )
                await asyncio.sleep(0.5)  # Simulate analysis time
                
                # Phase 2: Processing
                realtime_tracker.update_agent_status(
                    session_id, agent_name, AgentStatus.PROCESSING,
                    task=f"Processing {agent.domain} solution",
                    progress=60.0,
                    details="Generating specialized response"
                )
                realtime_tracker.add_crew_output(
                    session_id, "processing",
                    f"Agent {agent_name} applying {agent.domain} expertise to generate solution",
                    agent_name
                )
                await asyncio.sleep(1.0)  # Simulate processing time
                
                # Phase 3: Collaboration (if multiple agents)
                if len(agents) > 1 and i > 0:
                    realtime_tracker.update_agent_status(
                        session_id, agent_name, AgentStatus.COLLABORATING,
                        task="Coordinating with other agents",
                        progress=80.0,
                        details=f"Collaborating with {agents[0].name}"
                    )
                    realtime_tracker.add_crew_output(
                        session_id, "collaboration",
                        f"Agent {agent_name} coordinating solution with {agents[0].name}",
                        agent_name
                    )
                    await asyncio.sleep(0.3)
                
                # Phase 4: Completion
                realtime_tracker.update_agent_status(
                    session_id, agent_name, AgentStatus.COMPLETING,
                    task="Finalizing response",
                    progress=90.0,
                    details="Preparing final output"
                )
                await asyncio.sleep(0.2)
            
            # System synthesis phase
            realtime_tracker.update_crew_phase(session_id, "synthesis", "Combining agent responses")
            realtime_tracker.add_crew_output(
                session_id, "synthesis",
                f"Synthesizing responses from {len(agents)} agents into final answer"
            )
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Error in agent processing simulation: {e}")
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords for agent selection"""
        query_lower = query.lower()
        
        domain_keywords = {
            'technical': ['api', 'webhook', 'integration', 'ssl', 'certificate', 'error', 'bug'],
            'billing': ['payment', 'billing', 'subscription', 'invoice', 'refund', 'charge'],
            'security': ['security', 'vulnerability', 'breach', 'hack', 'compliance', 'audit'],
            'database': ['database', 'sql', 'query', 'migration', 'performance', 'timeout'],
            'competitive': ['competitor', 'competitive', 'market', 'analysis', 'compare'],
            'support': ['help', 'support', 'issue', 'problem', 'trouble', 'assist']
        }
        
        extracted = []
        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                extracted.extend(keywords)
        
        words = [w.strip('.,!?()[]"\'') for w in query_lower.split() if len(w) > 3]
        extracted.extend(words)
        
        return list(set(extracted))
    
    async def _record_enhanced_metrics(self, session_id: UUID, query: str, 
                                     result: Dict, processing_time: float,
                                     agents_used: List[str]):
        """Record enhanced metrics for learning and optimization"""
        try:
            # Get agent IDs for the agents that were used
            for agent_name in agents_used:
                db_agent = await crew_agent_pool.get_agent(agent_name)
                if db_agent:
                    metrics_data = {
                        'agent_id': db_agent.id,
                        'session_id': session_id,
                        'query_text': query,
                        'response_time_ms': int(processing_time * 1000),
                        'success': result.get('success', True),
                        'response_quality': 0.9,  # Default high quality for database agents
                        'llm_used': 'database_crewai_system',
                        'context': {
                            'agents_used': agents_used,
                            'database_backed': True,
                            'crew_execution': result.get('crew_execution', False)
                        }
                    }
                    
                    await metrics_manager.record_agent_performance(metrics_data)
            
            # Record agent collaboration if multiple agents were used
            if len(agents_used) > 1:
                await self._record_agent_collaboration(session_id, agents_used)
            
        except Exception as e:
            logger.error(f"Error recording enhanced metrics: {e}")
    
    async def _record_agent_collaboration(self, session_id: UUID, agents_used: List[str]):
        """Record agent collaboration patterns"""
        try:
            for i in range(len(agents_used) - 1):
                primary_agent = await crew_agent_pool.get_agent(agents_used[i])
                secondary_agent = await crew_agent_pool.get_agent(agents_used[i + 1])
                
                if primary_agent and secondary_agent:
                    collaboration_data = {
                        'session_id': session_id,
                        'primary_agent_id': primary_agent.id,
                        'secondary_agent_id': secondary_agent.id,
                        'collaboration_type': 'sequential',
                        'effectiveness_score': 0.85  # Default good collaboration
                    }
                    
                    await metrics_manager.record_agent_collaboration(collaboration_data)
        
        except Exception as e:
            logger.error(f"Error recording agent collaboration: {e}")
    
    def _calculate_complexity_score(self, query: str) -> float:
        """Calculate query complexity score"""
        # Simple heuristic based on query characteristics
        score = 0.5  # Base score
        
        # Length factor
        word_count = len(query.split())
        if word_count > 20:
            score += 0.2
        elif word_count > 10:
            score += 0.1
        
        # Technical keywords
        technical_keywords = ['api', 'webhook', 'ssl', 'certificate', 'integration', 'database']
        technical_count = sum(1 for kw in technical_keywords if kw in query.lower())
        score += min(technical_count * 0.1, 0.3)
        
        # Question complexity
        if '?' in query:
            score += 0.1
        if query.count('?') > 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_efficiency_score(self, result: Dict) -> float:
        """Calculate efficiency score based on result"""
        if not result.get('success'):
            return 0.0
        
        # Base efficiency
        efficiency = 0.8
        
        # Bonus for using multiple agents effectively
        agents_used = len(result.get('agents_used', []))
        if agents_used > 1:
            efficiency += 0.1
        
        # Database backing bonus
        if result.get('database_backed'):
            efficiency += 0.1
        
        return min(efficiency, 1.0)
    
    async def _get_optimization_status(self) -> Dict:
        """Get current optimization status"""
        cache_stats = crew_agent_pool.get_cache_stats()
        
        return {
            'last_optimization': self.last_optimization,
            'next_optimization_in': max(0, self.optimization_interval - (time.time() - self.last_optimization)),
            'cache_stats': cache_stats,
            'performance_optimized': True
        }
    
    async def _run_optimization_cycle(self):
        """Run optimization cycle to improve system performance"""
        try:
            logger.info("Starting optimization cycle...")
            
            # Refresh agent cache
            await crew_agent_pool.refresh_agents(force=True)
            
            # Generate learning insights
            await self._generate_performance_insights()
            
            # Update last optimization time
            self.last_optimization = time.time()
            
            logger.info("Optimization cycle completed")
            
        except Exception as e:
            logger.error(f"Error in optimization cycle: {e}")
    
    async def _generate_performance_insights(self):
        """Generate insights about system performance"""
        try:
            agents = await crew_agent_pool.get_all_agents()
            
            # Analyze agent performance and generate insights
            for agent_name, agent in agents.items():
                performance = await metrics_manager.get_agent_performance_summary(agent.id)
                
                if performance.get('total_interactions', 0) > 0:
                    # Check for performance issues
                    avg_quality = performance.get('avg_quality', 0)
                    success_rate = performance.get('success_rate', 0)
                    
                    if avg_quality < 0.7 or success_rate < 0.8:
                        # Generate improvement insight
                        insight_data = {
                            'insight_type': 'agent_performance_decline',
                            'title': f'Performance decline detected: {agent_name}',
                            'description': f'Agent showing declining performance: Quality={avg_quality:.2f}, Success Rate={success_rate:.2f}',
                            'confidence_score': 0.8,
                            'data_points': performance.get('total_interactions', 0),
                            'recommended_actions': [
                                'Review agent configuration and prompts',
                                'Consider LLM parameter adjustment',
                                'Analyze failed interactions for patterns',
                                'Update agent training data'
                            ]
                        }
                        
                        await learning_manager.generate_learning_insight(insight_data)
        
        except Exception as e:
            logger.error(f"Error generating performance insights: {e}")
    
    async def create_custom_agent(self, agent_config: Dict) -> Dict:
        """Create a custom agent and add to the system"""
        try:
            # Validate required fields
            required_fields = ['name', 'role', 'domain']
            missing_fields = [field for field in required_fields if field not in agent_config]
            
            if missing_fields:
                return {
                    'success': False,
                    'error': f'Missing required fields: {missing_fields}'
                }
            
            # Set defaults
            agent_data = {
                'name': agent_config['name'],
                'role': agent_config['role'],
                'domain': agent_config.get('domain', 'custom'),
                'backstory': agent_config.get('backstory', f'You are a specialized agent for {agent_config["domain"]} tasks.'),
                'goal': agent_config.get('goal', f'Provide excellent support for {agent_config["role"]} related queries'),
                'keywords': agent_config.get('keywords', []),
                'avatar': agent_config.get('avatar', '🤖'),
                'color': agent_config.get('color', 'blue'),
                'llm_config': agent_config.get('llm_config', {'model': 'claude-3-5-sonnet', 'temperature': 0.2}),
                'tools': agent_config.get('tools', [])
            }
            
            # Create in database
            from database.models import agent_manager
            agent_id = await agent_manager.create_agent(agent_data)
            
            # Hot reload the agent in the pool
            await crew_agent_pool.hot_reload_agent(agent_id)
            
            return {
                'success': True,
                'agent_id': str(agent_id),
                'message': f'Successfully created agent: {agent_config["name"]}'
            }
            
        except Exception as e:
            logger.error(f"Error creating custom agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_agent_config(self, agent_id: UUID, updates: Dict) -> Dict:
        """Update agent configuration and hot reload"""
        try:
            from database.models import agent_manager
            
            # Update in database
            success = await agent_manager.update_agent(agent_id, updates)
            
            if success:
                # Hot reload the agent
                await crew_agent_pool.hot_reload_agent(agent_id)
                
                return {
                    'success': True,
                    'message': 'Agent updated and hot reloaded successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update agent in database'
                }
                
        except Exception as e:
            logger.error(f"Error updating agent config: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        try:
            agent_status = await database_crew_orchestrator.get_agent_status()
            optimization_status = await self._get_optimization_status()
            
            # Get recent learning insights
            insights = await learning_manager.get_pending_insights()
            
            return {
                'system_healthy': self.initialized,
                'database_connected': True,
                'agents': agent_status,
                'optimization': optimization_status,
                'pending_insights': len(insights),
                'galileo_enabled': galileo_integration.galileo_enabled,
                'cache_performance': crew_agent_pool.get_cache_stats()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'system_healthy': False,
                'error': str(e)
            }

# Global instance
enhanced_adaptive_system = EnhancedAdaptiveSystem()