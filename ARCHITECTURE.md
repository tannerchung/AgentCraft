# AgentCraft System Architecture

Complete architectural overview of the AgentCraft multi-agent AI system.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Decisions](#architecture-decisions)
3. [Design Patterns](#design-patterns)
4. [Component Architecture](#component-architecture)
5. [Data Flow](#data-flow)
6. [Scalability](#scalability)
7. [Technology Choices](#technology-choices)
8. [Security Architecture](#security-architecture)

---

## System Overview

AgentCraft is a production-ready multi-agent AI system built on modern cloud-native principles with emphasis on scalability, observability, and intelligent agent orchestration.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Load Balancer                            │
│                     (Nginx / Cloud LB)                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴────────────────┐
         │                                │
         ▼                                ▼
┌─────────────────┐              ┌─────────────────┐
│  Frontend Tier  │              │  Frontend Tier  │
│  (React SPA)    │              │  (React SPA)    │
│  - Port 3000    │              │  - Port 3000    │
│  - Static Files │              │  - Static Files │
│  - WebSocket    │              │  - WebSocket    │
└────────┬────────┘              └────────┬────────┘
         │                                │
         └────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │   API Gateway Layer    │
         │   (FastAPI Backend)    │
         │   - Port 8000          │
         │   - REST Endpoints     │
         │   - WebSocket Handlers │
         └────────┬───────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
┌─────────┐  ┌──────────┐  ┌──────────┐
│  Agent  │  │Knowledge │  │WebSocket │
│  Router │  │Retrieval │  │ Manager  │
│  Layer  │  │  Layer   │  │          │
└────┬────┘  └────┬─────┘  └────┬─────┘
     │            │             │
     ▼            ▼             ▼
┌──────────────────────────────────────┐
│        Service Layer                 │
│  ┌─────────┐  ┌──────────┐          │
│  │ Qdrant  │  │Firecrawl │          │
│  │ Service │  │ Service  │          │
│  └─────────┘  └──────────┘          │
│  ┌─────────┐  ┌──────────┐          │
│  │  HITL   │  │ Target   │          │
│  │ Service │  │ Company  │          │
│  └─────────┘  └──────────┘          │
└──────────────────┬───────────────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
     ▼             ▼             ▼
┌──────────┐  ┌─────────┐  ┌──────────┐
│PostgreSQL│  │ Qdrant  │  │ External │
│ Database │  │ Cloud   │  │   APIs   │
│          │  │ Vector  │  │ (OpenAI, │
│          │  │   DB    │  │ Anthropic│
│          │  │         │  │ Firecrawl│
└──────────┘  └─────────┘  └──────────┘
```

### Key Components

1. **Frontend Layer**: React SPA with WebSocket support
2. **API Gateway**: FastAPI backend with async support
3. **Agent System**: Multi-agent orchestration and routing
4. **Knowledge Layer**: Vector search and web scraping
5. **Service Layer**: Specialized backend services
6. **Data Layer**: PostgreSQL + Qdrant vector database
7. **External Services**: AI APIs and web scraping

---

## Architecture Decisions

### 1. Microservices vs Monolith

**Decision**: Modular Monolith

**Rationale:**
- Simpler deployment and operations
- Easier local development
- Lower operational complexity
- Can evolve to microservices if needed

**Trade-offs:**
- ✅ Simplified deployment
- ✅ Easier debugging
- ✅ Reduced latency (no network calls)
- ❌ Harder to scale individual components
- ❌ Shared resources and dependencies

### 2. Synchronous vs Asynchronous

**Decision**: Async-first (AsyncIO + FastAPI)

**Rationale:**
- Non-blocking I/O for better performance
- Handle multiple concurrent requests efficiently
- Ideal for I/O-bound operations (API calls, database queries)

**Implementation:**
```python
# All I/O operations are async
async def process_query(query: str):
    # Concurrent operations
    results = await asyncio.gather(
        qdrant_service.search(query),
        firecrawl_service.scrape_url(url),
        get_conversation_context(session_id)
    )
    return combine_results(results)
```

### 3. State Management

**Decision**: In-Memory + Database Hybrid

**Rationale:**
- Conversation memory: In-memory for fast access
- Agent configs: Database for persistence
- WebSocket state: In-memory for real-time updates

**Architecture:**
```python
# In-memory (fast, ephemeral)
conversation_memory = ConversationMemory()  # RAM
websocket_connections = {}  # RAM

# Database (persistent, scalable)
Agent.objects.all()  # PostgreSQL
Conversation.create()  # PostgreSQL
```

### 4. Caching Strategy

**Decision**: Multi-level caching

**Levels:**
1. **Application cache**: LRU cache for function results
2. **Query cache**: Qdrant search results
3. **Content cache**: Firecrawl scraped content
4. **CDN cache**: Static assets (frontend)

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_search(query: str):
    return qdrant_service.search(query)
```

### 5. Real-time Communication

**Decision**: WebSocket for agent tracking, REST for queries

**Rationale:**
- WebSocket: Bidirectional, low latency for status updates
- REST: Stateless, cacheable for query processing

**Protocol Design:**
```javascript
// WebSocket: Real-time updates
ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    if (update.type === 'agent_status') {
        updateUI(update);
    }
};

// REST: Query processing
const response = await fetch('/api/query', {
    method: 'POST',
    body: JSON.stringify({ query })
});
```

---

## Design Patterns

### 1. Singleton Pattern

**Usage**: Service instances

**Implementation:**
```python
# src/services/qdrant_service.py
class QdrantService:
    def __init__(self):
        self.client = QdrantClient(...)

# Global singleton instance
qdrant_service = QdrantService()

# Import and use anywhere
from src.services.qdrant_service import qdrant_service
results = qdrant_service.search(query)
```

**Benefits:**
- Single point of configuration
- Shared connection pools
- Consistent state

### 2. Factory Pattern

**Usage**: Agent creation

**Implementation:**
```python
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, config: dict):
        if agent_type == "technical":
            return TechnicalAgent(config)
        elif agent_type == "business":
            return BusinessAgent(config)
        # ...

# Usage
agent = AgentFactory.create_agent("technical", config)
```

### 3. Observer Pattern

**Usage**: WebSocket notifications

**Implementation:**
```python
class WebSocketManager:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    async def notify(self, message):
        for observer in self.observers:
            await observer.send(message)

# Agent updates notify all WebSocket clients
ws_manager.notify(agent_status_update)
```

### 4. Strategy Pattern

**Usage**: Knowledge retrieval strategies

**Implementation:**
```python
class SearchStrategy(ABC):
    @abstractmethod
    def search(self, query: str):
        pass

class QdrantSearchStrategy(SearchStrategy):
    def search(self, query: str):
        return qdrant_service.search(query)

class FirecrawlSearchStrategy(SearchStrategy):
    def search(self, query: str):
        return firecrawl_service.scrape_url(url)

# Context switches strategies
class KnowledgeRetriever:
    def __init__(self, strategy: SearchStrategy):
        self.strategy = strategy

    def retrieve(self, query: str):
        return self.strategy.search(query)
```

### 5. Repository Pattern

**Usage**: Database abstraction

**Implementation:**
```python
class AgentRepository:
    def get_all(self):
        return Agent.objects.all()

    def get_by_id(self, agent_id: str):
        return Agent.objects.get(id=agent_id)

    def create(self, agent_data: dict):
        return Agent.objects.create(**agent_data)

    def update(self, agent_id: str, updates: dict):
        return Agent.objects.filter(id=agent_id).update(**updates)

# Service layer uses repository
class AgentService:
    def __init__(self):
        self.repo = AgentRepository()

    def list_agents(self):
        return self.repo.get_all()
```

---

## Component Architecture

### Frontend Architecture

```
src/
├── components/          # React components
│   ├── MultiAgentDemo.js
│   ├── AgentChat.js
│   └── KnowledgeBaseManager.js
├── hooks/              # Custom hooks
│   └── useAgentChat.js
├── services/           # API clients
│   └── api.js
└── App.js             # Main app component
```

**Component Hierarchy:**
```
App
├── Header
├── Navigation
└── ContentArea
    ├── MultiAgentDemo
    │   ├── AgentSelector
    │   ├── MessageList
    │   │   └── MessageBubble (multiple)
    │   ├── AgentStatusPanel
    │   │   └── AgentStatusCard (multiple)
    │   └── MessageInput
    ├── KnowledgeBaseManager
    │   ├── CompanySelector
    │   ├── URLManager
    │   └── SearchInterface
    └── AgentConfiguration
        ├── AgentList
        └── AgentEditor
```

### Backend Architecture

```
backend/
├── main.py                    # FastAPI app + routes
├── agent_management_api.py    # Agent CRUD
├── knowledge_api.py           # Knowledge endpoints
├── websocket_api.py           # WebSocket handlers
└── enhanced_backend.py        # Database integration

src/
├── core/
│   ├── base_agent.py         # Base agent class
│   └── agent_router.py       # Routing logic
├── agents/
│   ├── technical_support_agent.py
│   └── realtime_agent_tracker.py
└── services/
    ├── qdrant_service.py     # Vector DB
    ├── firecrawl_service.py  # Web scraping
    ├── hitl_service.py       # Human-in-the-loop
    └── target_company_service.py
```

**Layered Architecture:**
```
┌─────────────────────────┐
│   Presentation Layer    │  FastAPI routes
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│    Business Logic       │  Agent routing, orchestration
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│    Service Layer        │  Qdrant, Firecrawl, HITL
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│     Data Layer          │  PostgreSQL, Qdrant Cloud
└─────────────────────────┘
```

---

## Data Flow

### Query Processing Flow

```
1. User Input
   │
   ▼
2. Frontend (React)
   │ - Generate session ID
   │ - Send via API call
   ▼
3. API Gateway (FastAPI)
   │ - Validate request
   │ - Add to conversation memory
   ▼
4. Agent Router
   │ - Analyze query
   │ - Select appropriate agent
   │ - Calculate confidence
   ▼
5. Knowledge Retrieval (Parallel)
   ├─► Qdrant Vector Search
   │   └─► Semantic similarity
   └─► Firecrawl Web Scraping
       └─► Real-time content
   ▼
6. Agent Processing
   │ - Combine knowledge
   │ - Generate response
   │ - Create citations
   ▼
7. Response Assembly
   │ - Format response
   │ - Add metadata
   │ - Store in conversation
   ▼
8. API Response
   │ - Return to frontend
   ▼
9. UI Update
   └─► Display to user
```

### WebSocket Data Flow

```
1. Client Connects
   │
   ▼
2. WebSocket Manager
   │ - Accept connection
   │ - Store client reference
   │ - Send initial state
   ▼
3. Agent Execution
   │ - Agent starts task
   │ - Emit status updates
   ▼
4. Event Broadcasting
   │ - Format message
   │ - Send to all clients
   ▼
5. Client Receives
   │ - Parse message
   │ - Update UI
   └─► Real-time display
```

### Knowledge Indexing Flow

```
1. Add URL Request
   │
   ▼
2. Target Company Service
   │ - Validate URL
   │ - Store in database
   ▼
3. Trigger Crawl Job
   │
   ▼
4. Firecrawl Service
   │ - Scrape content
   │ - Extract text
   │ - Convert to markdown
   ▼
5. Content Processing
   │ - Clean content
   │ - Generate embeddings
   ▼
6. Qdrant Indexing
   │ - Create vectors
   │ - Store in collection
   │ - Add metadata
   ▼
7. Ready for Search
   └─► Available to agents
```

---

## Scalability

### Horizontal Scaling

**Stateless Components:**
```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentcraft-backend
spec:
  replicas: 5  # Scale to 5 instances
  selector:
    matchLabels:
      app: backend
  template:
    spec:
      containers:
      - name: backend
        image: agentcraft/backend:latest
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

**Load Balancing:**
```nginx
upstream backend_servers {
    least_conn;  # Least connections algorithm
    server backend1:8000 weight=1;
    server backend2:8000 weight=1;
    server backend3:8000 weight=1;
}
```

### Vertical Scaling

**Resource Allocation:**
```python
# Increase worker processes
workers = (cpu_count * 2) + 1

# Increase connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,      # More connections
    max_overflow=40
)
```

### Database Scaling

**Read Replicas:**
```python
# Master for writes
master_db = create_engine(MASTER_DATABASE_URL)

# Replicas for reads
read_db_1 = create_engine(READ_REPLICA_1_URL)
read_db_2 = create_engine(READ_REPLICA_2_URL)

# Route reads to replicas
def get_db_for_operation(operation_type):
    if operation_type == 'write':
        return master_db
    else:
        return random.choice([read_db_1, read_db_2])
```

**Sharding:**
```python
# Shard by session_id
def get_shard_for_session(session_id: str):
    shard_num = hash(session_id) % NUM_SHARDS
    return shards[shard_num]
```

### Caching Layer

**Redis for Distributed Cache:**
```python
import redis

cache = redis.Redis(host='redis-server', port=6379)

def cached_search(query: str):
    # Check cache
    cached_result = cache.get(f"search:{query}")
    if cached_result:
        return json.loads(cached_result)

    # Perform search
    result = qdrant_service.search(query)

    # Cache result (TTL: 1 hour)
    cache.setex(f"search:{query}", 3600, json.dumps(result))

    return result
```

### Queue-Based Processing

**Async Task Queue:**
```python
from celery import Celery

celery_app = Celery('agentcraft', broker='redis://localhost:6379')

@celery_app.task
def async_crawl_job(company_name: str):
    """Async crawl job for long-running tasks"""
    urls = target_company_service.get_crawl_urls(company_name)
    for url in urls:
        firecrawl_service.scrape_url(url)
        # Process and index

# Trigger async
async_crawl_job.delay("Zapier")
```

---

## Technology Choices

### Backend Technologies

| Technology | Purpose | Rationale |
|-----------|---------|-----------|
| **Python 3.11** | Backend language | Async support, AI/ML ecosystem |
| **FastAPI** | Web framework | High performance, async, auto docs |
| **PostgreSQL** | Primary database | ACID compliance, JSON support |
| **Qdrant** | Vector database | Semantic search, cloud-native |
| **AsyncIO** | Concurrency | Non-blocking I/O, scalability |

### Frontend Technologies

| Technology | Purpose | Rationale |
|-----------|---------|-----------|
| **React 18** | UI framework | Component reusability, ecosystem |
| **Tailwind CSS** | Styling | Utility-first, responsive design |
| **Lucide React** | Icons | Lightweight, consistent design |
| **WebSocket API** | Real-time | Bidirectional, low latency |

### External Services

| Service | Purpose | Rationale |
|---------|---------|-----------|
| **OpenAI/Anthropic** | AI models | State-of-the-art language models |
| **Firecrawl** | Web scraping | Reliable, structured content |
| **Qdrant Cloud** | Vector storage | Managed, scalable, semantic search |
| **Galileo** | Observability | AI-specific monitoring |

### Development Tools

| Tool | Purpose |
|------|---------|
| **pytest** | Testing framework |
| **Black** | Code formatting |
| **Flake8** | Linting |
| **Docker** | Containerization |
| **Git** | Version control |

---

## Security Architecture

### Authentication & Authorization

```python
# API key authentication (future)
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in valid_api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# Protected endpoint
@app.get("/api/protected")
async def protected_endpoint(api_key: str = Depends(verify_api_key)):
    return {"message": "Access granted"}
```

### Data Encryption

```python
# Encrypt sensitive data at rest
from cryptography.fernet import Fernet

cipher_suite = Fernet(encryption_key)

def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return cipher_suite.decrypt(encrypted_data.encode()).decode()
```

### Secure Communication

```nginx
# HTTPS only
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}
```

### Input Validation

```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    query: str
    session_id: str = None

    @validator('query')
    def validate_query(cls, v):
        if len(v) > 5000:
            raise ValueError('Query too long')
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/query")
@limiter.limit("10/minute")
async def query_endpoint(request: Request):
    # Process query
    pass
```

---

## Future Considerations

### Planned Enhancements

1. **Multi-tenancy**: Support multiple organizations
2. **Advanced Caching**: Redis cluster for distributed cache
3. **Microservices**: Split into independent services
4. **Event Sourcing**: Track all system events
5. **GraphQL API**: Alternative to REST
6. **gRPC**: High-performance inter-service communication

### Scalability Roadmap

```
Current: Modular Monolith
  ↓
Phase 1: Horizontal Scaling (multiple instances)
  ↓
Phase 2: Database Read Replicas
  ↓
Phase 3: Service Separation (knowledge, agents, websocket)
  ↓
Phase 4: Microservices Architecture
  ↓
Phase 5: Event-Driven Architecture
```

---

## Related Documentation

- [SERVICES.md](SERVICES.md) - Service implementations
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment architecture
- [FRONTEND.md](FRONTEND.md) - Frontend architecture
- [API.md](API.md) - API design
- [TESTING.md](TESTING.md) - Testing strategy
