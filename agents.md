# AgentCraft - Agent System Documentation

## Table of Contents
1. [Overview](#overview)
2. [Agent Architecture](#agent-architecture)
3. [Agent Types & Specializations](#agent-types--specializations)
4. [Agent Routing System](#agent-routing-system)
5. [Database-Backed Agent Management](#database-backed-agent-management)
6. [Adaptive Multi-LLM System](#adaptive-multi-llm-system)
7. [Knowledge Integration](#knowledge-integration)
8. [Real-Time Tracking & WebSocket](#real-time-tracking--websocket)
9. [Performance Metrics & Learning](#performance-metrics--learning)
10. [Frontend Components](#frontend-components)
11. [Backend API Endpoints](#backend-api-endpoints)
12. [Data Flow & Interaction](#data-flow--interaction)
13. [Configuration & Setup](#configuration--setup)

---

## Overview

**AgentCraft** is a production-ready multi-agent AI system that combines specialized domain expertise with advanced observability, real-time tracking, and competitive intelligence capabilities. The system demonstrates how custom AI agents can deliver superior outcomes compared to generic platform solutions.

### Key Capabilities
- **20+ Specialized Agents**: Domain-specific expertise across technical, business, and analysis domains
- **Intelligent Agent Routing**: Keyword-based routing to optimal agents
- **Database Persistence**: PostgreSQL-backed agent configurations and metrics
- **Adaptive LLM Selection**: Intelligent model selection (Claude, GPT-4) with performance tracking
- **External Knowledge Integration**: Real-time web scraping (Firecrawl) + vector search (Qdrant)
- **Conversation Memory**: Session-based persistent context across interactions
- **Real-Time Monitoring**: WebSocket-based live agent status tracking
- **Comprehensive Analytics**: Performance metrics, learning insights, and continuous improvement

---

## Agent Architecture

### Base Agent Class (`src/core/base_agent.py`)

The foundation for all specialized agents in AgentCraft.

```python
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
```

#### Key Features:
- **Abstract Methods**: `handle_query()` and `_get_specialized_knowledge()` must be implemented
- **Performance Tracking**: Automatic metrics updates for response time and confidence
- **Capability Reporting**: Self-describing agents with domain expertise metadata

### Agent Database Model (`database/models.py`)

Agents are persisted in PostgreSQL with comprehensive configuration:

```sql
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(500) NOT NULL,
    backstory TEXT,
    goal TEXT,
    llm_config JSONB DEFAULT '{}',
    tools JSONB DEFAULT '[]',
    keywords JSONB DEFAULT '[]',
    avatar VARCHAR(10) DEFAULT '🤖',
    color VARCHAR(50) DEFAULT 'blue',
    domain VARCHAR(100) DEFAULT 'general',
    is_active BOOLEAN DEFAULT true,
    performance_metrics JSONB DEFAULT '{}',
    specialization_score NUMERIC(3,2) DEFAULT 0.0,
    collaboration_rating NUMERIC(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Agent Properties:
- **Identity**: `name`, `role`, `avatar`, `color`
- **Configuration**: `backstory`, `goal`, `llm_config`, `tools`
- **Routing**: `keywords` (JSONB array for intelligent matching)
- **Classification**: `domain` (technical, business, analysis, etc.)
- **Metrics**: `performance_metrics`, `specialization_score`, `collaboration_rating`
- **Status**: `is_active` (soft delete support)

---

## Agent Types & Specializations

AgentCraft includes **20+ specialized agents** organized by domain:

### Technical Domain

#### Technical Integration Specialist
- **Keywords**: `webhook`, `api`, `integration`, `ssl`, `certificate`, `endpoint`, `authentication`
- **Expertise**: API integrations, webhooks, SSL/TLS, authentication protocols
- **Tools**: WebhookAnalysisTool, LiveWebhookTester
- **File**: `src/agents/technical_support_agent.py`, `src/agents/real_ai_technical_agent.py`

#### DevOps Engineer
- **Keywords**: `deployment`, `docker`, `kubernetes`, `ci/cd`, `pipeline`, `infrastructure`
- **Expertise**: Infrastructure management, deployment automation, monitoring

#### Security Specialist
- **Keywords**: `security`, `vulnerability`, `hack`, `breach`, `encryption`, `compliance`
- **Expertise**: Security audits, compliance (SOC 2, ISO 27001), penetration testing

#### Database Expert
- **Keywords**: `database`, `sql`, `query`, `migration`, `performance`, `timeout`, `optimization`
- **Expertise**: Database design, query optimization, migration strategies

### Business Domain

#### Billing & Revenue Expert
- **Keywords**: `billing`, `payment`, `subscription`, `invoice`, `refund`, `charge`
- **Expertise**: Payment processing (Stripe, PayPal), subscription management, revenue optimization

#### Legal Compliance Agent
- **Keywords**: `legal`, `contract`, `compliance`, `gdpr`, `privacy`, `terms`
- **Expertise**: Contract analysis, GDPR/CCPA compliance, legal risk assessment

#### Sales Operations
- **Keywords**: `sales`, `crm`, `lead`, `qualification`, `pipeline`
- **Expertise**: CRM management, lead qualification, sales pipeline optimization

#### Marketing Automation
- **Keywords**: `marketing`, `campaign`, `email`, `lead`, `nurturing`
- **Expertise**: Email campaigns, lead nurturing, marketing automation

### Analysis Domain

#### Competitive Intelligence Analyst
- **Keywords**: `competitor`, `competitive`, `market`, `analysis`, `strategy`
- **Expertise**: Market research, competitive positioning, strategic analysis
- **Tools**: CompetitiveAnalysisTool

#### Data Analytics Specialist
- **Keywords**: `analytics`, `data`, `metrics`, `reporting`, `business intelligence`
- **Expertise**: Business intelligence, predictive analytics, data visualization

#### Financial Analyst
- **Keywords**: `financial`, `budget`, `roi`, `forecast`, `revenue`
- **Expertise**: Financial modeling, ROI analysis, budget planning

### Customer Domain

#### Customer Success Manager
- **Keywords**: `customer`, `support`, `onboarding`, `retention`, `churn`
- **Expertise**: Customer onboarding, retention strategies, success metrics

#### Training & Education Specialist
- **Keywords**: `training`, `education`, `documentation`, `tutorial`
- **Expertise**: User education, documentation creation, training programs

### Product Domain

#### Product Manager
- **Keywords**: `product`, `roadmap`, `feature`, `requirements`
- **Expertise**: Product strategy, roadmap planning, feature prioritization

#### UX Research Specialist
- **Keywords**: `ux`, `user experience`, `usability`, `research`
- **Expertise**: User research, usability testing, UX design

### Industry Specialists

#### Healthcare Compliance Expert
- **Keywords**: `healthcare`, `hipaa`, `medical`, `patient`, `ehr`
- **Expertise**: HIPAA compliance, medical data security

#### Financial Services Specialist
- **Keywords**: `banking`, `fintech`, `pci`, `financial services`
- **Expertise**: Banking regulations, PCI DSS compliance

#### E-commerce Platform Expert
- **Keywords**: `ecommerce`, `retail`, `shopping`, `cart`
- **Expertise**: Online retail, payment processing, inventory management

#### SaaS Business Model Expert
- **Keywords**: `saas`, `subscription`, `platform`, `multi-tenant`
- **Expertise**: SaaS architecture, subscription models, platform scaling

---

## Agent Routing System

### AgentRouter Class (`src/core/agent_router.py`)

Routes queries to the most appropriate specialized agent based on keyword matching.

#### Routing Algorithm:

```python
def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    # 1. Analyze query for keywords
    query_lower = query.lower()
    agent_scores = {}

    # 2. Score each agent based on keyword matching
    for agent_name, keywords in self.routing_rules.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            agent_scores[agent_name] = score

    # 3. Select highest scoring agent
    if agent_scores:
        best_agent = max(agent_scores.items(), key=lambda x: x[1])
        selected_agent = best_agent[0]
        confidence = min(best_agent[1] / 3.0, 1.0)  # Normalize
    else:
        selected_agent = "technical_support"  # Default fallback
        confidence = 0.5

    # 4. Route to selected agent
    return agent.process_query(query, context)
```

#### Routing Features:
- **Keyword-Based Scoring**: Matches query text against agent keywords
- **Confidence Calculation**: Normalizes match score to confidence level
- **Fallback Mechanism**: Default to technical support if no matches
- **Performance Tracking**: Records routing decisions and outcomes

### Database-Driven Routing (`src/agents/database_agent_manager.py`)

Enhanced routing using database-backed agent selection:

```python
async def select_agents_for_query(self, query: str) -> List[Dict]:
    # 1. Extract keywords from query
    keywords = self._extract_keywords(query)

    # 2. Query database for matching agents
    matching_agents = await agent_manager.get_agents_by_keywords(keywords)

    # 3. Always include orchestrator
    orchestrator = await self.get_agent_by_name("Orchestration Agent")
    if orchestrator:
        matching_agents.insert(0, orchestrator)

    # 4. Limit to top 3 agents
    return matching_agents[:3]
```

#### Keyword Extraction Categories:
- `webhook`: webhook, api, integration, ssl, certificate, endpoint
- `billing`: billing, payment, subscription, invoice, refund, charge
- `security`: security, vulnerability, hack, breach, encryption, compliance
- `database`: database, sql, query, migration, performance, timeout
- `deployment`: deployment, docker, kubernetes, ci/cd, pipeline, infrastructure
- `legal`: legal, contract, compliance, gdpr, privacy, terms
- `competitive`: competitor, competitive, market, analysis, strategy
- `marketing`: marketing, campaign, email, lead, nurturing
- `support`: customer, support, onboarding, training, help

---

## Database-Backed Agent Management

### DatabaseAgentManager (`src/agents/database_agent_manager.py`)

Manages agents using PostgreSQL for persistence and dynamic configuration.

#### Key Features:

**1. Agent Caching**
```python
async def _refresh_agents_cache(self):
    agents = await agent_manager.get_all_agents()
    self._agents_cache = {agent['name']: agent for agent in agents}
    # Cache TTL: 5 minutes
```

**2. Dynamic Agent Selection**
- Keyword-based matching from database
- Specialization score ranking
- Collaboration rating optimization

**3. CRUD Operations**
- `create_agent(agent_data)`: Add new agents dynamically
- `update_agent(agent_id, updates)`: Modify agent configuration
- `deactivate_agent(agent_id)`: Soft delete agents

**4. Query Processing**
```python
async def process_query_with_agents(self, query: str, selected_agents: List[Dict]):
    # Create conversation session
    session_id = await agent_manager.create_conversation_session(session_data)

    # Process with adaptive LLM
    result = await self.adaptive_llm.process_multi_agent_query(
        query=query,
        selected_agents=selected_agents,
        session_id=session_id
    )

    # Record metrics for each agent
    await self._record_agent_metrics(...)

    return result
```

### AgentManager Database Layer (`database/models.py`)

Provides database operations for agent management:

**Core Methods:**
- `get_all_agents()`: Retrieve all active agents
- `get_agent_by_id(agent_id)`: Get specific agent
- `get_agents_by_keywords(keywords)`: Find agents by keyword matching
- `create_agent(agent_data)`: Create new agent
- `update_agent(agent_id, updates)`: Update agent configuration
- `deactivate_agent(agent_id)`: Soft delete agent

---

## Adaptive Multi-LLM System

### LLMPool Class (`src/agents/adaptive_llm_system.py`)

Manages multiple LLM models with intelligent selection and performance tracking.

#### Available Models:

**Fast Models** (OpenAI)
- `fast`: GPT-3.5 Turbo (temperature: 0.1)
- `balanced`: GPT-4o Mini (temperature: 0.2)
- `creative`: GPT-4o (temperature: 0.7)

**Reasoning Models** (Anthropic)
- `powerful`: Claude 3.5 Sonnet (temperature: 0.1)
- `reasoning`: Claude 3.5 Sonnet (temperature: 0.0)

#### LLM Metrics Tracking:

```python
@dataclass
class LLMMetrics:
    response_times: List[float]
    quality_scores: List[float]
    cost_per_token: float
    success_rate: float
    expertise_areas: List[str]
    token_usage: Dict[str, int]
    error_count: int
    total_requests: int

    def get_efficiency_score(self) -> float:
        quality = self.get_avg_quality()
        cost_efficiency = quality / self.cost_per_token
        speed_bonus = max(0, (5.0 - self.get_avg_response_time()) / 5.0)
        return cost_efficiency * (1 + speed_bonus * 0.2)
```

#### Selection Strategy:

```python
def select_best_llm(self, query_complexity: float, budget_constraint: float):
    weights = {
        "quality": 0.4,
        "speed": 0.3,
        "cost": 0.2,
        "reliability": 0.1
    }

    # Calculate weighted scores for each LLM
    # Select highest scoring model
    # Fall back to reliable model if primary fails
```

#### Features:
- **Performance Learning**: Tracks success/failure patterns
- **Cost Optimization**: Balances quality vs. cost
- **Hot-Swapping**: Dynamic model switching based on performance
- **Fallback Mechanisms**: Graceful degradation on failures
- **Quality Evaluation**: Uses evaluator LLM to score responses

### CrewAI Integration

AgentCraft uses **CrewAI** for multi-agent orchestration:

```python
from crewai import Agent, Task, Crew, LLM

# Create specialized agent
agent = Agent(
    role="Technical Integration Specialist",
    goal="Solve complex webhook and API integration issues",
    backstory="Senior engineer with 10+ years of API integration experience",
    llm=selected_llm,
    tools=[WebhookAnalysisTool(), LiveWebhookTester()],
    verbose=True
)

# Create task
task = Task(
    description=query,
    expected_output="Comprehensive technical solution",
    agent=agent
)

# Execute crew
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

---

## Knowledge Integration

### Qdrant Vector Database (`src/services/qdrant_service.py`)

Provides semantic search capabilities for knowledge retrieval.

#### Configuration:

```python
class QdrantService:
    def __init__(
        self,
        collection_name: str = "agentcraft_knowledge",
        host: str = "localhost",
        port: int = 6333
    ):
        # Try Qdrant Cloud first (with QDRANT_URL, QDRANT_API_KEY)
        # Fall back to local server
        # Fall back to in-memory mode
```

#### Key Operations:

**1. Collection Initialization**
```python
def _initialize_collection(self):
    # Create collection with vector dimensions
    VectorParams(size=384, distance=Distance.COSINE)
```

**2. Document Indexing**
```python
async def index_documents(self, documents: List[KnowledgeArticle]):
    # Generate embeddings using SentenceTransformer
    embeddings = self.encoder.encode([doc.content for doc in documents])

    # Create points with metadata
    points = [
        PointStruct(
            id=doc.id,
            vector=embedding.tolist(),
            payload={
                "title": doc.title,
                "category": doc.category,
                "tags": doc.tags,
                "content": doc.content
            }
        )
        for doc, embedding in zip(documents, embeddings)
    ]

    # Upsert to Qdrant
    self.client.upsert(collection_name=self.collection_name, points=points)
```

**3. Semantic Search**
```python
async def search(self, query: str, limit: int = 5, filters: Dict = None):
    # Encode query
    query_vector = self.encoder.encode(query).tolist()

    # Search with optional filters
    results = self.client.search(
        collection_name=self.collection_name,
        query_vector=query_vector,
        limit=limit,
        query_filter=filters
    )

    return [
        KnowledgeArticle(**hit.payload, relevance_score=hit.score)
        for hit in results
    ]
```

#### Embedding Model:
- **Model**: `all-MiniLM-L6-v2` (Sentence Transformers)
- **Dimensions**: 384
- **Distance Metric**: Cosine similarity
- **Performance**: Fast inference, good quality

### Firecrawl Web Scraping (`src/services/firecrawl_service.py`)

Real-time web scraping for external knowledge retrieval.

#### Configuration:
```python
class FirecrawlService:
    def __init__(self):
        self.api_key = os.getenv('FIRECRAWL_API_KEY')
        self.app = FirecrawlApp(api_key=self.api_key)
```

#### Key Operations:

**1. Single URL Scraping**
```python
async def scrape_url(self, url: str, options: Dict = None):
    scrape_options = {
        'formats': ['markdown', 'html'],
        'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'article'],
        'excludeTags': ['nav', 'footer', 'aside', 'script', 'style'],
        'onlyMainContent': True,
        'removeBase64Images': True
    }

    result = self.app.scrape_url(url, params=scrape_options)

    return {
        'success': True,
        'url': url,
        'title': result['data']['metadata']['title'],
        'content': result['data']['markdown'],
        'metadata': result['data']['metadata'],
        'scraped_at': datetime.now().isoformat()
    }
```

**2. Site Crawling**
```python
async def crawl_site(self, base_url: str, max_pages: int = 50):
    crawl_options = {
        'limit': max_pages,
        'scrapeOptions': {
            'formats': ['markdown'],
            'onlyMainContent': True
        }
    }

    crawl_result = self.app.crawl_url(base_url, params=crawl_options)
    # Returns multiple pages with structured content
```

#### Features:
- **Markdown Extraction**: Clean, structured content
- **Smart Content Detection**: Main content only
- **Metadata Extraction**: Title, description, keywords
- **Batch Crawling**: Multiple pages from same domain
- **Rate Limiting**: Respects site robots.txt

### Knowledge Integration Pipeline (`backend/knowledge_api.py`)

Orchestrates knowledge retrieval from multiple sources:

```python
async def get_knowledge(query: str):
    # 1. Try Qdrant vector search
    qdrant_results = await qdrant_service.search(query, limit=5)

    # 2. Try Firecrawl web scraping
    urls = determine_relevant_urls(query)
    firecrawl_results = await asyncio.gather(*[
        firecrawl_service.scrape_url(url) for url in urls
    ])

    # 3. Combine and rank results
    combined_results = rank_and_merge(qdrant_results, firecrawl_results)

    # 4. Generate citations
    citations = generate_citations(combined_results)

    return {
        'knowledge': combined_results,
        'citations': citations,
        'sources': {
            'qdrant': len(qdrant_results),
            'firecrawl': len(firecrawl_results)
        }
    }
```

---

## Real-Time Tracking & WebSocket

### WebSocket Agent Tracker (`src/agents/realtime_agent_tracker.py`)

Provides live agent status updates via WebSocket connections.

#### Agent Status States:
- `IDLE`: Agent waiting for tasks
- `ANALYZING`: Processing query, determining approach
- `PROCESSING`: Executing solution
- `COLLABORATING`: Working with other agents
- `COMPLETED`: Task finished
- `ERROR`: Encountered error

#### WebSocket Protocol:

**Connection Endpoint**: `ws://localhost:8000/api/ws/agent-tracking`

**Status Update Format**:
```json
{
    "type": "agent_status",
    "agent_id": "uuid-here",
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

**Collaboration Event Format**:
```json
{
    "type": "agent_collaboration",
    "primary_agent": "Technical Integration Specialist",
    "secondary_agent": "Security Specialist",
    "collaboration_type": "handoff",
    "reason": "Requires security expertise for SSL validation",
    "timestamp": "2024-01-20T10:31:15.456Z"
}
```

#### WebSocket API (`backend/websocket_api.py`)

**Endpoints**:
- `/ws/agent-tracking`: Real-time agent status updates
- `/ws/stats`: System statistics stream
- `/ws/chat/{session_id}`: Conversation-specific updates

**Features**:
- **Automatic Reconnection**: Client-side reconnection logic
- **Heartbeat**: Keep-alive ping/pong
- **Broadcast**: Multi-client support
- **Event Filtering**: Subscribe to specific agent or session

---

## Performance Metrics & Learning

### MetricsManager (`database/models.py`)

Tracks agent performance and generates learning insights.

#### Agent Metrics Schema:

```sql
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    session_id UUID REFERENCES conversation_sessions(id),
    query_hash VARCHAR(64),
    query_text TEXT NOT NULL,
    response_quality NUMERIC(3,2),
    response_time_ms INTEGER,
    tokens_used INTEGER,
    cost_per_request NUMERIC(10,4),
    user_feedback_rating INTEGER CHECK (user_feedback_rating BETWEEN 1 AND 5),
    llm_used VARCHAR(100),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    context JSONB DEFAULT '{}',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Performance Tracking:

```python
async def record_agent_performance(self, metrics_data: Dict):
    metrics_id = uuid4()
    query_hash = hashlib.sha256(query_text.encode()).hexdigest()

    await conn.execute("""
        INSERT INTO agent_metrics (
            id, agent_id, session_id, query_hash, query_text,
            response_quality, response_time_ms, tokens_used,
            cost_per_request, llm_used, success
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
    """, ...)
```

#### Performance Summary:

```python
async def get_agent_performance_summary(self, agent_id: UUID, days: int = 30):
    return {
        'total_interactions': count(*),
        'avg_quality': avg(response_quality),
        'avg_response_time': avg(response_time_ms),
        'avg_user_rating': avg(user_feedback_rating),
        'success_rate': sum(success) / count(*),
        'avg_cost': avg(cost_per_request)
    }
```

### Learning Insights System

#### Learning Insights Schema:

```sql
CREATE TABLE learning_insights (
    id UUID PRIMARY KEY,
    insight_type VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    confidence_score NUMERIC(3,2),
    data_points INTEGER DEFAULT 0,
    recommended_actions JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    implemented_at TIMESTAMP
);
```

#### Insight Generation:

**User Dissatisfaction** (Rating ≤ 2)
```python
async def _generate_improvement_insight(self, session_id, rating, comment):
    insight_data = {
        'insight_type': 'user_dissatisfaction',
        'title': f'Low user satisfaction (Rating: {rating}/5)',
        'description': f'User feedback indicates dissatisfaction. Comment: "{comment}"',
        'confidence_score': 0.8,
        'recommended_actions': [
            'Review agent selection for similar queries',
            'Analyze response quality metrics',
            'Consider agent retraining or LLM adjustment'
        ]
    }
    await learning_manager.generate_learning_insight(insight_data)
```

**User Satisfaction** (Rating ≥ 4)
```python
async def _generate_success_insight(self, session_id, rating, comment):
    insight_data = {
        'insight_type': 'user_satisfaction',
        'title': f'High user satisfaction (Rating: {rating}/5)',
        'description': f'User expressed high satisfaction. Comment: "{comment}"',
        'confidence_score': 0.9,
        'recommended_actions': [
            'Reinforce successful agent selection patterns',
            'Analyze what worked well',
            'Use as positive training example'
        ]
    }
```

### Agent Skills Tracking:

```sql
CREATE TABLE agent_skills (
    agent_id UUID REFERENCES agents(id),
    skill_name VARCHAR(255) NOT NULL,
    proficiency_score NUMERIC(3,2) DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    improvement_trend NUMERIC(3,2) DEFAULT 0.0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (agent_id, skill_name)
);
```

**Skill Update Logic**:
```python
async def update_agent_skills(self, agent_id, skill_name, proficiency_delta):
    await conn.execute("""
        INSERT INTO agent_skills (agent_id, skill_name, proficiency_score, usage_count)
        VALUES ($1, $2, $3, 1)
        ON CONFLICT (agent_id, skill_name)
        DO UPDATE SET
            proficiency_score = GREATEST(0.0, LEAST(1.0,
                agent_skills.proficiency_score + $3)),
            usage_count = agent_skills.usage_count + 1,
            improvement_trend = $3
    """, agent_id, skill_name, proficiency_delta)
```

### Conversation Sessions:

```sql
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY,
    user_id VARCHAR(255),
    query TEXT NOT NULL,
    agents_selected JSONB DEFAULT '[]',
    final_response TEXT,
    total_response_time_ms INTEGER,
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    escalated_to_human BOOLEAN DEFAULT false,
    escalation_reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Features**:
- **Session Tracking**: Unique ID for each conversation
- **Agent Selection History**: Records which agents were used
- **Response Time**: Total processing time
- **User Satisfaction**: 1-5 rating scale
- **Escalation Tracking**: Human handoff detection
- **Metadata**: Flexible JSON storage for context

---

## Frontend Components

### MultiAgentDemo (`src/components/MultiAgentDemo.js`)

Main interface for multi-agent interactions.

**Features**:
- Agent selection interface
- Real-time status visualization
- Conversation history
- Performance metrics display
- Knowledge source citations

**Key Functions**:
```javascript
const handleQuery = async (query) => {
    // 1. Send query to backend
    const response = await api.post('/api/multi-agent/query', {
        query,
        session_id: sessionId
    });

    // 2. Update conversation history
    setConversation(prev => [...prev, {
        query,
        response: response.data.response,
        citations: response.data.citations,
        agents_used: response.data.agents_used
    }]);

    // 3. Update agent status via WebSocket
    // Handled by useAgentStatus hook
};
```

### AgentChat (`src/components/AgentChat.js`)

Interactive chat interface with 20+ specialized agents.

**Features**:
- Agent picker with avatar/color
- Typing indicators
- Citation display
- Conversation memory
- Export conversation history

**Key State**:
```javascript
const [messages, setMessages] = useState([]);
const [selectedAgent, setSelectedAgent] = useState(null);
const [isTyping, setIsTyping] = useState(false);
const [citations, setCitations] = useState([]);
const [sessionId, setSessionId] = useState(uuidv4());
```

### AgentConfiguration (`src/components/AgentConfiguration.js`)

Dynamic agent configuration and management interface.

**Features**:
- Create/edit/delete agents
- Configure LLM settings
- Manage keywords for routing
- Update backstory and goals
- Monitor performance metrics

**CRUD Operations**:
```javascript
const createAgent = async (agentData) => {
    const response = await api.post('/api/agents', agentData);
    return response.data.agent_id;
};

const updateAgent = async (agentId, updates) => {
    await api.put(`/api/agents/${agentId}`, updates);
};

const deleteAgent = async (agentId) => {
    await api.delete(`/api/agents/${agentId}`);
};
```

### KnowledgeBaseManager (`src/components/KnowledgeBaseManager.js`)

Manages external knowledge sources and indexing.

**Features**:
- Add/remove crawl URLs
- Trigger Firecrawl scraping
- Monitor Qdrant indexing
- View knowledge base statistics
- Test semantic search

**Key Functions**:
```javascript
const addCrawlUrl = async (company, url) => {
    await api.post('/api/knowledge/urls', {
        company_name: company,
        url: url
    });
};

const triggerCrawl = async (company) => {
    const response = await api.post('/api/knowledge/crawl', {
        company_name: company
    });
    return response.data.job_id;
};

const searchKnowledge = async (query) => {
    const response = await api.get('/api/knowledge/search', {
        params: { q: query, limit: 10 }
    });
    return response.data.results;
};
```

### CompetitiveAnalysis (`src/components/CompetitiveAnalysis.js`)

Real-time competitive intelligence dashboard.

**Features**:
- Competitor analysis queries
- Cost-benefit comparisons
- Market positioning
- Strategic recommendations

### QueryAnalyzer (`src/components/QueryAnalyzer.js`)

Analyzes query patterns and agent performance.

**Metrics**:
- Query complexity analysis
- Agent selection patterns
- Response time trends
- Success rate by category

### useAgentChat Hook (`src/hooks/useAgentChat.js`)

Reusable React hook for agent chat functionality.

```javascript
const useAgentChat = (initialAgent) => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId] = useState(uuidv4());

    const sendMessage = async (content) => {
        setIsLoading(true);
        const response = await api.post('/api/chat', {
            message: content,
            agent: initialAgent,
            session_id: sessionId
        });

        setMessages(prev => [...prev, {
            role: 'user',
            content: content
        }, {
            role: 'assistant',
            content: response.data.response,
            citations: response.data.citations
        }]);

        setIsLoading(false);
    };

    return { messages, sendMessage, isLoading, sessionId };
};
```

---

## Backend API Endpoints

### Main Backend (`backend/main.py`)

FastAPI server with comprehensive endpoints.

#### Agent Management

**GET /api/agents**
- Returns all active agents
- Response: `{ "agents": [...] }`

**GET /api/agents/{agent_id}**
- Get specific agent by ID
- Response: `{ "agent": {...} }`

**POST /api/agents**
- Create new agent
- Body: `{ "name", "role", "backstory", "keywords", ... }`
- Response: `{ "agent_id": "uuid", "success": true }`

**PUT /api/agents/{agent_id}**
- Update agent configuration
- Body: `{ "llm_config", "keywords", ... }`
- Response: `{ "success": true }`

**DELETE /api/agents/{agent_id}**
- Deactivate agent (soft delete)
- Response: `{ "success": true }`

#### Query Processing

**POST /api/query**
- Process single query with agent routing
- Body: `{ "query": "...", "context": {...} }`
- Response:
```json
{
    "response": "Agent response text",
    "routing_info": {
        "selected_agent": "Technical Integration Specialist",
        "confidence": 0.85
    },
    "citations": [...],
    "session_id": "uuid"
}
```

**POST /api/multi-agent/query**
- Process query with multiple agents
- Body: `{ "query": "...", "session_id": "..." }`
- Response:
```json
{
    "response": "Combined agent response",
    "agents_used": ["Agent 1", "Agent 2"],
    "collaboration_log": [...],
    "citations": [...],
    "performance": {
        "response_time_ms": 1500,
        "tokens_used": 2500,
        "cost": 0.05
    }
}
```

#### Knowledge Management (`backend/knowledge_api.py`)

**GET /api/knowledge/search**
- Search knowledge base
- Params: `q` (query), `limit` (default: 10)
- Response:
```json
{
    "results": [
        {
            "title": "...",
            "content": "...",
            "relevance_score": 0.92,
            "source": "qdrant|firecrawl",
            "url": "..."
        }
    ]
}
```

**POST /api/knowledge/urls**
- Add crawl URL for company
- Body: `{ "company_name": "...", "url": "..." }`
- Response: `{ "url_id": "uuid", "success": true }`

**DELETE /api/knowledge/urls**
- Remove crawl URL
- Body: `{ "company_name": "...", "url": "..." }`
- Response: `{ "success": true }`

**GET /api/knowledge/companies**
- List all companies with knowledge bases
- Response: `{ "companies": [...] }`

**POST /api/knowledge/crawl**
- Trigger Firecrawl for company
- Body: `{ "company_name": "...", "max_pages": 50 }`
- Response: `{ "job_id": "uuid", "status": "started" }`

**GET /api/knowledge/crawl/{job_id}**
- Check crawl job status
- Response:
```json
{
    "job_id": "uuid",
    "status": "completed",
    "pages_crawled": 42,
    "documents_indexed": 38
}
```

#### Conversation Management

**GET /api/conversation/{session_id}**
- Get conversation history
- Response:
```json
{
    "session_id": "uuid",
    "messages": [
        { "role": "user", "content": "...", "timestamp": "..." },
        { "role": "assistant", "content": "...", "citations": [...] }
    ],
    "agents_used": [...],
    "created_at": "..."
}
```

**GET /api/conversations**
- List all active conversations
- Response:
```json
{
    "sessions": [
        {
            "session_id": "uuid",
            "query": "...",
            "created_at": "...",
            "message_count": 5
        }
    ]
}
```

**POST /api/conversation/feedback**
- Submit user feedback
- Body: `{ "session_id": "...", "rating": 5, "comment": "..." }`
- Response: `{ "success": true }`

#### Debug Endpoints

**GET /api/debug/knowledge/{query}**
- Debug knowledge retrieval
- Returns raw knowledge sources and processing steps

**GET /api/debug/routing/{query}**
- Debug agent routing decisions
- Returns agent scores and selection rationale

**GET /api/health**
- Health check endpoint
- Response:
```json
{
    "status": "healthy",
    "database": "connected",
    "qdrant": "connected",
    "firecrawl": "available",
    "agents_loaded": 22
}
```

#### Performance Analytics

**GET /api/analytics/performance**
- Get system-wide performance metrics
- Params: `days` (default: 30)
- Response:
```json
{
    "total_queries": 1250,
    "avg_response_time_ms": 1850,
    "success_rate": 0.962,
    "avg_user_rating": 4.3,
    "total_cost": 45.67,
    "agents_performance": {
        "Technical Integration Specialist": {
            "queries_handled": 350,
            "avg_quality": 0.89,
            "success_rate": 0.97
        }
    }
}
```

**GET /api/analytics/agent/{agent_id}**
- Get agent-specific analytics
- Response: Detailed performance breakdown

#### WebSocket Endpoints

**WS /ws/agent-tracking**
- Real-time agent status updates
- Broadcasts agent state changes

**WS /ws/stats**
- System statistics stream
- Real-time metrics updates

**WS /ws/chat/{session_id}**
- Conversation-specific updates
- Typing indicators, new messages

---

## Data Flow & Interaction

### Query Processing Flow

```
1. User submits query
   ↓
2. Frontend (MultiAgentDemo/AgentChat)
   ↓
3. POST /api/multi-agent/query
   ↓
4. DatabaseAgentManager.select_agents_for_query()
   ├─ Extract keywords
   ├─ Query database for matching agents
   └─ Return top 3 agents
   ↓
5. DatabaseAgentManager.process_query_with_agents()
   ├─ Create conversation session
   ├─ AdaptiveLLMSystem.process_multi_agent_query()
   │  ├─ Select optimal LLM
   │  ├─ Check knowledge requirements
   │  │  ├─ QdrantService.search() [vector DB]
   │  │  └─ FirecrawlService.scrape_url() [web scraping]
   │  ├─ Create CrewAI agents
   │  ├─ Create tasks
   │  ├─ Execute crew
   │  └─ Evaluate response quality
   ├─ Record agent metrics
   └─ Update session completion
   ↓
6. Return response with citations
   ↓
7. Frontend displays response
   ├─ Show agent responses
   ├─ Display citations
   └─ Update conversation history
   ↓
8. WebSocket broadcasts agent status throughout
```

### Knowledge Integration Flow

```
1. Query requires external knowledge
   ↓
2. Knowledge determination logic
   ↓
3. Parallel knowledge retrieval:
   ├─ Qdrant Vector Search
   │  ├─ Encode query to embedding
   │  ├─ Search similar vectors
   │  └─ Return top matches
   │
   └─ Firecrawl Web Scraping
      ├─ Determine relevant URLs
      ├─ Scrape content
      └─ Extract markdown
   ↓
4. Merge and rank results
   ├─ Combine Qdrant + Firecrawl
   ├─ Deduplicate
   └─ Sort by relevance
   ↓
5. Generate citations
   ├─ Format as markdown links
   └─ Include source URLs
   ↓
6. Inject knowledge into agent context
   ↓
7. Agent processes with enriched context
   ↓
8. Response includes citations
```

### Agent Collaboration Flow

```
1. Primary agent receives query
   ↓
2. Determines if collaboration needed
   ↓
3. WebSocket broadcasts: COLLABORATING
   ↓
4. DatabaseAgentManager selects secondary agents
   ├─ Keyword matching
   ├─ Specialization scores
   └─ Collaboration ratings
   ↓
5. Handoff or parallel processing
   ├─ Handoff: Pass full context to specialist
   └─ Parallel: Split tasks among agents
   ↓
6. Record agent_collaborations
   ├─ Primary agent ID
   ├─ Secondary agent ID
   ├─ Collaboration type
   └─ Effectiveness score
   ↓
7. Merge responses
   ↓
8. Update collaboration_rating for agents
```

### Learning & Improvement Flow

```
1. User provides feedback (1-5 rating)
   ↓
2. POST /api/conversation/feedback
   ↓
3. MetricsManager.record_user_feedback()
   ├─ Update conversation_sessions
   └─ Generate learning insight
   ↓
4. Insight generation based on rating:
   ├─ Rating ≤ 2: Improvement insight
   │  └─ Recommended actions for fixing
   │
   └─ Rating ≥ 4: Success insight
      └─ Recommended reinforcement
   ↓
5. Store in learning_insights table
   ↓
6. Background process reviews insights
   ├─ Analyze patterns
   ├─ Update agent skills
   ├─ Adjust routing weights
   └─ Tune LLM selection
   ↓
7. Continuous improvement loop
```

### Database Schema Relationships

```
agents
├─ agent_metrics (one-to-many)
├─ agent_skills (one-to-many)
└─ agent_collaborations (many-to-many via join)

conversation_sessions
├─ agent_metrics (one-to-many)
└─ agent_collaborations (one-to-many)

companies
└─ crawl_urls (one-to-many)

query_patterns
└─ Referenced by agent routing logic

learning_insights
└─ Generated from agent_metrics analysis
```

---

## Configuration & Setup

### Environment Variables

**Required for AI capabilities:**
```bash
ANTHROPIC_API_KEY=sk-ant-...         # Claude API
OPENAI_API_KEY=sk-proj-...           # GPT models
```

**Knowledge integration:**
```bash
FIRECRAWL_API_KEY=fc-...             # Web scraping
QDRANT_URL=https://xxx.qdrant.io    # Vector database
QDRANT_API_KEY=...                   # Qdrant auth
```

**Database:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/agentcraft_db
```

**Optional - AI observability:**
```bash
GALILEO_API_KEY=...                  # Galileo integration
GALILEO_PROJECT=AgentCraft
```

### Database Setup

**1. Create PostgreSQL database:**
```bash
createdb agentcraft_db
```

**2. Run schema creation:**
```bash
psql agentcraft_db < database/schema.sql
```

**3. Add knowledge tables:**
```bash
psql agentcraft_db < database/add_knowledge_tables.sql
```

**4. Initialize with seed data (optional):**
```bash
python database/setup.py
```

### Qdrant Setup

**Option 1: Qdrant Cloud (Recommended)**
1. Create account at https://cloud.qdrant.io
2. Create cluster
3. Get cluster URL and API key
4. Set `QDRANT_URL` and `QDRANT_API_KEY` in `.env`

**Option 2: Local Qdrant**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Option 3: In-Memory (Development)**
- No setup needed
- Data not persisted
- Automatically used if no Qdrant URL provided

### Firecrawl Setup

1. Create account at https://firecrawl.dev
2. Get API key
3. Set `FIRECRAWL_API_KEY` in `.env`

### Running the Application

**Quick Start:**
```bash
python main.py
```

This will:
- Install dependencies
- Initialize database
- Start FastAPI backend (port 8000)
- Start React frontend (port 3000)

**Access Points:**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws/agent-tracking

### Adding Custom Agents

**Method 1: Via API**
```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Specialist",
    "role": "Domain expert",
    "backstory": "Background story",
    "goal": "Agent objective",
    "keywords": ["keyword1", "keyword2"],
    "domain": "custom",
    "llm_config": {
        "model": "claude-3-5-sonnet-20241022",
        "temperature": 0.1
    }
  }'
```

**Method 2: Via Frontend**
- Navigate to Agent Configuration page
- Click "Create New Agent"
- Fill in agent details
- Save

**Method 3: Database Direct**
```sql
INSERT INTO agents (id, name, role, backstory, keywords, domain)
VALUES (
    gen_random_uuid(),
    'Custom Specialist',
    'Domain expert',
    'Expert background',
    '["keyword1", "keyword2"]'::jsonb,
    'custom'
);
```

### Monitoring & Debugging

**Check System Health:**
```bash
curl http://localhost:8000/api/health
```

**Debug Agent Routing:**
```bash
curl "http://localhost:8000/api/debug/routing/webhook%20integration"
```

**Debug Knowledge Retrieval:**
```bash
curl "http://localhost:8000/api/debug/knowledge/zapier%20api"
```

**View Conversation History:**
```bash
curl "http://localhost:8000/api/conversation/{session_id}"
```

**Monitor WebSocket:**
```bash
wscat -c ws://localhost:8000/ws/stats
```

### Testing

**Run test suite:**
```bash
pytest tests/ -v
```

**Test specific agent:**
```bash
python tests/test_technical_agent.py
```

**Test endpoints:**
```bash
python test_endpoints.py
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │MultiAgentDemo│  │  AgentChat   │  │AgentConfiguration  │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬───────────┘  │
│         │                  │                     │               │
│         └──────────────────┴─────────────────────┘               │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTP/WebSocket
┌────────────────────────────┼─────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│  ┌──────────────────────────┴─────────────────────────────────┐ │
│  │               Main API (backend/main.py)                    │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │ │
│  │  │Agent Mgmt   │  │Knowledge API│  │WebSocket API    │   │ │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘   │ │
│  └─────────┼─────────────────┼──────────────────┼────────────┘ │
│            │                 │                  │               │
│  ┌─────────┼─────────────────┼──────────────────┼────────────┐ │
│  │                 CORE AGENT SYSTEM                          │ │
│  │  ┌──────┴──────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │DatabaseAgent    │  │AgentRouter   │  │BaseAgent     │ │ │
│  │  │Manager          │  │              │  │              │ │ │
│  │  └────────┬────────┘  └──────┬───────┘  └──────────────┘ │ │
│  │           │                   │                           │ │
│  │  ┌────────┴────────┐  ┌──────┴──────┐  ┌──────────────┐ │ │
│  │  │Adaptive LLM     │  │20+ Agents   │  │Realtime      │ │ │
│  │  │System           │  │(Technical,  │  │Tracker       │ │ │
│  │  │                 │  │Business,    │  │              │ │ │
│  │  │                 │  │Analysis)    │  │              │ │ │
│  │  └────────┬────────┘  └─────────────┘  └──────────────┘ │ │
│  └───────────┼──────────────────────────────────────────────┘ │
└──────────────┼────────────────────────────────────────────────┘
               │
┌──────────────┼────────────────────────────────────────────────┐
│              │              EXTERNAL SERVICES                  │
│  ┌───────────┴──────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │                      │  │              │  │             │ │
│  │  CrewAI Framework    │  │Firecrawl     │  │Qdrant       │ │
│  │  - Agent Creation    │  │Service       │  │Vector DB    │ │
│  │  - Task Execution    │  │(Web Scraping)│  │(Semantic    │ │
│  │  - Collaboration     │  │              │  │ Search)     │ │
│  │                      │  │              │  │             │ │
│  └──────────────────────┘  └──────────────┘  └─────────────┘ │
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐                  │
│  │Anthropic Claude  │  │OpenAI GPT        │                  │
│  │- Sonnet 3.5      │  │- GPT-4o          │                  │
│  │- Reasoning       │  │- GPT-4o Mini     │                  │
│  └──────────────────┘  └──────────────────┘                  │
└────────────────────────────────────────────────────────────────┘
               │
┌──────────────┼────────────────────────────────────────────────┐
│           DATABASE (PostgreSQL)                                │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │agents      │  │agent_metrics │  │conversation_       │    │
│  │            │  │              │  │sessions            │    │
│  └────────────┘  └──────────────┘  └────────────────────┘    │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │agent_skills│  │learning_     │  │companies +         │    │
│  │            │  │insights      │  │crawl_urls          │    │
│  └────────────┘  └──────────────┘  └────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

---

## Summary

AgentCraft is a comprehensive multi-agent AI system that demonstrates:

1. **Specialized Agent Architecture**: 20+ domain-specific agents with deep expertise
2. **Intelligent Routing**: Keyword-based agent selection with confidence scoring
3. **Database Persistence**: PostgreSQL-backed configuration and metrics
4. **Adaptive AI**: Multi-LLM system with performance-based selection
5. **Knowledge Integration**: Qdrant vector search + Firecrawl web scraping
6. **Conversation Memory**: Session-based persistent context
7. **Real-Time Monitoring**: WebSocket-based live status updates
8. **Performance Learning**: Continuous improvement through metrics and insights
9. **Production-Ready**: Comprehensive error handling, fallbacks, and resilience
10. **Developer-Friendly**: Clear APIs, extensive documentation, easy customization

The system combines the power of specialized agents, external knowledge sources, and adaptive AI to deliver superior outcomes compared to generic platform solutions.

---

**For more details, see:**
- `README.md` - Project overview and quick start
- `ADAPTIVE_LLM_SYSTEM.md` - Multi-LLM system details
- `DATABASE_SETUP.md` - Database configuration
- `ENHANCED_SETUP_GUIDE.md` - Comprehensive setup instructions
- `GALILEO_ADAPTIVE_INTEGRATION.md` - AI observability integration
