# AgentCraft Conversation Memory System

Complete documentation for the conversation memory and context management system.

## Table of Contents

1. [Overview](#overview)
2. [ConversationMemory Class](#conversationmemory-class)
3. [Session Management](#session-management)
4. [Context Window Management](#context-window-management)
5. [Message Storage](#message-storage)
6. [API Integration](#api-integration)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

---

## Overview

AgentCraft's conversation memory system provides persistent context across multiple interactions, enabling natural multi-turn conversations and context-aware responses.

### Key Features

- **Persistent Memory**: Conversations maintained across sessions
- **Smart Context Management**: Automatic context window optimization
- **Session Tracking**: Unique session IDs for conversation continuity
- **Context Injection**: Seamless integration of previous messages
- **Memory Optimization**: Automatic truncation and relevance filtering

### Architecture

```
Conversation Memory System
├── ConversationMemory Class (backend/main.py)
│   ├── Session Storage
│   ├── Message Management
│   ├── Context Extraction
│   └── Memory Optimization
├── Session Management
│   ├── Session ID Generation
│   ├── Session Tracking
│   └── Session Cleanup
└── Context Window
    ├── Last N Messages
    ├── Role-based Filtering
    └── Content Truncation
```

---

## ConversationMemory Class

### Location

`backend/main.py` (lines 23-67)

### Purpose

Manages conversation history, context extraction, and memory optimization for all agent interactions.

### Class Definition

```python
class ConversationMemory:
    def __init__(self):
        self.conversations = {}  # {session_id: [messages]}

    def add_message(self, session_id: str, role: str, message: str, agent_type: str = None)
    def get_conversation_context(self, session_id: str) -> str
    def get_conversation_summary(self, session_id: str) -> dict
```

### Data Structure

```python
# Conversation storage format
{
    "session_uuid": [
        {
            "role": "user",
            "content": "How do I verify webhook signatures?",
            "timestamp": "2024-01-20T10:30:00.000000",
            "agent_type": None
        },
        {
            "role": "assistant",
            "content": "To verify webhook signatures...",
            "timestamp": "2024-01-20T10:30:02.500000",
            "agent_type": "Technical Integration Specialist"
        }
    ]
}
```

---

## Session Management

### Session ID Generation

Session IDs are generated client-side for immediate availability:

```javascript
// Frontend session ID generation
const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// Example: "session_1705750200123_k7m9p3x2q"
```

### Session Lifecycle

```
1. User starts conversation → Generate session ID
2. First message sent → Create session in memory
3. Subsequent messages → Add to existing session
4. Context retrieval → Last 6 messages used
5. Session cleanup → Automatically after 10+ messages
```

### Session Storage

```python
# Global conversation memory instance
conversation_memory = ConversationMemory()

# Sessions stored in memory
conversation_store = {}  # Alternative storage

# Access conversation
if session_id in conversation_memory.conversations:
    messages = conversation_memory.conversations[session_id]
```

---

## Context Window Management

### Context Extraction

The system maintains context from recent conversation history:

```python
def get_conversation_context(self, session_id: str) -> str:
    """Extract relevant context from conversation history"""

    if session_id not in self.conversations:
        return ""

    context_messages = []
    for msg in self.conversations[session_id]:
        if msg["role"] == "user":
            context_messages.append(f"User: {msg['content']}")
        elif msg["role"] == "assistant":
            agent_info = f" ({msg.get('agent_type', 'AI')})" if msg.get('agent_type') else ""
            # Truncate assistant responses to 200 chars for context
            context_messages.append(f"Assistant{agent_info}: {msg['content'][:200]}...")

    # Return last 6 messages for context
    return "\n".join(context_messages[-6:])
```

### Context Window Parameters

```python
CONTEXT_WINDOW = 6          # Last 6 messages used for context
MAX_MESSAGES_STORED = 10    # Maximum messages stored per session
ASSISTANT_PREVIEW = 200     # Characters from assistant response
```

### Memory Optimization

Automatic truncation prevents memory bloat:

```python
def add_message(self, session_id: str, role: str, message: str, agent_type: str = None):
    if session_id not in self.conversations:
        self.conversations[session_id] = []

    message_entry = {
        "role": role,
        "content": message,
        "timestamp": datetime.utcnow().isoformat(),
        "agent_type": agent_type
    }

    self.conversations[session_id].append(message_entry)

    # Keep only the last 10 messages per conversation
    if len(self.conversations[session_id]) > 10:
        self.conversations[session_id] = self.conversations[session_id][-10:]
```

---

## Message Storage

### Adding Messages

```python
# Add user message
conversation_memory.add_message(
    session_id="session_12345",
    role="user",
    message="How do I fix webhook signature errors?"
)

# Add assistant message with agent type
conversation_memory.add_message(
    session_id="session_12345",
    role="assistant",
    message="To fix webhook signature errors, you should...",
    agent_type="Technical Integration Specialist"
)
```

### Message Format

```python
{
    "role": "user" | "assistant",
    "content": str,  # Full message content
    "timestamp": str,  # ISO 8601 format
    "agent_type": str | None  # Agent name if assistant
}
```

### Retrieving Messages

```python
# Get full conversation
messages = conversation_memory.conversations.get(session_id, [])

# Get context summary
context = conversation_memory.get_conversation_context(session_id)

# Get conversation metadata
summary = conversation_memory.get_conversation_summary(session_id)
# Returns:
{
    "message_count": 6,
    "last_activity": "2024-01-20T10:35:00.000000",
    "session_started": "2024-01-20T10:30:00.000000"
}
```

---

## API Integration

### Query Processing with Context

```python
@app.post("/api/multi-agent/query")
async def process_multi_agent_query(request: dict):
    query = request.get("query")
    session_id = request.get("session_id")

    # Add user message to conversation
    conversation_memory.add_message(
        session_id=session_id,
        role="user",
        message=query
    )

    # Get conversation context
    context = conversation_memory.get_conversation_context(session_id)

    # Process with context
    enhanced_query = f"""
Previous conversation:
{context}

Current question: {query}
"""

    # Get AI response
    response = await process_with_ai(enhanced_query)

    # Store assistant response
    conversation_memory.add_message(
        session_id=session_id,
        role="assistant",
        message=response['content'],
        agent_type=response.get('agent_name')
    )

    return response
```

### REST Endpoints

#### Get Conversation History

```http
GET /api/conversation/{session_id}
```

**Response:**
```json
{
    "success": true,
    "session_id": "session_12345",
    "messages": [
        {
            "role": "user",
            "content": "How do I validate webhook signatures?",
            "timestamp": "2024-01-20T10:30:00Z"
        },
        {
            "role": "assistant",
            "content": "Here's how to validate webhook signatures...",
            "timestamp": "2024-01-20T10:30:02Z",
            "agent": "Technical Integration Specialist",
            "citations": [...]
        }
    ],
    "agents_used": ["Technical Integration Specialist"],
    "created_at": "2024-01-20T10:30:00Z",
    "message_count": 6
}
```

#### List Active Conversations

```http
GET /api/conversations?limit=50&offset=0
```

**Response:**
```json
{
    "success": true,
    "sessions": [
        {
            "session_id": "session_12345",
            "query": "First message...",
            "created_at": "2024-01-20T10:00:00Z",
            "last_activity": "2024-01-20T10:30:00Z",
            "message_count": 8,
            "agents_used": ["Technical Integration Specialist"]
        }
    ],
    "total_sessions": 156,
    "limit": 50,
    "offset": 0
}
```

---

## Best Practices

### 1. Session Management

**Generate unique session IDs:**
```javascript
// Client-side
const sessionId = generateSessionId();
localStorage.setItem('agentcraft_session', sessionId);

// Reuse session ID for conversation continuity
const savedSession = localStorage.getItem('agentcraft_session');
```

**Create new sessions appropriately:**
```javascript
// New session for new topics
if (userStartsNewTopic) {
    sessionId = generateSessionId();
}

// Keep session for follow-up questions
if (isFollowUpQuestion) {
    // Use existing sessionId
}
```

### 2. Context Utilization

**Leverage context for better responses:**
```python
# Always retrieve context before processing
context = conversation_memory.get_conversation_context(session_id)

# Include context in AI prompt
prompt = f"""
Conversation history:
{context}

User's current question: {query}

Please provide a contextually aware response.
"""
```

**Reference previous messages:**
```python
# Check if query references previous context
if "that" in query.lower() or "it" in query.lower():
    # User likely referring to previous discussion
    context_important = True
```

### 3. Memory Management

**Clean up old sessions:**
```python
from datetime import datetime, timedelta

def cleanup_old_sessions():
    """Remove sessions older than 24 hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=24)

    for session_id in list(conversation_memory.conversations.keys()):
        summary = conversation_memory.get_conversation_summary(session_id)
        last_activity = datetime.fromisoformat(summary['last_activity'])

        if last_activity < cutoff_time:
            del conversation_memory.conversations[session_id]
```

**Monitor memory usage:**
```python
def get_memory_stats():
    total_sessions = len(conversation_memory.conversations)
    total_messages = sum(
        len(messages)
        for messages in conversation_memory.conversations.values()
    )

    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "avg_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0
    }
```

### 4. Error Handling

**Handle missing sessions gracefully:**
```python
def safe_get_context(session_id: str) -> str:
    try:
        return conversation_memory.get_conversation_context(session_id)
    except KeyError:
        logging.warning(f"Session not found: {session_id}")
        return ""
    except Exception as e:
        logging.error(f"Error retrieving context: {e}")
        return ""
```

**Validate session IDs:**
```python
import re

def is_valid_session_id(session_id: str) -> bool:
    # Format: session_timestamp_randomstring
    pattern = r'^session_\d+_[a-z0-9]+$'
    return bool(re.match(pattern, session_id))
```

### 5. Performance Optimization

**Use efficient data structures:**
```python
# Good: Dictionary lookup O(1)
messages = conversation_memory.conversations[session_id]

# Bad: List search O(n)
# Don't store sessions in a list
```

**Limit context size:**
```python
# Truncate long messages
MAX_CONTEXT_LENGTH = 2000

context = conversation_memory.get_conversation_context(session_id)
if len(context) > MAX_CONTEXT_LENGTH:
    context = context[-MAX_CONTEXT_LENGTH:]
```

---

## Examples

### Example 1: Basic Conversation Flow

```python
# Initialize
from backend.main import conversation_memory

# User starts conversation
session_id = "session_1705750200_abc123"

# First message
conversation_memory.add_message(
    session_id=session_id,
    role="user",
    message="How do I set up webhooks?"
)

# Agent responds
conversation_memory.add_message(
    session_id=session_id,
    role="assistant",
    message="To set up webhooks, follow these steps...",
    agent_type="Technical Integration Specialist"
)

# Follow-up question (context-aware)
conversation_memory.add_message(
    session_id=session_id,
    role="user",
    message="What about signature verification?"
)

# Get context for processing
context = conversation_memory.get_conversation_context(session_id)
print(context)
# Output:
# User: How do I set up webhooks?
# Assistant (Technical Integration Specialist): To set up webhooks, follow these steps...
# User: What about signature verification?
```

### Example 2: Multi-Turn Conversation

```python
async def handle_conversation(session_id: str, query: str):
    """Handle a multi-turn conversation"""

    # Add user message
    conversation_memory.add_message(
        session_id=session_id,
        role="user",
        message=query
    )

    # Get context
    context = conversation_memory.get_conversation_context(session_id)

    # Check if this is a follow-up
    messages = conversation_memory.conversations.get(session_id, [])
    is_follow_up = len(messages) > 1

    # Build contextual prompt
    if is_follow_up:
        prompt = f"""
Previous conversation:
{context}

This is a follow-up question. Consider the previous context when answering.

User's question: {query}
"""
    else:
        prompt = query

    # Process with AI
    response = await process_with_ai(prompt)

    # Store response
    conversation_memory.add_message(
        session_id=session_id,
        role="assistant",
        message=response['content'],
        agent_type=response.get('agent')
    )

    return response
```

### Example 3: Context-Aware Response

```python
async def get_context_aware_response(session_id: str, query: str):
    """Generate context-aware response"""

    # Get conversation history
    context = conversation_memory.get_conversation_context(session_id)

    # Analyze if query references previous context
    reference_words = ["it", "that", "this", "they", "them", "those"]
    has_reference = any(word in query.lower().split() for word in reference_words)

    if has_reference and context:
        # User is likely referring to previous discussion
        prompt = f"""
Based on our previous conversation:
{context}

The user is now asking: {query}

This question seems to reference our previous discussion. Please provide a contextually appropriate response.
"""
    else:
        # Standalone question
        if context:
            prompt = f"""
Background from our conversation:
{context}

New question: {query}
"""
        else:
            prompt = query

    response = await ai_process(prompt)
    return response
```

### Example 4: Session Summary

```python
def get_conversation_insights(session_id: str):
    """Get insights from conversation"""

    summary = conversation_memory.get_conversation_summary(session_id)
    messages = conversation_memory.conversations.get(session_id, [])

    # Analyze conversation
    user_messages = [m for m in messages if m['role'] == 'user']
    assistant_messages = [m for m in messages if m['role'] == 'assistant']

    # Extract topics
    topics = set()
    for msg in user_messages:
        # Simple topic extraction (in production, use NLP)
        if 'webhook' in msg['content'].lower():
            topics.add('webhooks')
        if 'api' in msg['content'].lower():
            topics.add('api')
        if 'signature' in msg['content'].lower():
            topics.add('security')

    # Agent usage
    agents_used = set()
    for msg in assistant_messages:
        if msg.get('agent_type'):
            agents_used.add(msg['agent_type'])

    return {
        "session_id": session_id,
        "message_count": summary['message_count'],
        "duration": calculate_duration(summary),
        "topics": list(topics),
        "agents_used": list(agents_used),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages)
    }
```

### Example 5: Conversation Export

```python
def export_conversation(session_id: str, format: str = 'json'):
    """Export conversation in various formats"""

    messages = conversation_memory.conversations.get(session_id, [])

    if format == 'json':
        return json.dumps(messages, indent=2)

    elif format == 'markdown':
        md = f"# Conversation {session_id}\n\n"
        for msg in messages:
            role = "**User**" if msg['role'] == 'user' else "**Assistant**"
            if msg.get('agent_type'):
                role += f" ({msg['agent_type']})"
            md += f"{role}: {msg['content']}\n\n"
        return md

    elif format == 'text':
        txt = ""
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Assistant"
            txt += f"{role}: {msg['content']}\n\n"
        return txt
```

---

## Advanced Features

### Session Persistence

For production deployments, consider persistent storage:

```python
# Using Redis
import redis
import json

class PersistentConversationMemory:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.ttl = 86400  # 24 hours

    def add_message(self, session_id: str, role: str, message: str, agent_type: str = None):
        key = f"conversation:{session_id}"

        message_entry = {
            "role": role,
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_type": agent_type
        }

        # Get existing messages
        messages = self.get_messages(session_id)
        messages.append(message_entry)

        # Keep last 10
        messages = messages[-10:]

        # Store in Redis
        self.redis.setex(
            key,
            self.ttl,
            json.dumps(messages)
        )

    def get_messages(self, session_id: str):
        key = f"conversation:{session_id}"
        data = self.redis.get(key)
        return json.loads(data) if data else []
```

### Database Storage

```python
# Using PostgreSQL
from database.models import Conversation, Message

async def store_message_db(session_id: str, role: str, content: str, agent_type: str = None):
    """Store message in database"""

    # Get or create conversation
    conversation = await Conversation.get_or_create(session_id=session_id)

    # Create message
    message = await Message.create(
        conversation_id=conversation.id,
        role=role,
        content=content,
        agent_type=agent_type,
        timestamp=datetime.utcnow()
    )

    return message
```

---

## Related Documentation

- [API.md](API.md) - Conversation API endpoints
- [FRONTEND.md](FRONTEND.md) - Frontend conversation UI
- [WEBSOCKET.md](WEBSOCKET.md) - Real-time conversation updates
- [KNOWLEDGE_SYSTEM.md](KNOWLEDGE_SYSTEM.md) - Context enhancement with knowledge
