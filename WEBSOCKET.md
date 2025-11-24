# AgentCraft WebSocket Protocol

Complete documentation for WebSocket-based real-time communication in AgentCraft.

## Table of Contents

1. [Overview](#overview)
2. [Connection Lifecycle](#connection-lifecycle)
3. [Message Types](#message-types)
4. [Event Handling](#event-handling)
5. [Reconnection Strategies](#reconnection-strategies)
6. [Client Implementation](#client-implementation)
7. [Server Implementation](#server-implementation)
8. [Best Practices](#best-practices)

---

## Overview

AgentCraft uses WebSocket for real-time bidirectional communication between the frontend and backend, enabling live agent status updates, execution tracking, and interactive debugging.

### WebSocket Architecture

```
┌──────────────────┐                    ┌──────────────────┐
│  React Frontend  │◄──────WebSocket───►│  FastAPI Backend │
│                  │                    │                  │
│  - Agent UI      │                    │  - WebSocket Mgr │
│  - Status Display│                    │  - Agent Tracker │
│  - Log Viewer    │                    │  - Log Streamer  │
└──────────────────┘                    └──────────────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌──────────────────┐                    ┌──────────────────┐
│  State Updates   │                    │  Agent Events    │
│  - Agent Status  │                    │  - PROCESSING    │
│  - Progress Bars │                    │  - COLLABORATING │
│  - Active Tasks  │                    │  - COMPLETED     │
└──────────────────┘                    └──────────────────┘
```

### Key Features

- **Real-time Agent Status**: Live updates on agent execution
- **Progress Tracking**: Real-time progress bars and percentages
- **Log Streaming**: Live CrewAI execution logs
- **Session Monitoring**: Track active sessions and agents
- **Automatic Reconnection**: Resilient connection management
- **Heartbeat Protocol**: Keep-alive ping/pong mechanism

### Endpoint

```
ws://localhost:8000/ws/agent-tracking/{client_id}
```

---

## Connection Lifecycle

### 1. Connection Establishment

```javascript
// Client initiates connection
const clientId = generateClientId();
const ws = new WebSocket(`ws://localhost:8000/ws/agent-tracking/${clientId}`);

ws.onopen = () => {
    console.log('WebSocket connected');
    // Connection established, server sends active sessions
};
```

```python
# Server accepts connection
@router.websocket("/agent-tracking/{client_id}")
async def websocket_agent_tracking(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    # Send current active sessions
    await ws_manager._send_active_sessions(client_id)
```

### 2. Active Communication

```
Client                          Server
  │                               │
  │──────── Connection ──────────►│
  │                               │
  │◄────── Active Sessions ───────│
  │                               │
  │──── get_session_state ───────►│
  │                               │
  │◄────── Session State ─────────│
  │                               │
  │◄── Agent Status Updates ──────│ (continuous)
  │                               │
```

### 3. Heartbeat Protocol

```javascript
// Server sends periodic pings
{
    "type": "ping",
    "timestamp": 1642678200.123
}

// Client responds with pong
ws.send(JSON.stringify({
    "type": "pong"
}));
```

### 4. Disconnection

```javascript
ws.onclose = (event) => {
    console.log('WebSocket closed:', event.reason);
    // Attempt reconnection
    setTimeout(() => reconnect(), 3000);
};
```

```python
# Server handles disconnection
except WebSocketDisconnect:
    await ws_manager.disconnect(client_id)
    # Clean up resources
```

---

## Message Types

### Server to Client Messages

#### 1. Active Sessions

Sent immediately on connection and when sessions change.

```json
{
    "type": "active_sessions",
    "timestamp": 1642678200.123,
    "data": {
        "total_sessions": 3,
        "sessions": [
            {
                "session_id": "session_abc123",
                "query": "How do I fix webhook errors?",
                "status": "processing",
                "agents_active": 2
            }
        ]
    }
}
```

#### 2. Agent Status Update

Real-time agent execution status.

```json
{
    "type": "agent_status",
    "agent_id": "agent-uuid",
    "agent_name": "Technical Integration Specialist",
    "status": "PROCESSING",
    "progress": 65,
    "message": "Analyzing webhook signature validation...",
    "timestamp": "2024-01-20T10:30:45.123Z",
    "metadata": {
        "task_id": "task-uuid",
        "estimated_completion": 30
    }
}
```

**Status Values:**
- `IDLE` - Agent not active
- `ANALYZING` - Analyzing query
- `PROCESSING` - Executing task
- `COLLABORATING` - Working with other agents
- `COMPLETED` - Task finished
- `ERROR` - Error occurred

#### 3. Agent Collaboration

Notification when agents collaborate.

```json
{
    "type": "agent_collaboration",
    "primary_agent": "Technical Integration Specialist",
    "secondary_agent": "Security Specialist",
    "collaboration_type": "handoff",
    "reason": "Requires security expertise",
    "timestamp": "2024-01-20T10:31:15.456Z"
}
```

#### 4. Session State

Complete session state snapshot.

```json
{
    "type": "session_state",
    "session_id": "session_abc123",
    "state": {
        "session_id": "session_abc123",
        "query": "How do I fix webhook errors?",
        "current_phase": "processing",
        "overall_progress": 65,
        "active_agents": [
            {
                "agent_name": "Technical Integration Specialist",
                "status": "PROCESSING",
                "progress": 75,
                "current_task": "Analyzing webhook configuration",
                "details": {}
            }
        ],
        "crew_output": [...]
    },
    "timestamp": 1642678200.123
}
```

#### 5. Session Logs

Execution logs for a session.

```json
{
    "type": "session_logs",
    "session_id": "session_abc123",
    "logs": [
        {
            "timestamp": "2024-01-20T10:30:00Z",
            "level": "info",
            "agent": "Technical Integration Specialist",
            "message": "Starting webhook analysis",
            "details": {}
        }
    ],
    "timestamp": 1642678200.123
}
```

#### 6. Ping (Heartbeat)

Keep-alive message.

```json
{
    "type": "ping",
    "timestamp": 1642678200.123
}
```

### Client to Server Messages

#### 1. Get Session Logs

Request execution logs for a session.

```json
{
    "type": "get_session_logs",
    "session_id": "session_abc123"
}
```

#### 2. Get Session State

Request current state of a session.

```json
{
    "type": "get_session_state",
    "session_id": "session_abc123"
}
```

#### 3. Start Log Streaming

Enable live log streaming.

```json
{
    "type": "start_log_streaming",
    "session_id": "session_abc123"
}
```

#### 4. Stop Log Streaming

Disable log streaming.

```json
{
    "type": "stop_log_streaming"
}
```

#### 5. Pong (Heartbeat Response)

Response to server ping.

```json
{
    "type": "pong"
}
```

---

## Event Handling

### Frontend Event Handlers

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent-tracking/client-123');

ws.onopen = () => {
    console.log('Connected to agent tracking');
    setConnectionStatus('connected');
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    switch (message.type) {
        case 'active_sessions':
            handleActiveSessions(message.data);
            break;

        case 'agent_status':
            updateAgentStatus(message);
            break;

        case 'agent_collaboration':
            showCollaboration(message);
            break;

        case 'session_state':
            updateSessionState(message.state);
            break;

        case 'session_logs':
            displayLogs(message.logs);
            break;

        case 'ping':
            ws.send(JSON.stringify({ type: 'pong' }));
            break;

        default:
            console.warn('Unknown message type:', message.type);
    }
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    setConnectionStatus('error');
};

ws.onclose = () => {
    console.log('WebSocket closed');
    setConnectionStatus('disconnected');
    attemptReconnect();
};
```

### Handler Implementations

```javascript
function handleActiveSessions(data) {
    setActiveSessions(data.sessions);
    setTotalSessions(data.total_sessions);
}

function updateAgentStatus(message) {
    setAgentStatuses(prev => ({
        ...prev,
        [message.agent_id]: {
            name: message.agent_name,
            status: message.status,
            progress: message.progress,
            message: message.message,
            timestamp: message.timestamp
        }
    }));
}

function showCollaboration(message) {
    const notification = `${message.primary_agent} → ${message.secondary_agent}: ${message.reason}`;
    showNotification(notification, 'info');
}

function updateSessionState(state) {
    setCurrentSession(state);
    setActiveAgents(state.active_agents);
    setOverallProgress(state.overall_progress);
}

function displayLogs(logs) {
    setSessionLogs(prev => [...prev, ...logs]);
    // Auto-scroll to bottom
    logsContainerRef.current?.scrollTo(0, logsContainerRef.current.scrollHeight);
}
```

---

## Reconnection Strategies

### Exponential Backoff

```javascript
class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.baseDelay = 1000;
        this.maxDelay = 30000;
    }

    connect(clientId) {
        this.ws = new WebSocket(`${this.url}/${clientId}`);
        this.setupEventHandlers();
    }

    attemptReconnect(clientId) {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.onMaxReconnectFailed?.();
            return;
        }

        this.reconnectAttempts++;

        // Exponential backoff with max delay
        const delay = Math.min(
            this.baseDelay * Math.pow(2, this.reconnectAttempts),
            this.maxDelay
        );

        console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

        setTimeout(() => {
            console.log('Attempting to reconnect...');
            this.connect(clientId);
        }, delay);
    }

    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0; // Reset on successful connection
            this.onConnected?.();
        };

        this.ws.onclose = () => {
            console.log('WebSocket closed');
            this.onDisconnected?.();
            this.attemptReconnect(this.clientId);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.onError?.(error);
        };

        this.ws.onmessage = (event) => {
            this.handleMessage(JSON.parse(event.data));
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}
```

### Connection State Management

```javascript
const [connectionState, setConnectionState] = useState({
    status: 'disconnected', // 'connecting', 'connected', 'disconnected', 'error'
    reconnectAttempts: 0,
    lastConnected: null,
    lastError: null
});

function updateConnectionState(status, extra = {}) {
    setConnectionState(prev => ({
        ...prev,
        status,
        ...extra,
        ...(status === 'connected' && { lastConnected: new Date() })
    }));
}
```

### User Feedback

```javascript
function ConnectionStatusIndicator() {
    const { connectionState } = useWebSocket();

    const statusConfig = {
        connected: {
            color: 'green',
            icon: '🟢',
            text: 'Connected'
        },
        connecting: {
            color: 'yellow',
            icon: '🟡',
            text: 'Connecting...'
        },
        disconnected: {
            color: 'gray',
            icon: '⚫',
            text: 'Disconnected'
        },
        error: {
            color: 'red',
            icon: '🔴',
            text: 'Connection Error'
        }
    };

    const config = statusConfig[connectionState.status];

    return (
        <div className={`connection-status ${config.color}`}>
            <span>{config.icon}</span>
            <span>{config.text}</span>
            {connectionState.reconnectAttempts > 0 && (
                <span className="reconnect-count">
                    (Attempt {connectionState.reconnectAttempts})
                </span>
            )}
        </div>
    );
}
```

---

## Client Implementation

### React Hook for WebSocket

```javascript
import { useState, useEffect, useCallback, useRef } from 'react';

export function useAgentWebSocket(clientId) {
    const [isConnected, setIsConnected] = useState(false);
    const [agentStatuses, setAgentStatuses] = useState({});
    const [activeSessions, setActiveSessions] = useState([]);
    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);

    const connect = useCallback(() => {
        const ws = new WebSocket(
            `ws://localhost:8000/ws/agent-tracking/${clientId}`
        );

        ws.onopen = () => {
            console.log('WebSocket connected');
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);

            switch (message.type) {
                case 'agent_status':
                    setAgentStatuses(prev => ({
                        ...prev,
                        [message.agent_id]: {
                            name: message.agent_name,
                            status: message.status,
                            progress: message.progress,
                            message: message.message
                        }
                    }));
                    break;

                case 'active_sessions':
                    setActiveSessions(message.data.sessions);
                    break;

                case 'ping':
                    ws.send(JSON.stringify({ type: 'pong' }));
                    break;
            }
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            setIsConnected(false);

            // Attempt reconnection after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
                connect();
            }, 3000);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        wsRef.current = ws;
    }, [clientId]);

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    const sendMessage = useCallback((message) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        }
    }, []);

    return {
        isConnected,
        agentStatuses,
        activeSessions,
        sendMessage
    };
}
```

### Usage in Component

```javascript
function AgentDashboard() {
    const clientId = useMemo(() => `client_${Date.now()}`, []);
    const { isConnected, agentStatuses, sendMessage } = useAgentWebSocket(clientId);

    const requestSessionState = (sessionId) => {
        sendMessage({
            type: 'get_session_state',
            session_id: sessionId
        });
    };

    return (
        <div>
            <ConnectionStatus connected={isConnected} />

            <div className="agents-grid">
                {Object.entries(agentStatuses).map(([id, agent]) => (
                    <AgentCard
                        key={id}
                        name={agent.name}
                        status={agent.status}
                        progress={agent.progress}
                        message={agent.message}
                    />
                ))}
            </div>
        </div>
    );
}
```

---

## Server Implementation

### WebSocket Manager

```python
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

        # Send current active sessions
        await self._send_active_sessions(client_id)

    async def disconnect(self, client_id: str):
        """Handle WebSocket disconnection"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            realtime_tracker.remove_websocket_connection(websocket)

            del self.active_connections[client_id]
            del self.connection_metadata[client_id]

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
                await websocket.send_text(json.dumps(message))
                self.connection_metadata[client_id]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                dead_connections.append(client_id)

        # Clean up dead connections
        for client_id in dead_connections:
            await self.disconnect(client_id)
```

### WebSocket Endpoint

```python
@router.websocket("/agent-tracking/{client_id}")
async def websocket_agent_tracking(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time agent tracking"""
    await ws_manager.connect(websocket, client_id)

    try:
        while True:
            try:
                # Receive client messages with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
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
```

### Broadcasting Agent Updates

```python
async def broadcast_agent_status(agent_id: str, agent_name: str, status: str, progress: int, message: str):
    """Broadcast agent status to all connected clients"""

    update_message = {
        "type": "agent_status",
        "agent_id": agent_id,
        "agent_name": agent_name,
        "status": status,
        "progress": progress,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

    await ws_manager.broadcast(update_message)
```

---

## Best Practices

### 1. Connection Management

**Generate unique client IDs:**
```javascript
const generateClientId = () => {
    return `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};
```

**Clean up on unmount:**
```javascript
useEffect(() => {
    const ws = connectWebSocket();

    return () => {
        ws.close();
    };
}, []);
```

### 2. Error Handling

**Handle all connection states:**
```javascript
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    showUserNotification('Connection error. Retrying...');
};

ws.onclose = (event) => {
    if (event.wasClean) {
        console.log('Clean disconnect');
    } else {
        console.error('Connection died');
        attemptReconnect();
    }
};
```

### 3. Message Validation

**Validate incoming messages:**
```javascript
function isValidMessage(message) {
    return message &&
           typeof message === 'object' &&
           'type' in message &&
           typeof message.type === 'string';
}

ws.onmessage = (event) => {
    try {
        const message = JSON.parse(event.data);

        if (!isValidMessage(message)) {
            console.warn('Invalid message format:', message);
            return;
        }

        handleMessage(message);
    } catch (error) {
        console.error('Error parsing message:', error);
    }
};
```

### 4. Performance Optimization

**Throttle status updates:**
```javascript
import { throttle } from 'lodash';

const updateAgentStatus = throttle((status) => {
    setAgentStatuses(prev => ({
        ...prev,
        ...status
    }));
}, 100); // Max 10 updates per second
```

**Batch message processing:**
```javascript
let messageQueue = [];
let processingTimer = null;

ws.onmessage = (event) => {
    messageQueue.push(JSON.parse(event.data));

    if (!processingTimer) {
        processingTimer = setTimeout(() => {
            processBatch(messageQueue);
            messageQueue = [];
            processingTimer = null;
        }, 50);
    }
};
```

### 5. Security

**Validate client IDs:**
```python
import re

def is_valid_client_id(client_id: str) -> bool:
    # Format: client_timestamp_randomstring
    pattern = r'^client_\d+_[a-z0-9]+$'
    return bool(re.match(pattern, client_id))

@router.websocket("/agent-tracking/{client_id}")
async def websocket_agent_tracking(websocket: WebSocket, client_id: str):
    if not is_valid_client_id(client_id):
        await websocket.close(code=1008, reason="Invalid client ID")
        return

    await ws_manager.connect(websocket, client_id)
```

**Rate limiting:**
```python
from collections import defaultdict
import time

message_timestamps = defaultdict(list)
MAX_MESSAGES_PER_MINUTE = 60

async def handle_client_message(message: dict, client_id: str):
    # Rate limiting
    now = time.time()
    timestamps = message_timestamps[client_id]

    # Remove old timestamps
    timestamps[:] = [t for t in timestamps if now - t < 60]

    if len(timestamps) >= MAX_MESSAGES_PER_MINUTE:
        logger.warning(f"Rate limit exceeded for {client_id}")
        return

    timestamps.append(now)

    # Process message
    # ...
```

---

## Related Documentation

- [API.md](API.md) - REST API endpoints for WebSocket stats
- [FRONTEND.md](FRONTEND.md) - Frontend WebSocket integration
- [SERVICES.md](SERVICES.md) - Backend services
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - WebSocket connection issues
