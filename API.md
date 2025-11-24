# AgentCraft API Reference

Complete API documentation for the AgentCraft multi-agent AI system.

## Base URL

```
Development: http://localhost:8000
Production: https://your-domain.com
```

## Table of Contents

1. [Authentication](#authentication)
2. [Agent Management](#agent-management)
3. [Query Processing](#query-processing)
4. [Knowledge Management](#knowledge-management)
5. [Conversation Management](#conversation-management)
6. [Efficiency & Optimization](#efficiency--optimization)
7. [WebSocket API](#websocket-api)
8. [Error Handling](#error-handling)

---

## Authentication

Currently, the API does not require authentication for development. For production deployment, implement API key-based or JWT authentication.

### Future Authentication Header

```http
Authorization: Bearer <your-api-key>
```

---

## Agent Management

### List All Agents

Get all active agents in the system.

**Endpoint:** `GET /api/agents/list`

**Response:**
```json
{
  "success": true,
  "agents": {
    "agent-uuid-1": {
      "id": "uuid",
      "name": "Technical Integration Specialist",
      "role": "API and webhook integration expert",
      "domain": "technical",
      "avatar": "⚙️",
      "color": "blue",
      "keywords": ["webhook", "api", "integration"],
      "specialization_score": 0.95,
      "collaboration_rating": 0.88,
      "is_active": true
    }
  },
  "total_agents": 22
}
```

### Create Agent

Create a new specialized agent.

**Endpoint:** `POST /api/agents/create`

**Request Body:**
```json
{
  "name": "Custom Security Analyst",
  "role": "Advanced cybersecurity analysis and threat detection",
  "domain": "security",
  "backstory": "Expert cybersecurity analyst with years of experience",
  "goal": "Identify security threats and provide actionable recommendations",
  "keywords": ["security", "vulnerability", "threat", "malware"],
  "avatar": "🔒",
  "color": "red",
  "llm_config": {
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.1
  },
  "tools": ["security_scanner", "vulnerability_detector"],
  "specialization_score": 0.9
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "new-agent-uuid",
  "message": "Agent created successfully"
}
```

### Update Agent

Update an existing agent's configuration.

**Endpoint:** `PUT /api/agents/{agent_id}`

**Request Body:**
```json
{
  "role": "Enhanced cybersecurity analysis with AI-powered threat detection",
  "keywords": ["security", "ai", "machine-learning", "threat-detection"],
  "specialization_score": 0.95,
  "llm_config": {
    "model": "gpt-4",
    "temperature": 0.05
  }
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "agent-uuid",
  "message": "Agent updated successfully"
}
```

### Delete Agent

Deactivate an agent (soft delete).

**Endpoint:** `DELETE /api/agents/{agent_id}`

**Response:**
```json
{
  "success": true,
  "agent_id": "agent-uuid",
  "message": "Agent deactivated successfully"
}
```

### Get Agent Metrics

Get performance metrics for a specific agent.

**Endpoint:** `GET /api/agents/{agent_id}/metrics`

**Response:**
```json
{
  "success": true,
  "agent_id": "agent-uuid",
  "metrics": {
    "total_interactions": 450,
    "avg_quality": 0.89,
    "avg_response_time_ms": 1850,
    "avg_user_rating": 4.3,
    "success_rate": 0.97,
    "avg_cost": 0.05
  }
}
```

### Hot Reload Agent

Reload a specific agent's configuration without restarting.

**Endpoint:** `POST /api/agents/{agent_id}/reload`

**Response:**
```json
{
  "success": true,
  "agent_id": "agent-uuid",
  "message": "Agent reloaded successfully"
}
```

### Get Agent System Status

Get overall agent system status.

**Endpoint:** `GET /api/agents/status`

**Response:**
```json
{
  "success": true,
  "total_agents": 22,
  "cache_stats": {
    "total_agents": 22,
    "cache_hits": 450,
    "cache_misses": 12
  },
  "agents_by_domain": {
    "technical": [
      {
        "name": "Technical Integration Specialist",
        "id": "uuid",
        "specialization_score": 0.95,
        "collaboration_rating": 0.88
      }
    ],
    "business": [...],
    "analysis": [...]
  },
  "database_connected": true,
  "memory_cached": true
}
```

### Refresh Agent Cache

Manually refresh the agent cache.

**Endpoint:** `POST /api/agents/cache/refresh`

**Response:**
```json
{
  "success": true,
  "message": "Agent cache refreshed",
  "agents_loaded": 22
}
```

---

## Query Processing

### Process Single Query

Process a query with automatic agent routing.

**Endpoint:** `POST /api/query`

**Request Body:**
```json
{
  "query": "How do I fix webhook signature validation errors?",
  "context": {
    "user_id": "user-123",
    "session_id": "session-456"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "Detailed technical response...",
  "routing_info": {
    "selected_agent": "Technical Integration Specialist",
    "confidence": 0.85,
    "routing_time": 0.05
  },
  "citations": [
    {
      "source": "Zapier Official Documentation",
      "url": "https://zapier.com/help/webhooks",
      "relevance": 0.92
    }
  ],
  "session_id": "session-uuid",
  "response_time_ms": 1500,
  "tokens_used": 2500,
  "cost": 0.05
}
```

### Multi-Agent Query Processing

Process query with multiple specialized agents.

**Endpoint:** `POST /api/multi-agent/query`

**Request Body:**
```json
{
  "query": "Analyze the security implications of our webhook implementation",
  "session_id": "session-uuid",
  "context": {
    "user_id": "user-123",
    "priority": "high"
  }
}
```

**Response:**
```json
{
  "success": true,
  "response": "Combined response from multiple agents...",
  "agents_used": [
    "Technical Integration Specialist",
    "Security Specialist",
    "Database Expert"
  ],
  "collaboration_log": [
    {
      "timestamp": "2024-01-20T10:30:00Z",
      "agent": "Technical Integration Specialist",
      "action": "initial_analysis",
      "output": "..."
    },
    {
      "timestamp": "2024-01-20T10:30:15Z",
      "agent": "Security Specialist",
      "action": "security_review",
      "output": "..."
    }
  ],
  "citations": [...],
  "performance": {
    "response_time_ms": 2500,
    "tokens_used": 4200,
    "cost": 0.08,
    "quality_score": 0.93
  },
  "session_id": "session-uuid",
  "database_session_id": "db-session-uuid"
}
```

---

## Knowledge Management

### Search Knowledge Base

Search through the knowledge base using semantic search.

**Endpoint:** `GET /api/knowledge/search`

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Number of results (default: 10, max: 50)
- `company` (optional): Filter by company name

**Example:**
```
GET /api/knowledge/search?q=webhook%20authentication&limit=5
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "doc-uuid",
      "title": "Webhook Authentication Best Practices",
      "content": "Detailed content...",
      "relevance_score": 0.92,
      "source": "qdrant",
      "url": "https://example.com/docs/webhooks",
      "category": "documentation",
      "created_at": "2024-01-20T10:00:00Z"
    }
  ],
  "total_results": 5,
  "query": "webhook authentication"
}
```

### Add Crawl URL

Add a URL to be crawled for knowledge base.

**Endpoint:** `POST /api/knowledge/urls`

**Request Body:**
```json
{
  "company_name": "Zapier",
  "url": "https://zapier.com/help/webhooks"
}
```

**Response:**
```json
{
  "success": true,
  "url_id": "url-uuid",
  "company_name": "Zapier",
  "url": "https://zapier.com/help/webhooks",
  "message": "URL added to crawl queue"
}
```

### Remove Crawl URL

Remove a URL from the crawl list.

**Endpoint:** `DELETE /api/knowledge/urls`

**Request Body:**
```json
{
  "company_name": "Zapier",
  "url": "https://zapier.com/help/webhooks"
}
```

**Response:**
```json
{
  "success": true,
  "message": "URL removed from crawl list"
}
```

### Get Company URLs

Get all crawl URLs for a specific company.

**Endpoint:** `GET /api/knowledge/companies/{company_name}/urls`

**Response:**
```json
{
  "success": true,
  "company_name": "Zapier",
  "urls": [
    {
      "id": "url-uuid",
      "url": "https://zapier.com/help/webhooks",
      "is_active": true,
      "created_at": "2024-01-20T10:00:00Z",
      "last_crawled": "2024-01-20T15:30:00Z"
    }
  ],
  "total_urls": 10
}
```

### Trigger Knowledge Crawl

Trigger Firecrawl to scrape and index content.

**Endpoint:** `POST /api/knowledge/crawl`

**Request Body:**
```json
{
  "company_name": "Zapier",
  "max_pages": 50,
  "force_refresh": false
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "crawl-job-uuid",
  "status": "started",
  "company_name": "Zapier",
  "max_pages": 50,
  "estimated_completion": "2024-01-20T16:00:00Z"
}
```

### Check Crawl Job Status

Check the status of a crawl job.

**Endpoint:** `GET /api/knowledge/crawl/{job_id}`

**Response:**
```json
{
  "success": true,
  "job_id": "crawl-job-uuid",
  "status": "completed",
  "company_name": "Zapier",
  "pages_crawled": 42,
  "documents_indexed": 38,
  "started_at": "2024-01-20T15:00:00Z",
  "completed_at": "2024-01-20T15:45:00Z",
  "errors": []
}
```

### Get All Companies

List all companies in the knowledge base.

**Endpoint:** `GET /api/knowledge/companies`

**Response:**
```json
{
  "success": true,
  "companies": [
    {
      "id": "company-uuid",
      "name": "Zapier",
      "domain": "zapier.com",
      "description": "Automation platform",
      "url_count": 10,
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total_companies": 5
}
```

### Set Current Company

Set the active company for knowledge retrieval.

**Endpoint:** `POST /api/knowledge/companies/current`

**Request Body:**
```json
{
  "company_name": "Zapier"
}
```

**Response:**
```json
{
  "success": true,
  "current_company": "Zapier",
  "message": "Current company updated"
}
```

---

## Conversation Management

### Get Conversation History

Retrieve conversation history for a session.

**Endpoint:** `GET /api/conversation/{session_id}`

**Response:**
```json
{
  "success": true,
  "session_id": "session-uuid",
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

### List Active Conversations

Get all active conversation sessions.

**Endpoint:** `GET /api/conversations`

**Query Parameters:**
- `limit` (optional): Number of conversations (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "session-uuid",
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

### Submit User Feedback

Submit feedback for a conversation session.

**Endpoint:** `POST /api/agents/feedback`

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "rating": 5,
  "comment": "Excellent technical support, solved my issue quickly"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "session-uuid",
  "message": "Feedback recorded successfully",
  "learning_insight_generated": true
}
```

---

## Efficiency & Optimization

### Bulk Chat Processing

Process multiple messages efficiently in parallel.

**Endpoint:** `POST /api/efficiency/bulk-chat`

**Request Body:**
```json
{
  "messages": [
    "How do I set up webhooks?",
    "What's the billing structure?",
    "Security best practices?"
  ],
  "agent_type": "multi-agent",
  "context": {
    "user_id": "user-123"
  },
  "priority": "normal"
}
```

**Response:**
```json
{
  "success": true,
  "processed_count": 3,
  "results": [
    {
      "index": 0,
      "message": "How do I set up webhooks?",
      "result": {
        "success": true,
        "response": "...",
        "database_session_id": "session-uuid-1"
      }
    }
  ],
  "session_ids": ["session-uuid-1", "session-uuid-2", "session-uuid-3"],
  "bulk_processing": true
}
```

### Get Chat Templates

Get predefined templates for common queries.

**Endpoint:** `GET /api/efficiency/templates`

**Response:**
```json
{
  "success": true,
  "templates": [
    {
      "name": "webhook_troubleshooting",
      "template": "I'm having issues with webhook {webhook_url}. The error is: {error_message}. Can you help diagnose the problem?",
      "variables": ["webhook_url", "error_message"],
      "category": "technical",
      "description": "Template for webhook integration issues"
    }
  ],
  "total_count": 5
}
```

### Generate from Template

Generate and process a message from a template.

**Endpoint:** `POST /api/efficiency/templates/{template_name}/generate`

**Request Body:**
```json
{
  "webhook_url": "https://api.example.com/webhook",
  "error_message": "401 Unauthorized"
}
```

**Response:**
```json
{
  "success": true,
  "template_name": "webhook_troubleshooting",
  "generated_message": "I'm having issues with webhook https://api.example.com/webhook. The error is: 401 Unauthorized. Can you help diagnose the problem?",
  "result": {
    "success": true,
    "response": "..."
  }
}
```

### Get Agent Presets

Get predefined agent combinations for specific use cases.

**Endpoint:** `GET /api/efficiency/agent-presets`

**Response:**
```json
{
  "success": true,
  "presets": [
    {
      "name": "technical_support",
      "description": "Best agents for technical troubleshooting",
      "agent_ids": ["agent-uuid-1", "agent-uuid-2"],
      "use_case": "API issues, webhook problems",
      "priority_order": [0, 1, 2]
    }
  ],
  "total_presets": 3
}
```

### Get Performance Insights

Get performance insights and optimization recommendations.

**Endpoint:** `GET /api/efficiency/performance-insights`

**Query Parameters:**
- `days` (optional): Time period in days (default: 7, max: 90)
- `limit` (optional): Number of insights (default: 10, max: 50)

**Response:**
```json
{
  "success": true,
  "performance_score": 92.0,
  "time_period_days": 7,
  "insights": {
    "query_patterns": [
      {
        "pattern_description": "Webhook troubleshooting",
        "frequency": 45,
        "avg_satisfaction": 4.5,
        "optimal_agents": ["Technical Integration Specialist"]
      }
    ],
    "learning_insights": [
      {
        "title": "High user satisfaction on security queries",
        "type": "user_satisfaction",
        "confidence": 0.9,
        "data_points": 23
      }
    ],
    "recommendations": [
      {
        "type": "optimization",
        "priority": "medium",
        "title": "Optimize Common Query Pattern",
        "description": "..."
      }
    ]
  },
  "system_health": {...},
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Optimize System

Trigger system optimization tasks.

**Endpoint:** `POST /api/efficiency/optimize`

**Request Body:**
```json
{
  "optimization_type": "cache",
  "parameters": {
    "force_refresh": true
  }
}
```

**Optimization Types:**
- `cache`: Refresh agent cache
- `performance`: Performance optimization
- `learning`: Generate learning insights
- `agents`: Agent optimization

**Response:**
```json
{
  "success": true,
  "optimization_type": "cache",
  "results": {
    "cache_refresh": {
      "success": true,
      "agents_loaded": 22
    }
  },
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Get Usage Statistics

Get comprehensive usage statistics.

**Endpoint:** `GET /api/efficiency/usage-statistics`

**Query Parameters:**
- `days` (optional): Time period (default: 7, max: 90)

**Response:**
```json
{
  "success": true,
  "statistics": {
    "time_period": {
      "start_date": "2024-01-13T00:00:00Z",
      "end_date": "2024-01-20T00:00:00Z",
      "days": 7
    },
    "conversation_stats": {
      "total_conversations": 156,
      "successful_conversations": 142,
      "success_rate": 91.0,
      "avg_response_time": "2.3s",
      "avg_user_satisfaction": 4.2
    },
    "agent_usage": {
      "most_used_agent": "Technical Integration Specialist",
      "avg_agents_per_query": 2.1,
      "collaboration_rate": 68.0
    },
    "performance_metrics": {
      "cache_hit_rate": 89.5,
      "database_response_time": "45ms",
      "memory_efficiency": 92.3
    },
    "learning_metrics": {
      "insights_generated": 23,
      "insights_implemented": 18,
      "improvement_rate": 78.3
    }
  },
  "generated_at": "2024-01-20T10:30:00Z"
}
```

### Comprehensive Health Check

Get comprehensive system health status.

**Endpoint:** `GET /api/efficiency/health-check`

**Response:**
```json
{
  "overall_status": "healthy",
  "timestamp": "2024-01-20T10:30:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "pool_size": 5
    },
    "agent_cache": {
      "status": "healthy",
      "stats": {
        "total_agents": 22,
        "cache_hits": 450,
        "cache_misses": 12
      }
    },
    "websockets": {
      "status": "healthy",
      "active_sessions": 8
    },
    "crewai": {
      "status": "healthy",
      "patched": true
    }
  }
}
```

---

## WebSocket API

### Agent Tracking WebSocket

Real-time agent status updates.

**Endpoint:** `ws://localhost:8000/ws/agent-tracking/{client_id}`

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent-tracking/client-123');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

**Message Types Received:**

**1. Active Sessions**
```json
{
  "type": "active_sessions",
  "timestamp": 1642678200.123,
  "data": {
    "total_sessions": 3,
    "sessions": [...]
  }
}
```

**2. Agent Status Update**
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

**3. Agent Collaboration**
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

**4. Ping/Pong**
```json
{
  "type": "ping",
  "timestamp": 1642678200.123
}
```

**Client Messages to Send:**

**1. Get Session Logs**
```json
{
  "type": "get_session_logs",
  "session_id": "session-uuid"
}
```

**2. Get Session State**
```json
{
  "type": "get_session_state",
  "session_id": "session-uuid"
}
```

**3. Start Log Streaming**
```json
{
  "type": "start_log_streaming",
  "session_id": "session-uuid"
}
```

**4. Stop Log Streaming**
```json
{
  "type": "stop_log_streaming"
}
```

**5. Pong (response to ping)**
```json
{
  "type": "pong"
}
```

### WebSocket Stats

Get WebSocket connection statistics (REST endpoint).

**Endpoint:** `GET /api/ws/stats`

**Response:**
```json
{
  "success": true,
  "stats": {
    "active_connections": 5,
    "total_messages_sent": 1250,
    "connections": [
      {
        "client_id": "client-123",
        "connected_at": 1642678000.0,
        "message_count": 45
      }
    ]
  },
  "realtime_sessions": {
    "total_sessions": 3,
    "active_agents": 8
  }
}
```

### Get Session Logs (REST)

Get execution logs for a session (REST endpoint).

**Endpoint:** `GET /api/ws/sessions/{session_id}/logs`

**Response:**
```json
{
  "success": true,
  "session_id": "session-uuid",
  "logs": [
    {
      "timestamp": "2024-01-20T10:30:00Z",
      "level": "info",
      "agent": "Technical Integration Specialist",
      "message": "Starting webhook analysis",
      "details": {}
    }
  ],
  "total_logs": 45
}
```

### Get Session State (REST)

Get current session state (REST endpoint).

**Endpoint:** `GET /api/ws/sessions/{session_id}/state`

**Response:**
```json
{
  "success": true,
  "session_id": "session-uuid",
  "state": {
    "session_id": "session-uuid",
    "query": "How do I fix webhook errors?",
    "total_agents": 3,
    "current_phase": "processing",
    "overall_progress": 65,
    "started_at": "2024-01-20T10:30:00Z",
    "estimated_completion": 30,
    "active_agents": [
      {
        "agent_id": "agent-uuid",
        "agent_name": "Technical Integration Specialist",
        "status": "PROCESSING",
        "current_task": "Analyzing webhook configuration",
        "progress": 75,
        "details": {},
        "started_at": "2024-01-20T10:30:05Z",
        "updated_at": "2024-01-20T10:30:20Z"
      }
    ],
    "completed_agents": [],
    "crew_output": [...]
  }
}
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "error_type": "validation_error",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Scenarios

**1. Invalid Agent ID**
```json
{
  "detail": "Invalid agent ID format",
  "status_code": 400
}
```

**2. Agent Not Found**
```json
{
  "detail": "Agent not found",
  "status_code": 404
}
```

**3. Session Not Found**
```json
{
  "detail": "Session not found",
  "status_code": 404
}
```

**4. Database Connection Error**
```json
{
  "detail": "Database connection failed",
  "status_code": 503
}
```

**5. Validation Error**
```json
{
  "detail": "Validation error: name is required",
  "status_code": 422,
  "validation_errors": [
    {
      "field": "name",
      "message": "Field required"
    }
  ]
}
```

---

## Rate Limiting

Currently not implemented. For production:

```
Rate Limits:
- 100 requests per minute per IP
- 1000 requests per hour per API key
```

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642678260
```

---

## Examples

### Complete Workflow Example

```javascript
// 1. Create a custom agent
const createResponse = await fetch('http://localhost:8000/api/agents/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "Custom Security Analyst",
    role: "Cybersecurity expert",
    domain: "security",
    keywords: ["security", "vulnerability"],
    llm_config: {
      model: "claude-3-5-sonnet-20241022",
      temperature: 0.1
    }
  })
});

const { agent_id } = await createResponse.json();

// 2. Process a query
const queryResponse = await fetch('http://localhost:8000/api/multi-agent/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Analyze security vulnerabilities in our webhook system",
    context: { user_id: "user-123" }
  })
});

const result = await queryResponse.json();
console.log('Response:', result.response);
console.log('Agents used:', result.agents_used);

// 3. Submit feedback
await fetch('http://localhost:8000/api/agents/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: result.session_id,
    rating: 5,
    comment: "Excellent security analysis"
  })
});
```

### WebSocket Real-Time Tracking Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent-tracking/my-client-id');

ws.onopen = () => {
  console.log('Connected to agent tracking');

  // Request session state
  ws.send(JSON.stringify({
    type: 'get_session_state',
    session_id: 'session-uuid'
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'agent_status':
      console.log(`Agent ${message.agent_name}: ${message.status} - ${message.message}`);
      updateProgressBar(message.progress);
      break;

    case 'agent_collaboration':
      console.log(`Collaboration: ${message.primary_agent} → ${message.secondary_agent}`);
      break;

    case 'ping':
      ws.send(JSON.stringify({ type: 'pong' }));
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket closed, reconnecting...');
  setTimeout(connectWebSocket, 3000);
};
```

---

## API Versioning

Current version: `v1` (implicit, no version in URL)

Future versions will use URL versioning:
```
/api/v2/agents/list
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- Test API calls directly
- View request/response schemas
- See validation rules

---

## SDK Support

### JavaScript/TypeScript

```javascript
import { AgentCraftClient } from './services/api';

const client = new AgentCraftClient('http://localhost:8000');

// List agents
const agents = await client.agents.list();

// Process query
const result = await client.query.process({
  query: "How do I fix webhook errors?",
  context: {}
});

// Submit feedback
await client.feedback.submit({
  session_id: result.session_id,
  rating: 5
});
```

### Python

```python
from agentcraft_client import AgentCraftClient

client = AgentCraftClient("http://localhost:8000")

# List agents
agents = client.agents.list()

# Process query
result = client.query.process(
    query="How do I fix webhook errors?",
    context={}
)

# Submit feedback
client.feedback.submit(
    session_id=result["session_id"],
    rating=5
)
```

---

For more information, see:
- [agents.md](agents.md) - Agent system architecture
- [WEBSOCKET.md](WEBSOCKET.md) - WebSocket protocol details
- [CONVERSATION_SYSTEM.md](CONVERSATION_SYSTEM.md) - Conversation memory system
- [KNOWLEDGE_SYSTEM.md](KNOWLEDGE_SYSTEM.md) - Knowledge retrieval system
