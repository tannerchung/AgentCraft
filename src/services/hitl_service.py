"""
Human-in-the-Loop (HITL) Service for AgentCraft
Handles escalation, feedback, and continuous learning
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import random

class EscalationReason(Enum):
    """Reasons for escalating to human operator"""
    LOW_CONFIDENCE = "low_confidence"
    MISSING_INFO = "missing_information"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    USER_REQUEST = "user_requested"
    COMPLEX_ISSUE = "complex_issue"
    POLICY_VIOLATION = "policy_violation"
    REPEAT_FAILURE = "repeat_failure"

class EscalationPriority(Enum):
    """Priority levels for escalation"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class EscalationContext:
    """Context for escalation to human operator"""
    conversation_id: str
    user_id: str
    agent_id: str
    reason: EscalationReason
    priority: EscalationPriority
    conversation_history: List[Dict[str, Any]]
    agent_analysis: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class HumanFeedback:
    """Feedback from human operator"""
    escalation_id: str
    operator_id: str
    resolution: str
    feedback_type: str  # 'correction', 'validation', 'teaching'
    agent_response_quality: int  # 1-5 rating
    should_retrain: bool
    notes: str
    timestamp: str

class HITLService:
    """Service for managing Human-in-the-Loop operations"""
    
    def __init__(self):
        self.confidence_threshold = 0.7
        self.sentiment_threshold = -0.5
        self.escalation_queue = []
        self.feedback_history = []
        self.learning_cache = {}
        self.operator_pool = []
        self.metrics = {
            "total_escalations": 0,
            "resolved_escalations": 0,
            "avg_resolution_time": 0,
            "feedback_incorporated": 0,
            "performance_improvement": 0
        }
    
    async def evaluate_escalation(
        self, 
        query: str,
        agent_response: Dict[str, Any],
        confidence_score: float,
        sentiment_score: float = 0.0,
        conversation_history: List[Dict] = None
    ) -> Tuple[bool, Optional[EscalationContext]]:
        """
        Evaluate if escalation to human is needed
        Returns (should_escalate, escalation_context)
        """
        reasons = []
        priority = EscalationPriority.LOW
        
        # Check confidence threshold
        if confidence_score < self.confidence_threshold:
            reasons.append(EscalationReason.LOW_CONFIDENCE)
            priority = EscalationPriority.MEDIUM
            
        # Check sentiment
        if sentiment_score < self.sentiment_threshold:
            reasons.append(EscalationReason.NEGATIVE_SENTIMENT)
            priority = EscalationPriority.HIGH
            
        # Check for missing information indicators
        missing_info_indicators = [
            "i don't have enough information",
            "could you provide more details",
            "unable to determine",
            "insufficient data"
        ]
        
        response_text = str(agent_response.get("content", "")).lower()
        if any(indicator in response_text for indicator in missing_info_indicators):
            reasons.append(EscalationReason.MISSING_INFO)
            priority = EscalationPriority.MEDIUM
            
        # Check for complex issues (based on query complexity)
        if self._assess_complexity(query) > 0.8:
            reasons.append(EscalationReason.COMPLEX_ISSUE)
            priority = EscalationPriority.HIGH
            
        # Check conversation history for repeat failures
        if conversation_history and self._check_repeat_failures(conversation_history):
            reasons.append(EscalationReason.REPEAT_FAILURE)
            priority = EscalationPriority.CRITICAL
        
        should_escalate = len(reasons) > 0
        
        if should_escalate:
            context = EscalationContext(
                conversation_id=f"conv_{datetime.now().timestamp()}",
                user_id="user_demo",
                agent_id=agent_response.get("agent_id", "unknown"),
                reason=reasons[0],  # Primary reason
                priority=priority,
                conversation_history=conversation_history or [],
                agent_analysis={
                    "confidence": confidence_score,
                    "sentiment": sentiment_score,
                    "response": agent_response,
                    "all_reasons": [r.value for r in reasons]
                },
                timestamp=datetime.now().isoformat(),
                metadata={"query": query}
            )
            
            # Add to escalation queue
            await self._queue_escalation(context)
            
            return True, context
        
        return False, None
    
    async def _queue_escalation(self, context: EscalationContext):
        """Add escalation to queue and notify operators"""
        self.escalation_queue.append(context)
        self.metrics["total_escalations"] += 1
        
        # Simulate notification to human operators
        logging.info(f"Escalation queued: {context.reason.value} - Priority: {context.priority.name}")
        
        # In production, this would trigger actual notifications
        # await self._notify_operators(context)
    
    def _assess_complexity(self, query: str) -> float:
        """Assess query complexity (0-1 scale)"""
        # Simple heuristic based on length and technical terms
        complexity_score = 0.0
        
        # Length factor
        word_count = len(query.split())
        if word_count > 50:
            complexity_score += 0.3
        elif word_count > 30:
            complexity_score += 0.2
        
        # Technical terms factor
        technical_terms = [
            "integration", "api", "webhook", "authentication",
            "migration", "architecture", "scalability", "compliance",
            "encryption", "synchronization", "orchestration"
        ]
        
        query_lower = query.lower()
        technical_count = sum(1 for term in technical_terms if term in query_lower)
        complexity_score += min(technical_count * 0.15, 0.5)
        
        # Multiple questions factor
        if query.count("?") > 1:
            complexity_score += 0.2
        
        return min(complexity_score, 1.0)
    
    def _check_repeat_failures(self, conversation_history: List[Dict]) -> bool:
        """Check if there are repeated failures in conversation"""
        if len(conversation_history) < 3:
            return False
        
        # Look for patterns of user dissatisfaction
        negative_indicators = [
            "that's not what i asked",
            "wrong answer",
            "doesn't help",
            "still having issues",
            "not working"
        ]
        
        negative_count = 0
        for message in conversation_history[-3:]:
            if message.get("role") == "user":
                text = message.get("content", "").lower()
                if any(indicator in text for indicator in negative_indicators):
                    negative_count += 1
        
        return negative_count >= 2
    
    async def process_human_feedback(
        self,
        escalation_id: str,
        operator_id: str,
        resolution: str,
        quality_rating: int,
        teaching_notes: str = ""
    ) -> HumanFeedback:
        """Process feedback from human operator"""
        feedback = HumanFeedback(
            escalation_id=escalation_id,
            operator_id=operator_id,
            resolution=resolution,
            feedback_type="teaching" if teaching_notes else "correction",
            agent_response_quality=quality_rating,
            should_retrain=quality_rating < 3,
            notes=teaching_notes,
            timestamp=datetime.now().isoformat()
        )
        
        # Store feedback
        self.feedback_history.append(feedback)
        self.metrics["resolved_escalations"] += 1
        
        # Update learning cache
        await self._incorporate_feedback(feedback)
        
        return feedback
    
    async def _incorporate_feedback(self, feedback: HumanFeedback):
        """Incorporate human feedback into learning system"""
        # Extract patterns from feedback
        if feedback.should_retrain:
            # In production, this would trigger model retraining
            self.learning_cache[feedback.escalation_id] = {
                "resolution": feedback.resolution,
                "quality": feedback.agent_response_quality,
                "teaching": feedback.notes,
                "timestamp": feedback.timestamp
            }
            self.metrics["feedback_incorporated"] += 1
            
            # Simulate performance improvement
            self.metrics["performance_improvement"] = min(
                self.metrics["performance_improvement"] + 0.5,
                25.0  # Cap at 25% improvement
            )
    
    def get_escalation_metrics(self) -> Dict[str, Any]:
        """Get HITL metrics"""
        escalation_rate = 0
        if self.metrics["total_escalations"] > 0:
            escalation_rate = (self.metrics["resolved_escalations"] / 
                             self.metrics["total_escalations"]) * 100
        
        return {
            "total_escalations": self.metrics["total_escalations"],
            "resolved_escalations": self.metrics["resolved_escalations"],
            "escalation_rate": escalation_rate,
            "avg_resolution_time": "2.3 minutes",  # Simulated
            "feedback_incorporated": self.metrics["feedback_incorporated"],
            "performance_improvement": f"{self.metrics['performance_improvement']:.1f}%",
            "queue_length": len(self.escalation_queue),
            "learning_cache_size": len(self.learning_cache)
        }
    
    def simulate_sentiment_analysis(self, text: str) -> float:
        """
        Simulate sentiment analysis
        In production, use Google Cloud NLP or Amazon Comprehend
        """
        # Simple keyword-based sentiment
        positive_words = ["great", "excellent", "perfect", "thanks", "good", "helpful"]
        negative_words = ["bad", "terrible", "awful", "useless", "frustrated", "angry"]
        
        text_lower = text.lower()
        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        if positive_score > negative_score:
            return min(positive_score * 0.3, 1.0)
        elif negative_score > positive_score:
            return max(-negative_score * 0.3, -1.0)
        else:
            return 0.0
    
    async def get_operator_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for human operators"""
        return {
            "queue": [
                {
                    "id": esc.conversation_id,
                    "priority": esc.priority.name,
                    "reason": esc.reason.value,
                    "wait_time": "30 seconds",  # Simulated
                    "user_sentiment": esc.agent_analysis.get("sentiment", 0)
                }
                for esc in self.escalation_queue[:5]  # Top 5 in queue
            ],
            "stats": {
                "active_escalations": len(self.escalation_queue),
                "avg_wait_time": "45 seconds",
                "operators_online": 3,  # Simulated
                "resolution_rate": "94%"
            },
            "recent_feedback": [
                {
                    "operator": fb.operator_id,
                    "quality": fb.agent_response_quality,
                    "type": fb.feedback_type,
                    "time": fb.timestamp
                }
                for fb in self.feedback_history[-5:]  # Last 5 feedbacks
            ]
        }

# Singleton instance
hitl_service = HITLService()