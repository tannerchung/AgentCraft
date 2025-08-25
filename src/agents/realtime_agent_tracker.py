"""
Real-time Agent Tracker for CrewAI Integration
Tracks agent execution states and broadcasts to frontend
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Set
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    ANALYZING = "analyzing"
    PROCESSING = "processing"
    COLLABORATING = "collaborating"
    COMPLETING = "completing"
    FINISHED = "finished"
    ERROR = "error"

@dataclass
class AgentActivity:
    agent_id: str
    agent_name: str
    status: AgentStatus
    current_task: Optional[str] = None
    progress: float = 0.0
    details: Optional[str] = None
    started_at: Optional[float] = None
    updated_at: float = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = time.time()
        if self.started_at is None and self.status != AgentStatus.IDLE:
            self.started_at = time.time()

@dataclass 
class CrewExecutionState:
    session_id: str
    query: str
    total_agents: int
    active_agents: List[AgentActivity]
    completed_agents: List[str] = None
    current_phase: str = "initialization"
    overall_progress: float = 0.0
    started_at: float = None
    estimated_completion: Optional[float] = None
    crew_output: List[Dict] = None
    
    def __post_init__(self):
        if self.completed_agents is None:
            self.completed_agents = []
        if self.crew_output is None:
            self.crew_output = []
        if self.started_at is None:
            self.started_at = time.time()
        
        # Calculate initial overall progress
        if self.active_agents:
            total_progress = sum(agent.progress for agent in self.active_agents)
            self.overall_progress = total_progress / len(self.active_agents)

class RealtimeAgentTracker:
    """Tracks agent execution in real-time and provides updates"""
    
    def __init__(self):
        self.active_sessions: Dict[str, CrewExecutionState] = {}
        self.websocket_connections: Set = set()
        self.execution_logs: Dict[str, List[Dict]] = {}
        
    def start_session(self, session_id: str, query: str, agent_names: List[str]) -> CrewExecutionState:
        """Start tracking a new CrewAI execution session"""
        agents = []
        for name in agent_names:
            activity = AgentActivity(
                agent_id=f"agent_{len(agents)}",
                agent_name=name,
                status=AgentStatus.IDLE
            )
            agents.append(activity)
        
        state = CrewExecutionState(
            session_id=session_id,
            query=query,
            total_agents=len(agent_names),
            active_agents=agents,
            current_phase="agent_initialization"
        )
        
        self.active_sessions[session_id] = state
        self.execution_logs[session_id] = []
        
        # Broadcast session start (handle no event loop gracefully for testing)
        try:
            asyncio.create_task(self._broadcast_update(session_id, "session_started"))
        except RuntimeError:
            # No event loop running (likely in tests)
            pass
        
        logger.info(f"Started tracking session {session_id} with {len(agent_names)} agents")
        return state
    
    def update_agent_status(self, session_id: str, agent_name: str, 
                           status: AgentStatus, task: str = None, 
                           progress: float = None, details: str = None):
        """Update status of a specific agent"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found for agent update")
            return
        
        state = self.active_sessions[session_id]
        
        # Find and update agent
        for agent in state.active_agents:
            if agent.agent_name == agent_name:
                agent.status = status
                agent.updated_at = time.time()
                
                if task:
                    agent.current_task = task
                if progress is not None:
                    agent.progress = progress
                if details:
                    agent.details = details
                
                # Mark as completed if finished
                if status == AgentStatus.FINISHED and agent_name not in state.completed_agents:
                    state.completed_agents.append(agent_name)
                
                break
        
        # Update overall progress
        self._update_overall_progress(state)
        
        # Log the update
        self._log_agent_activity(session_id, agent_name, status, task, details)
        
        # Broadcast update (handle no event loop gracefully for testing)
        try:
            asyncio.create_task(self._broadcast_update(session_id, "agent_status_update"))
        except RuntimeError:
            # No event loop running (likely in tests)
            pass
    
    def update_crew_phase(self, session_id: str, phase: str, details: str = None):
        """Update the current execution phase"""
        if session_id not in self.active_sessions:
            return
        
        state = self.active_sessions[session_id]
        state.current_phase = phase
        
        self._log_crew_activity(session_id, f"Phase: {phase}", details)
        try:
            asyncio.create_task(self._broadcast_update(session_id, "phase_update"))
        except RuntimeError:
            # No event loop running (likely in tests)
            pass
    
    def add_crew_output(self, session_id: str, output_type: str, content: str, 
                       agent_name: str = None):
        """Add CrewAI output for display"""
        if session_id not in self.active_sessions:
            return
        
        state = self.active_sessions[session_id]
        output_entry = {
            "timestamp": time.time(),
            "type": output_type,
            "content": content,
            "agent": agent_name
        }
        
        state.crew_output.append(output_entry)
        
        # Keep only last 50 outputs to prevent memory issues
        if len(state.crew_output) > 50:
            state.crew_output = state.crew_output[-50:]
        
        self._log_crew_activity(session_id, f"{output_type}: {content[:100]}...", agent_name)
        try:
            asyncio.create_task(self._broadcast_update(session_id, "crew_output"))
        except RuntimeError:
            # No event loop running (likely in tests)
            pass
    
    def complete_session(self, session_id: str, final_result: str = None):
        """Mark session as completed"""
        if session_id not in self.active_sessions:
            return
        
        state = self.active_sessions[session_id]
        state.current_phase = "completed"
        state.overall_progress = 100.0
        
        # Mark all agents as finished
        for agent in state.active_agents:
            if agent.status != AgentStatus.FINISHED:
                agent.status = AgentStatus.FINISHED
                agent.progress = 100.0
        
        if final_result:
            self.add_crew_output(session_id, "final_result", final_result)
        
        self._log_crew_activity(session_id, "Session completed", final_result)
        try:
            asyncio.create_task(self._broadcast_update(session_id, "session_completed"))
        except RuntimeError:
            # No event loop running (likely in tests)
            pass
        
        logger.info(f"Completed tracking session {session_id}")
    
    def error_session(self, session_id: str, error_message: str, agent_name: str = None):
        """Mark session as errored"""
        if session_id not in self.active_sessions:
            return
        
        state = self.active_sessions[session_id]
        state.current_phase = "error"
        
        # Mark specific agent or all agents as error
        if agent_name:
            for agent in state.active_agents:
                if agent.agent_name == agent_name:
                    agent.status = AgentStatus.ERROR
                    agent.details = error_message
                    break
        else:
            for agent in state.active_agents:
                agent.status = AgentStatus.ERROR
        
        self._log_crew_activity(session_id, f"Error: {error_message}", agent_name)
        try:
            asyncio.create_task(self._broadcast_update(session_id, "session_error"))
        except RuntimeError:
            # No event loop running (likely in tests)
            pass
    
    def get_session_state(self, session_id: str) -> Optional[CrewExecutionState]:
        """Get current state of a session"""
        return self.active_sessions.get(session_id)
    
    def get_session_logs(self, session_id: str) -> List[Dict]:
        """Get execution logs for a session"""
        return self.execution_logs.get(session_id, [])
    
    def cleanup_session(self, session_id: str):
        """Clean up completed session data"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Keep logs for a bit longer for debugging
        # Could implement a TTL cleanup later
    
    def _update_overall_progress(self, state: CrewExecutionState):
        """Calculate overall progress based on agent progress"""
        if not state.active_agents:
            state.overall_progress = 0.0
            return
        
        total_progress = sum(agent.progress for agent in state.active_agents)
        state.overall_progress = total_progress / len(state.active_agents)
        
        # Estimate completion time based on progress
        if state.overall_progress > 0:
            elapsed = time.time() - state.started_at
            estimated_total = elapsed / (state.overall_progress / 100.0)
            state.estimated_completion = state.started_at + estimated_total
    
    def _log_agent_activity(self, session_id: str, agent_name: str, status: AgentStatus,
                           task: str = None, details: str = None):
        """Log agent activity"""
        log_entry = {
            "timestamp": time.time(),
            "type": "agent_activity",
            "agent": agent_name,
            "status": status.value,
            "task": task,
            "details": details
        }
        
        if session_id in self.execution_logs:
            self.execution_logs[session_id].append(log_entry)
    
    def _log_crew_activity(self, session_id: str, message: str, details: str = None):
        """Log crew-level activity"""
        log_entry = {
            "timestamp": time.time(),
            "type": "crew_activity", 
            "message": message,
            "details": details
        }
        
        if session_id in self.execution_logs:
            self.execution_logs[session_id].append(log_entry)
    
    async def _broadcast_update(self, session_id: str, update_type: str):
        """Broadcast update to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
        
        state = self.active_sessions.get(session_id)
        if not state:
            return
        
        # Convert to serializable format
        update_data = {
            "type": update_type,
            "session_id": session_id,
            "timestamp": time.time(),
            "state": {
                "session_id": state.session_id,
                "query": state.query,
                "total_agents": state.total_agents,
                "active_agents": [
                    {
                        "agent_id": agent.agent_id,
                        "agent_name": agent.agent_name,
                        "status": agent.status.value,
                        "current_task": agent.current_task,
                        "progress": agent.progress,
                        "details": agent.details,
                        "started_at": agent.started_at,
                        "updated_at": agent.updated_at
                    } for agent in state.active_agents
                ],
                "completed_agents": state.completed_agents,
                "current_phase": state.current_phase,
                "overall_progress": state.overall_progress,
                "started_at": state.started_at,
                "estimated_completion": state.estimated_completion,
                "crew_output": state.crew_output[-5:] if state.crew_output else []  # Last 5 outputs
            }
        }
        
        message = json.dumps(update_data)
        
        # Send to all connected clients
        dead_connections = set()
        for websocket in self.websocket_connections.copy():
            try:
                # Check if WebSocket is still open before sending
                if hasattr(websocket, 'client_state') and websocket.client_state.name != 'CONNECTED':
                    dead_connections.add(websocket)
                    continue
                    
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket update: {e}")
                dead_connections.add(websocket)
        
        # Remove dead connections
        self.websocket_connections -= dead_connections
    
    def add_websocket_connection(self, websocket):
        """Add WebSocket connection for real-time updates"""
        self.websocket_connections.add(websocket)
        logger.info(f"Added WebSocket connection. Total connections: {len(self.websocket_connections)}")
    
    def remove_websocket_connection(self, websocket):
        """Remove WebSocket connection"""
        self.websocket_connections.discard(websocket)
        logger.info(f"Removed WebSocket connection. Total connections: {len(self.websocket_connections)}")
    
    def get_active_sessions_summary(self) -> Dict:
        """Get summary of all active sessions"""
        return {
            "total_sessions": len(self.active_sessions),
            "sessions": [
                {
                    "session_id": session_id,
                    "phase": state.current_phase,
                    "progress": state.overall_progress,
                    "agents": len(state.active_agents),
                    "started_at": state.started_at
                }
                for session_id, state in self.active_sessions.items()
            ]
        }

# Global tracker instance
realtime_tracker = RealtimeAgentTracker()