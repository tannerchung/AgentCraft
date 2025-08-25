"""
WebSocket API for Real-time Agent Tracking
Provides live updates of CrewAI agent execution to frontend
"""

import asyncio
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState

from src.agents.realtime_agent_tracker import realtime_tracker
from src.agents.crewai_log_streamer import crewai_log_streamer

logger = logging.getLogger(__name__)

# Create WebSocket router
router = APIRouter()

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "message_count": 0
        }
        
        # Add to realtime tracker
        realtime_tracker.add_websocket_connection(websocket)
        
        # Set up CrewAI log streaming for this connection
        crewai_log_streamer.set_websocket_manager(self)
        
        logger.info(f"WebSocket connected: {client_id}")
        
        # Send current active sessions
        await self._send_active_sessions(client_id)
    
    async def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            
            # Remove from realtime tracker
            realtime_tracker.remove_websocket_connection(websocket)
            
            # Clean up
            del self.active_connections[client_id]
            del self.connection_metadata[client_id]
            
            logger.info(f"WebSocket disconnected: {client_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(json.dumps(message))
                self.connection_metadata[client_id]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        dead_connections = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                # Check if WebSocket is still open before sending
                if hasattr(websocket, 'client_state') and websocket.client_state.name != 'CONNECTED':
                    dead_connections.append(client_id)
                    continue
                    
                await websocket.send_text(json.dumps(message))
                self.connection_metadata[client_id]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                dead_connections.append(client_id)
        
        # Clean up dead connections
        for client_id in dead_connections:
            await self.disconnect(client_id)
    
    async def _send_active_sessions(self, client_id: str):
        """Send current active sessions to newly connected client"""
        summary = realtime_tracker.get_active_sessions_summary()
        
        message = {
            "type": "active_sessions",
            "timestamp": asyncio.get_event_loop().time(),
            "data": summary
        }
        
        await self.send_personal_message(message, client_id)
    
    def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        total_messages = sum(
            meta["message_count"] for meta in self.connection_metadata.values()
        )
        
        return {
            "active_connections": len(self.active_connections),
            "total_messages_sent": total_messages,
            "connections": [
                {
                    "client_id": client_id,
                    "connected_at": meta["connected_at"],
                    "message_count": meta["message_count"]
                }
                for client_id, meta in self.connection_metadata.items()
            ]
        }

# Global WebSocket manager
ws_manager = WebSocketManager()

@router.websocket("/agent-tracking/{client_id}")
async def websocket_agent_tracking(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time agent tracking"""
    await ws_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle client commands
                await handle_client_message(message, client_id)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                ping_message = {
                    "type": "ping",
                    "timestamp": asyncio.get_event_loop().time()
                }
                await ws_manager.send_personal_message(ping_message, client_id)
                
    except WebSocketDisconnect:
        await ws_manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        await ws_manager.disconnect(client_id)

async def handle_client_message(message: dict, client_id: str):
    """Handle messages from WebSocket clients"""
    message_type = message.get("type")
    
    if message_type == "get_session_logs":
        session_id = message.get("session_id")
        if session_id:
            logs = realtime_tracker.get_session_logs(session_id)
            response = {
                "type": "session_logs",
                "session_id": session_id,
                "logs": logs[-50:],  # Last 50 logs
                "timestamp": asyncio.get_event_loop().time()
            }
            await ws_manager.send_personal_message(response, client_id)
    
    elif message_type == "get_session_state":
        session_id = message.get("session_id")
        if session_id:
            state = realtime_tracker.get_session_state(session_id)
            if state:
                response = {
                    "type": "session_state",
                    "session_id": session_id,
                    "state": {
                        "session_id": state.session_id,
                        "query": state.query,
                        "current_phase": state.current_phase,
                        "overall_progress": state.overall_progress,
                        "active_agents": [
                            {
                                "agent_name": agent.agent_name,
                                "status": agent.status.value,
                                "progress": agent.progress,
                                "current_task": agent.current_task,
                                "details": agent.details
                            }
                            for agent in state.active_agents
                        ],
                        "crew_output": state.crew_output[-10:]  # Last 10 outputs
                    },
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                response = {
                    "type": "session_not_found",
                    "session_id": session_id,
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            await ws_manager.send_personal_message(response, client_id)
    
    elif message_type == "start_log_streaming":
        session_id = message.get("session_id", "default")
        # Set session ID for log context
        crewai_log_streamer.set_session_id(session_id)
        
        response = {
            "type": "log_streaming_started",
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time(),
            "message": "CrewAI log streaming enabled"
        }
        await ws_manager.send_personal_message(response, client_id)
    
    elif message_type == "stop_log_streaming":
        # Clear session ID to stop contextual logging
        crewai_log_streamer.set_session_id(None)
        
        response = {
            "type": "log_streaming_stopped",
            "timestamp": asyncio.get_event_loop().time(),
            "message": "CrewAI log streaming disabled"
        }
        await ws_manager.send_personal_message(response, client_id)
    
    elif message_type == "pong":
        # Client responding to ping
        pass
    
    else:
        logger.warning(f"Unknown message type from {client_id}: {message_type}")

# Additional REST endpoints for WebSocket management
@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "success": True,
        "stats": ws_manager.get_connection_stats(),
        "realtime_sessions": realtime_tracker.get_active_sessions_summary()
    }

@router.post("/ws/broadcast")
async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    try:
        await ws_manager.broadcast(message)
        return {"success": True, "message": "Broadcast sent"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/ws/sessions/{session_id}/logs")
async def get_session_logs(session_id: str):
    """Get execution logs for a specific session"""
    logs = realtime_tracker.get_session_logs(session_id)
    return {
        "success": True,
        "session_id": session_id,
        "logs": logs,
        "total_logs": len(logs)
    }

@router.get("/ws/sessions/{session_id}/state")
async def get_session_state(session_id: str):
    """Get current state of a specific session"""
    state = realtime_tracker.get_session_state(session_id)
    
    if not state:
        return {
            "success": False,
            "error": "Session not found",
            "session_id": session_id
        }
    
    return {
        "success": True,
        "session_id": session_id,
        "state": {
            "session_id": state.session_id,
            "query": state.query,
            "total_agents": state.total_agents,
            "current_phase": state.current_phase,
            "overall_progress": state.overall_progress,
            "started_at": state.started_at,
            "estimated_completion": state.estimated_completion,
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
                }
                for agent in state.active_agents
            ],
            "completed_agents": state.completed_agents,
            "crew_output": state.crew_output
        }
    }