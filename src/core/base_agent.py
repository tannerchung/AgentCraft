
"""
Base Agent class for AgentCraft specialized agent architecture.
Demonstrates domain expertise over generic topic handling.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for specialized agents in AgentCraft.
    Emphasizes domain knowledge depth over template responses.
    """
    
    def __init__(self, name: str, expertise_domain: str, description: str):
        self.name = name
        self.expertise_domain = expertise_domain
        self.description = description
        self.performance_metrics = {
            "queries_handled": 0,
            "avg_response_time": 0.0,
            "expertise_confidence": 0.0
        }
        
    @abstractmethod
    def handle_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle a specialized query within the agent's domain expertise.
        Returns structured response with confidence scores.
        """
        pass
    
    def _update_metrics(self, response_time: float, confidence: float):
        """Update performance tracking metrics."""
        self.performance_metrics["queries_handled"] += 1
        
        # Update average response time
        current_avg = self.performance_metrics["avg_response_time"]
        count = self.performance_metrics["queries_handled"]
        self.performance_metrics["avg_response_time"] = (
            (current_avg * (count - 1) + response_time) / count
        )
        
        # Update average confidence
        current_confidence = self.performance_metrics["expertise_confidence"]
        self.performance_metrics["expertise_confidence"] = (
            (current_confidence * (count - 1) + confidence) / count
        )
        
        logger.info(f"{self.name}: Handled query {count}, avg confidence: {self.performance_metrics['expertise_confidence']:.2f}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and performance metrics."""
        return {
            "name": self.name,
            "expertise_domain": self.expertise_domain,
            "description": self.description,
            "performance_metrics": self.performance_metrics,
            "specialized_knowledge": self._get_specialized_knowledge()
        }
    
    @abstractmethod
    def _get_specialized_knowledge(self) -> Dict[str, str]:
        """Return domain-specific knowledge areas."""
        pass
