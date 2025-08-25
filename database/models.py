"""
Database models for AgentCraft
PostgreSQL integration for agent configuration and metrics persistence
"""

import asyncpg
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
import hashlib
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database connections and operations"""
    
    def __init__(self):
        self.pool = None
        self.database_url = os.getenv('DATABASE_URL', 
                                     'postgresql://agentcraft:agentcraft@localhost:5432/agentcraft')
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

class AgentManager:
    """Manages agent configurations in the database"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def get_all_agents(self) -> List[Dict]:
        """Get all active agents"""
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id, name, role, backstory, goal, llm_config, tools, 
                    keywords, avatar, color, domain, is_active,
                    performance_metrics, specialization_score, collaboration_rating,
                    created_at, updated_at
                FROM agents 
                WHERE is_active = true
                ORDER BY domain, name
            """)
            return [dict(row) for row in rows]
    
    async def get_agent_by_id(self, agent_id: UUID) -> Optional[Dict]:
        """Get agent by ID"""
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    id, name, role, backstory, goal, llm_config, tools,
                    keywords, avatar, color, domain, is_active,
                    performance_metrics, specialization_score, collaboration_rating,
                    created_at, updated_at
                FROM agents 
                WHERE id = $1
            """, agent_id)
            return dict(row) if row else None
    
    async def create_agent(self, agent_data: Dict) -> UUID:
        """Create a new agent"""
        agent_id = uuid4()
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agents (
                    id, name, role, backstory, goal, llm_config, tools,
                    keywords, avatar, color, domain, specialization_score
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """, 
                agent_id,
                agent_data['name'],
                agent_data['role'], 
                agent_data.get('backstory', ''),
                agent_data.get('goal', ''),
                json.dumps(agent_data.get('llm_config', {})),
                json.dumps(agent_data.get('tools', [])),
                json.dumps(agent_data.get('keywords', [])),
                agent_data.get('avatar', '🤖'),
                agent_data.get('color', 'blue'),
                agent_data.get('domain', 'general'),
                agent_data.get('specialization_score', 0.0)
            )
        logger.info(f"Created agent: {agent_data['name']} ({agent_id})")
        return agent_id
    
    async def update_agent(self, agent_id: UUID, updates: Dict) -> bool:
        """Update agent configuration"""
        set_clauses = []
        values = []
        param_count = 1
        
        for field, value in updates.items():
            if field in ['llm_config', 'tools', 'keywords', 'performance_metrics']:
                value = json.dumps(value)
            set_clauses.append(f"{field} = ${param_count}")
            values.append(value)
            param_count += 1
        
        if not set_clauses:
            return False
        
        query = f"""
            UPDATE agents 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
        """
        values.append(agent_id)
        
        async with self.db.pool.acquire() as conn:
            result = await conn.execute(query, *values)
            success = result.split()[-1] == '1'  # Check if 1 row was updated
            if success:
                logger.info(f"Updated agent {agent_id}: {list(updates.keys())}")
            return success
    
    async def deactivate_agent(self, agent_id: UUID) -> bool:
        """Deactivate an agent (soft delete)"""
        async with self.db.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE agents 
                SET is_active = false, updated_at = CURRENT_TIMESTAMP 
                WHERE id = $1
            """, agent_id)
            success = result.split()[-1] == '1'
            if success:
                logger.info(f"Deactivated agent {agent_id}")
            return success
    
    async def get_agents_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """Find agents that match given keywords"""
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id, name, role, keywords, specialization_score, collaboration_rating,
                    avatar, color, domain
                FROM agents 
                WHERE is_active = true 
                AND keywords ?| $1
                ORDER BY specialization_score DESC, collaboration_rating DESC
            """, keywords)
            return [dict(row) for row in rows]

class MetricsManager:
    """Manages performance metrics and learning data"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def record_agent_performance(self, metrics_data: Dict) -> UUID:
        """Record agent performance metrics"""
        metrics_id = uuid4()
        
        # Create query hash for pattern analysis
        query_hash = hashlib.sha256(
            metrics_data['query_text'].encode('utf-8')
        ).hexdigest()[:64]
        
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_metrics (
                    id, agent_id, session_id, query_hash, query_text,
                    response_quality, response_time_ms, tokens_used,
                    cost_per_request, user_feedback_rating, llm_used,
                    success, error_message, context
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """,
                metrics_id,
                metrics_data['agent_id'],
                metrics_data.get('session_id'),
                query_hash,
                metrics_data['query_text'],
                metrics_data.get('response_quality', 0.0),
                metrics_data.get('response_time_ms', 0),
                metrics_data.get('tokens_used', 0),
                metrics_data.get('cost_per_request', 0.0),
                metrics_data.get('user_feedback_rating'),
                metrics_data.get('llm_used', 'unknown'),
                metrics_data.get('success', True),
                metrics_data.get('error_message'),
                json.dumps(metrics_data.get('context', {}))
            )
        
        logger.info(f"Recorded metrics for agent {metrics_data['agent_id']}")
        return metrics_id
    
    async def create_conversation_session(self, session_data: Dict) -> UUID:
        """Create a new conversation session"""
        session_id = uuid4()
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO conversation_sessions (
                    id, user_id, query, agents_selected, total_response_time_ms,
                    escalated_to_human, escalation_reason, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                session_id,
                session_data.get('user_id'),
                session_data['query'],
                json.dumps(session_data.get('agents_selected', [])),
                session_data.get('total_response_time_ms', 0),
                session_data.get('escalated_to_human', False),
                session_data.get('escalation_reason'),
                json.dumps(session_data.get('metadata', {}))
            )
        return session_id
    
    async def update_session_completion(self, session_id: UUID, 
                                       final_response: str, 
                                       user_satisfaction: Optional[int] = None):
        """Update session when conversation is completed"""
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                UPDATE conversation_sessions 
                SET final_response = $1, user_satisfaction = $2, 
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = $3
            """, final_response, user_satisfaction, session_id)
    
    async def record_agent_collaboration(self, collaboration_data: Dict) -> UUID:
        """Record agent collaboration patterns"""
        collab_id = uuid4()
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_collaborations (
                    id, session_id, primary_agent_id, secondary_agent_id,
                    collaboration_type, effectiveness_score
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
                collab_id,
                collaboration_data['session_id'],
                collaboration_data['primary_agent_id'],
                collaboration_data['secondary_agent_id'],
                collaboration_data['collaboration_type'],
                collaboration_data.get('effectiveness_score', 0.0)
            )
        return collab_id
    
    async def update_agent_skills(self, agent_id: UUID, skill_name: str, 
                                 proficiency_delta: float = 0.0):
        """Update or create agent skill proficiency"""
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_skills (agent_id, skill_name, proficiency_score, usage_count, last_used)
                VALUES ($1, $2, GREATEST(0.0, LEAST(1.0, $3)), 1, CURRENT_TIMESTAMP)
                ON CONFLICT (agent_id, skill_name)
                DO UPDATE SET
                    proficiency_score = GREATEST(0.0, LEAST(1.0, agent_skills.proficiency_score + $3)),
                    usage_count = agent_skills.usage_count + 1,
                    last_used = CURRENT_TIMESTAMP,
                    improvement_trend = $3,
                    updated_at = CURRENT_TIMESTAMP
            """, agent_id, skill_name, proficiency_delta)
    
    async def get_agent_performance_summary(self, agent_id: UUID, days: int = 30) -> Dict:
        """Get performance summary for an agent"""
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_interactions,
                    AVG(response_quality) as avg_quality,
                    AVG(response_time_ms) as avg_response_time,
                    AVG(user_feedback_rating) as avg_user_rating,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate,
                    AVG(cost_per_request) as avg_cost
                FROM agent_metrics 
                WHERE agent_id = $1 
                AND recorded_at > CURRENT_TIMESTAMP - INTERVAL '%s days'
            """ % days, agent_id)
            
            return dict(row) if row else {}
    
    async def analyze_query_patterns(self, limit: int = 50) -> List[Dict]:
        """Analyze common query patterns for optimization"""
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    qp.pattern_hash,
                    qp.pattern_description,
                    qp.frequency,
                    qp.optimal_agents,
                    qp.avg_response_time_ms,
                    qp.avg_satisfaction,
                    qp.last_seen
                FROM query_patterns qp
                ORDER BY qp.frequency DESC, qp.avg_satisfaction DESC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]

