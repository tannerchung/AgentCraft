
"""
Agent Router for AgentCraft - demonstrates architectural flexibility
and rapid customization capabilities.
"""

from typing import Dict, List, Optional, Any
from src.core.base_agent import BaseAgent
import re
import logging

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Intelligent routing system that matches queries to specialized agents
    based on domain expertise rather than generic topic classification.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.routing_patterns: Dict[str, List[str]] = {}
        
    def register_agent(self, agent: BaseAgent, routing_keywords: List[str]):
        """
        Register a specialized agent with routing keywords.
        Enables rapid customization for new domains.
        """
        self.agents[agent.name] = agent
        self.routing_patterns[agent.name] = routing_keywords
        logger.info(f"Registered specialized agent: {agent.name} for domain: {agent.expertise_domain}")
    
    def route_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route query to the most appropriate specialized agent.
        Demonstrates domain knowledge advantage over generic responses.
        """
        # Calculate routing scores based on keyword matching and context
        routing_scores = {}
        
        for agent_name, keywords in self.routing_patterns.items():
            score = self._calculate_routing_score(query, keywords, context)
            routing_scores[agent_name] = score
        
        # Select agent with highest confidence score
        if routing_scores:
            best_agent_name = max(routing_scores, key=routing_scores.get)
            confidence = routing_scores[best_agent_name]
            
            if confidence > 0.3:  # Minimum confidence threshold
                selected_agent = self.agents[best_agent_name]
                logger.info(f"Routing to specialized agent: {best_agent_name} (confidence: {confidence:.2f})")
                
                response = selected_agent.handle_query(query, context)
                response["routing_info"] = {
                    "selected_agent": best_agent_name,
                    "routing_confidence": confidence,
                    "available_agents": list(self.agents.keys())
                }
                return response
        
        # Fallback response if no specialized agent matches
        return {
            "response": "I don't have a specialized agent for this query. Consider adding domain expertise for better results.",
            "confidence": 0.1,
            "agent_used": "fallback",
            "routing_info": {
                "selected_agent": "none",
                "routing_confidence": 0.0,
                "available_agents": list(self.agents.keys())
            }
        }
    
    def _calculate_routing_score(self, query: str, keywords: List[str], context: Optional[Dict[str, Any]]) -> float:
        """Calculate routing confidence score based on keyword matching."""
        query_lower = query.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword.lower() in query_lower:
                matches += 1
        
        # Base score from keyword matching
        score = matches / len(keywords) if keywords else 0
        
        # Boost score if context provides additional signals
        if context and "technical_indicators" in context:
            technical_matches = sum(1 for indicator in context["technical_indicators"] 
                                  if any(keyword.lower() in indicator.lower() for keyword in keywords))
            score += technical_matches * 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status and performance metrics for all registered agents."""
        return {
            "total_agents": len(self.agents),
            "agents": {name: agent.get_capabilities() for name, agent in self.agents.items()},
            "routing_patterns": self.routing_patterns
        }
