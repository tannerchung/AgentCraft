
"""
Agent Router for AgentCraft - Intelligent routing to specialized agents vs generic topics
"""

from typing import Dict, List, Optional, Any
from src.core.base_agent import BaseAgent
from src.agents.technical_support_agent import TechnicalSupportAgent
import time
import logging

logger = logging.getLogger(__name__)


class AgentRouter:
    """Intelligent routing to specialized agents vs generic topics"""
    
    def __init__(self):
        self.agents = {}
        self.routing_rules = {}
        self.performance_tracker = {
            "total_requests": 0,
            "successful_routes": 0,
            "average_confidence": 0.0
        }
        
    def register_agent(self, agent_name: str, agent_instance: Any, keywords: List[str]):
        """Register a specialized agent with routing keywords"""
        self.agents[agent_name] = agent_instance
        self.routing_rules[agent_name] = keywords
    
    def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route query to most appropriate specialized agent"""
        
        start_time = time.time()
        self.performance_tracker["total_requests"] += 1
        
        # Analyze query for agent selection
        query_lower = query.lower()
        agent_scores = {}
        
        # Score each agent based on keyword matching
        for agent_name, keywords in self.routing_rules.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                agent_scores[agent_name] = score
        
        # Select highest scoring agent
        if agent_scores:
            best_agent = max(agent_scores.items(), key=lambda x: x[1])
            selected_agent = best_agent[0]
            confidence = min(best_agent[1] / 3.0, 1.0)  # Normalize confidence
        else:
            # Default to technical support for technical queries
            selected_agent = "technical_support"
            confidence = 0.5
        
        # Route to selected agent
        if selected_agent in self.agents:
            response = self.agents[selected_agent].process_technical_query(query, context)
            self.performance_tracker["successful_routes"] += 1
        else:
            response = {
                "error": f"Agent {selected_agent} not available",
                "available_agents": list(self.agents.keys())
            }
            confidence = 0.0
        
        routing_time = time.time() - start_time
        
        return {
            "routing_info": {
                "selected_agent": selected_agent,
                "confidence": confidence,
                "routing_time": routing_time,
                "available_agents": list(self.agents.keys())
            },
            "agent_response": response,
            "performance_metrics": self.performance_tracker
        }
    
# Initialize router with technical support agent
def initialize_agent_system():
    """Set up the specialized agent system"""
    router = AgentRouter()
    
    # Register Technical Support Agent
    tech_agent = TechnicalSupportAgent()
    router.register_agent(
        agent_name="technical_support",
        agent_instance=tech_agent,
        keywords=["webhook", "api", "integration", "signature", "timeout", "403", "429", "technical", "agentforce", "competitor"]
    )
    
    return router

# Global instance for use in FastAPI
agent_router = initialize_agent_system()