class LearningManager:
    """Manages self-improvement and learning insights"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def generate_learning_insight(self, insight_data: Dict) -> UUID:
        """Generate and store a learning insight"""
        insight_id = uuid4()
        async with self.db.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO learning_insights (
                    id, insight_type, title, description, confidence_score,
                    data_points, recommended_actions
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                insight_id,
                insight_data['insight_type'],
                insight_data['title'],
                insight_data['description'],
                insight_data.get('confidence_score', 0.0),
                insight_data.get('data_points', 0),
                json.dumps(insight_data.get('recommended_actions', []))
            )
        logger.info(f"Generated learning insight: {insight_data['title']}")
        return insight_id
    
    async def get_pending_insights(self) -> List[Dict]:
        """Get insights that haven't been implemented yet"""
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    id, insight_type, title, description, confidence_score,
                    data_points, recommended_actions, created_at
                FROM learning_insights 
                WHERE status = 'pending'
                ORDER BY confidence_score DESC, data_points DESC
            """)
            return [dict(row) for row in rows]
    
    async def implement_insight(self, insight_id: UUID) -> bool:
        """Mark insight as implemented"""
        async with self.db.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE learning_insights 
                SET status = 'implemented', implemented_at = CURRENT_TIMESTAMP
                WHERE id = $1
            """, insight_id)
            success = result.split()[-1] == '1'
            if success:
                logger.info(f"Implemented insight {insight_id}")
            return success

# Global database manager instance
db_manager = DatabaseManager()
agent_manager = AgentManager(db_manager)
metrics_manager = MetricsManager(db_manager)
learning_manager = LearningManager(db_manager)