# AgentCraft Backend Services

Complete documentation for all backend services in AgentCraft.

## Table of Contents

1. [Overview](#overview)
2. [Qdrant Service](#qdrant-service)
3. [Firecrawl Service](#firecrawl-service)
4. [HITL Service](#hitl-service)
5. [Target Company Service](#target-company-service)
6. [Training Data Service](#training-data-service)
7. [Service Integration](#service-integration)
8. [Best Practices](#best-practices)

---

## Overview

AgentCraft's backend services provide specialized functionality for knowledge management, web scraping, human-in-the-loop operations, and company context management. All services follow a singleton pattern for easy access throughout the application.

### Service Architecture

```
src/services/
├── qdrant_service.py          # Vector database for semantic search
├── firecrawl_service.py       # Web scraping and content extraction
├── hitl_service.py            # Human-in-the-loop operations
├── target_company_service.py  # Company context management
└── training_data_service.py   # Training data collection
```

---

## Qdrant Service

Vector database service for semantic search and knowledge base indexing.

### Location

`src/services/qdrant_service.py`

### Purpose

- Semantic search through knowledge base
- Vector embeddings for content
- Knowledge article indexing
- Similarity-based retrieval

### Configuration

```python
from src.services.qdrant_service import qdrant_service

# Service automatically connects to:
# - Qdrant Cloud (if QDRANT_URL and QDRANT_API_KEY are set)
# - Local Qdrant server (if running on localhost:6333)
# - In-memory mode (fallback for testing)
```

### Environment Variables

```bash
# Qdrant Cloud (Recommended for Production)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Local Qdrant Server (Development)
# No variables needed - connects to localhost:6333
```

### Key Features

#### 1. Knowledge Base Indexing

```python
from src.services.qdrant_service import qdrant_service, KnowledgeArticle

# Create knowledge articles
articles = [
    KnowledgeArticle(
        id="kb_001",
        title="Webhook Signature Verification",
        content="Complete guide to webhook signatures...",
        category="Technical Integration",
        tags=["webhook", "security", "api"],
        created_at="2024-01-15T10:00:00Z",
        updated_at="2024-01-15T10:00:00Z"
    )
]

# Index articles
qdrant_service.index_knowledge_base(articles)
```

#### 2. Semantic Search

```python
# Search for relevant knowledge
results = qdrant_service.search(
    query="How to verify webhook signatures?",
    limit=5,
    category_filter="Technical Integration"
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Similarity: {result['similarity_score']:.2f}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Tags: {', '.join(result['tags'])}")
```

#### 3. Mock Knowledge Generation

```python
# Generate mock knowledge base for a company
articles = qdrant_service.generate_mock_knowledge_base()

# Returns company-specific articles covering:
# - Webhook integration guides
# - API troubleshooting
# - Billing and subscription management
# - Security best practices
# - Common error resolutions
```

#### 4. Performance Metrics

```python
# Get service metrics
metrics = qdrant_service.get_metrics()

print(f"Status: {metrics['status']}")
print(f"Indexed Points: {metrics['indexed_points']}")
print(f"Vector Count: {metrics['vector_count']}")
print(f"Average Latency: {metrics['search_performance']['average_latency_ms']}ms")
```

### Classes and Methods

#### `QdrantService`

**Constructor:**
```python
QdrantService(
    collection_name: str = "agentcraft_knowledge",
    host: str = "localhost",
    port: int = 6333,
    use_memory: bool = False
)
```

**Methods:**

- `index_knowledge_base(articles: List[KnowledgeArticle])` - Index articles into vector database
- `search(query: str, limit: int, category_filter: str, tags_filter: List[str])` - Semantic search
- `generate_mock_knowledge_base(company_context: Dict)` - Generate sample articles
- `get_metrics()` - Get performance metrics

#### `KnowledgeArticle` (Dataclass)

```python
@dataclass
class KnowledgeArticle:
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: str
    updated_at: str
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None
```

### Technical Details

**Embedding Model:** `all-MiniLM-L6-v2` (384 dimensions)
- Fast inference
- Good balance of accuracy and speed
- Suitable for production use

**Distance Metric:** Cosine similarity
- Best for semantic similarity
- Range: 0 (different) to 1 (identical)

**Collection Configuration:**
```python
VectorParams(
    size=384,           # MiniLM embedding dimension
    distance=Distance.COSINE
)
```

---

## Firecrawl Service

Web scraping service for real-time content extraction and knowledge base updates.

### Location

`src/services/firecrawl_service.py`

### Purpose

- Real-time web scraping
- Content extraction from documentation
- Markdown conversion
- Bulk URL processing

### Configuration

```python
from src.services.firecrawl_service import firecrawl_service
```

### Environment Variables

```bash
# Firecrawl API
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### Key Features

#### 1. Single URL Scraping

```python
# Scrape a single URL
result = await firecrawl_service.scrape_url(
    url="https://zapier.com/help/webhooks",
    options={
        'formats': ['markdown', 'html'],
        'onlyMainContent': True
    }
)

if result['success']:
    print(f"Title: {result['title']}")
    print(f"Content: {result['content'][:500]}...")
    print(f"Metadata: {result['metadata']}")
```

#### 2. Site Crawling

```python
# Crawl entire site
crawl_result = await firecrawl_service.crawl_site(
    base_url="https://docs.zapier.com",
    max_pages=50,
    options={
        'limit': 50,
        'scrapeOptions': {
            'formats': ['markdown'],
            'onlyMainContent': True
        }
    }
)

if crawl_result['success']:
    print(f"Pages crawled: {crawl_result['pages_crawled']}")
    for page in crawl_result['data']:
        print(f"- {page['title']}: {page['url']}")
```

#### 3. Bulk URL Processing

```python
# Scrape multiple URLs concurrently
urls = [
    "https://zapier.com/help/webhooks",
    "https://zapier.com/help/api",
    "https://zapier.com/help/troubleshooting"
]

results = await firecrawl_service.bulk_scrape_urls(urls)

successful = [r for r in results if r['success']]
print(f"Successfully scraped: {len(successful)}/{len(urls)}")
```

#### 4. Mock Mode (Demo/Development)

When Firecrawl API is not available, the service automatically uses mock data:

```python
# Automatically falls back to mock data
result = await firecrawl_service.scrape_url(
    "https://zapier.com/help/webhooks"
)

# Returns realistic mock content for:
# - zapier.com
# - docs.zapier.com
# - community.zapier.com
# - learn.zapier.com
```

### Classes and Methods

#### `FirecrawlService`

**Constructor:**
```python
FirecrawlService()  # Initializes with FIRECRAWL_API_KEY from environment
```

**Methods:**

- `scrape_url(url: str, options: Dict)` - Scrape single URL
- `crawl_site(base_url: str, max_pages: int, options: Dict)` - Crawl entire site
- `bulk_scrape_urls(urls: List[str], options: Dict)` - Scrape multiple URLs

### Scraping Options

```python
default_options = {
    'formats': ['markdown', 'html'],
    'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'article', 'main'],
    'excludeTags': ['nav', 'footer', 'aside', 'script', 'style'],
    'onlyMainContent': True,
    'removeBase64Images': True
}
```

### Response Format

```python
{
    'success': True,
    'url': 'https://example.com',
    'title': 'Page Title',
    'content': 'Markdown content...',
    'html': '<html>...</html>',
    'metadata': {
        'description': 'Page description',
        'keywords': ['tag1', 'tag2']
    },
    'scraped_at': '2024-01-20T10:30:00Z'
}
```

### Concurrency Control

The service implements automatic concurrency limiting:

```python
# Maximum 5 concurrent requests
semaphore = asyncio.Semaphore(5)
```

This prevents overwhelming the Firecrawl API and ensures reliable operation.

---

## HITL Service

Human-in-the-Loop service for escalation management and continuous learning.

### Location

`src/services/hitl_service.py`

### Purpose

- Automated escalation to human operators
- Feedback collection and processing
- Continuous learning from human input
- Quality assurance and improvement

### Configuration

```python
from src.services.hitl_service import hitl_service
```

### Key Features

#### 1. Escalation Evaluation

```python
# Evaluate if query should be escalated
should_escalate, context = await hitl_service.evaluate_escalation(
    query="Complex integration issue...",
    agent_response={
        "content": "I'm not sure about this...",
        "confidence": 0.5
    },
    confidence_score=0.5,
    sentiment_score=-0.3,
    conversation_history=[...]
)

if should_escalate:
    print(f"Escalation reason: {context.reason.value}")
    print(f"Priority: {context.priority.name}")
    print(f"Queue position: {len(hitl_service.escalation_queue)}")
```

#### 2. Escalation Reasons

```python
class EscalationReason(Enum):
    LOW_CONFIDENCE = "low_confidence"           # AI confidence < 0.7
    MISSING_INFO = "missing_information"        # Insufficient data
    NEGATIVE_SENTIMENT = "negative_sentiment"   # User frustration
    USER_REQUEST = "user_requested"             # Explicit request
    COMPLEX_ISSUE = "complex_issue"             # High complexity
    POLICY_VIOLATION = "policy_violation"       # Policy concerns
    REPEAT_FAILURE = "repeat_failure"           # Multiple failures
```

#### 3. Priority Levels

```python
class EscalationPriority(Enum):
    LOW = 1       # Can wait
    MEDIUM = 2    # Should be addressed soon
    HIGH = 3      # Needs prompt attention
    CRITICAL = 4  # Urgent - immediate attention
```

#### 4. Human Feedback Processing

```python
# Process feedback from human operator
feedback = await hitl_service.process_human_feedback(
    escalation_id="esc_12345",
    operator_id="operator_jane",
    resolution="Updated webhook signature validation code",
    quality_rating=4,  # 1-5 scale
    teaching_notes="Remember to check header case sensitivity"
)

# Feedback automatically incorporated into learning system
print(f"Should retrain: {feedback.should_retrain}")
print(f"Performance improvement: {hitl_service.metrics['performance_improvement']}%")
```

#### 5. Operator Dashboard

```python
# Get dashboard for human operators
dashboard = await hitl_service.get_operator_dashboard()

print(f"Active escalations: {dashboard['stats']['active_escalations']}")
print(f"Average wait time: {dashboard['stats']['avg_wait_time']}")
print(f"Operators online: {dashboard['stats']['operators_online']}")

# View queue
for item in dashboard['queue']:
    print(f"Priority {item['priority']}: {item['reason']}")
```

#### 6. Metrics and Analytics

```python
# Get HITL metrics
metrics = hitl_service.get_escalation_metrics()

print(f"Total escalations: {metrics['total_escalations']}")
print(f"Resolution rate: {metrics['escalation_rate']:.1f}%")
print(f"Average resolution time: {metrics['avg_resolution_time']}")
print(f"Performance improvement: {metrics['performance_improvement']}")
```

### Classes and Data Structures

#### `EscalationContext`

```python
@dataclass
class EscalationContext:
    conversation_id: str
    user_id: str
    agent_id: str
    reason: EscalationReason
    priority: EscalationPriority
    conversation_history: List[Dict[str, Any]]
    agent_analysis: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
```

#### `HumanFeedback`

```python
@dataclass
class HumanFeedback:
    escalation_id: str
    operator_id: str
    resolution: str
    feedback_type: str  # 'correction', 'validation', 'teaching'
    agent_response_quality: int  # 1-5 rating
    should_retrain: bool
    notes: str
    timestamp: str
```

### Escalation Thresholds

```python
# Default thresholds (configurable)
confidence_threshold = 0.7      # Below this triggers escalation
sentiment_threshold = -0.5      # Negative sentiment trigger
complexity_threshold = 0.8      # Query complexity trigger
```

### Sentiment Analysis

```python
# Simulate sentiment analysis
sentiment = hitl_service.simulate_sentiment_analysis(
    "This is terrible and not working at all!"
)
# Returns: -0.6 (negative sentiment)

sentiment = hitl_service.simulate_sentiment_analysis(
    "Great service, thanks for the help!"
)
# Returns: 0.6 (positive sentiment)
```

---

## Target Company Service

Hot-swappable company context management for multi-tenant scenarios.

### Location

`src/services/target_company_service.py`

### Purpose

- Manage multiple company contexts
- Hot-swap company configurations
- Provide company-specific knowledge sources
- Support multi-tenant deployments

### Configuration

```python
from src.services.target_company_service import target_company_service
```

### Key Features

#### 1. Company Management

```python
# Get current company
company = target_company_service.get_current_company()

print(f"Company: {company.display_name}")
print(f"Industry: {company.industry}")
print(f"Primary color: {company.primary_color}")
print(f"Logo: {company.logo_emoji}")
```

#### 2. Switch Company Context

```python
# Switch to different company
success = target_company_service.set_current_company("hubspot")

if success:
    company = target_company_service.get_current_company()
    print(f"Switched to: {company.display_name}")
```

#### 3. Get Company Context for Agents

```python
# Get contextual information for AI agents
context = target_company_service.get_company_context()

# Returns:
{
    "company_name": "Zapier",
    "industry": "Integration & Automation",
    "primary_use_cases": [
        "Webhook troubleshooting and debugging",
        "API integration setup and optimization",
        ...
    ],
    "technical_focus": [
        "REST API integrations",
        "Webhook signature verification",
        ...
    ],
    "customer_pain_points": [
        "Complex webhook signature verification",
        "API rate limiting issues",
        ...
    ],
    "competitive_landscape": {
        "main_competitors": ["Microsoft Power Automate", ...],
        "our_advantages": ["Largest app ecosystem", ...]
    },
    "knowledge_sources": {
        "documentation": [...],
        "community": [...],
        "learning": [...]
    }
}
```

#### 4. Get Crawl URLs

```python
# Get all URLs to crawl for knowledge base
urls = target_company_service.get_crawl_urls()

print(f"Found {len(urls)} URLs to crawl:")
for url in urls:
    print(f"  - {url}")

# URLs include:
# - Documentation URLs
# - Community URLs
# - Marketing URLs
# - Blog URLs
# - Learning URLs
```

#### 5. List All Companies

```python
# Get all available companies
companies = target_company_service.get_all_companies()

for company_id, company in companies.items():
    print(f"{company.display_name} ({company_id})")
    print(f"  Industry: {company.industry}")
    print(f"  Focus areas: {', '.join(company.technical_focus_areas[:3])}")
```

### Predefined Companies

The service comes with three pre-configured companies:

#### Zapier
```python
{
    "id": "zapier",
    "display_name": "Zapier",
    "industry": "Integration & Automation",
    "primary_color": "#FF4A00",
    "logo_emoji": "⚡"
}
```

#### HubSpot
```python
{
    "id": "hubspot",
    "display_name": "HubSpot",
    "industry": "CRM & Marketing",
    "primary_color": "#FF7A59",
    "logo_emoji": "🧲"
}
```

#### Shopify
```python
{
    "id": "shopify",
    "display_name": "Shopify",
    "industry": "E-commerce",
    "primary_color": "#7AB55C",
    "logo_emoji": "🛍️"
}
```

### TargetCompany Data Structure

```python
@dataclass
class TargetCompany:
    id: str
    name: str
    display_name: str
    description: str
    industry: str
    primary_color: str
    logo_emoji: str

    # Knowledge sources
    documentation_urls: List[str]
    community_urls: List[str]
    marketing_urls: List[str]
    blog_urls: List[str]
    learning_urls: List[str]

    # Agent specializations
    primary_use_cases: List[str]
    technical_focus_areas: List[str]
    customer_pain_points: List[str]

    # Competitive positioning
    main_competitors: List[str]
    competitive_advantages: List[str]
    pricing_model: str
    target_market: str
```

### Adding New Companies

```python
# Extend the service with new companies
new_company = TargetCompany(
    id="slack",
    name="slack",
    display_name="Slack",
    description="Team collaboration platform",
    industry="Communication & Collaboration",
    primary_color="#4A154B",
    logo_emoji="💬",
    documentation_urls=["https://api.slack.com/docs"],
    # ... additional fields
)

# Add to service
target_company_service.companies["slack"] = new_company
target_company_service.set_current_company("slack")
```

---

## Training Data Service

Service for collecting and managing training data for continuous improvement.

### Location

`src/services/training_data_service.py`

### Purpose

- Collect query-response pairs
- Store conversation data
- Generate training datasets
- Support model fine-tuning

### Usage Pattern

```python
from src.services.training_data_service import training_data_service

# Record training example
training_data_service.record_interaction(
    query="How do I verify webhook signatures?",
    response="To verify webhook signatures...",
    feedback_score=5,
    metadata={
        "agent": "Technical Integration Specialist",
        "response_time": 1.2,
        "user_satisfied": True
    }
)

# Export training data
dataset = training_data_service.export_training_data(
    format="jsonl",
    min_feedback_score=4
)
```

---

## Service Integration

### Integrated Usage Example

```python
from src.services.qdrant_service import qdrant_service
from src.services.firecrawl_service import firecrawl_service
from src.services.hitl_service import hitl_service
from src.services.target_company_service import target_company_service

async def process_knowledge_query(query: str):
    """Comprehensive knowledge query processing"""

    # 1. Get company context
    company_context = target_company_service.get_company_context()

    # 2. Search existing knowledge base
    kb_results = qdrant_service.search(query, limit=5)

    # 3. If no good results, scrape fresh content
    if not kb_results or kb_results[0]['similarity_score'] < 0.7:
        urls = target_company_service.get_crawl_urls()[:3]
        scraped_content = await firecrawl_service.bulk_scrape_urls(urls)

        # Index new content
        new_articles = convert_to_knowledge_articles(scraped_content)
        qdrant_service.index_knowledge_base(new_articles)

        # Re-search with new content
        kb_results = qdrant_service.search(query, limit=5)

    # 4. Generate response with context
    response = generate_response(query, kb_results, company_context)

    # 5. Evaluate for escalation
    should_escalate, escalation_context = await hitl_service.evaluate_escalation(
        query=query,
        agent_response=response,
        confidence_score=response['confidence'],
        sentiment_score=0.0
    )

    if should_escalate:
        return {
            "response": "I'm escalating this to a human expert...",
            "escalated": True,
            "escalation_id": escalation_context.conversation_id
        }

    return {
        "response": response['content'],
        "sources": kb_results,
        "company": company_context['company_name']
    }
```

### Service Health Checks

```python
async def check_all_services():
    """Check health of all services"""

    services_status = {
        "qdrant": qdrant_service.get_metrics(),
        "firecrawl": {
            "available": firecrawl_service.app is not None,
            "mock_mode": firecrawl_service.app is None
        },
        "hitl": hitl_service.get_escalation_metrics(),
        "target_company": {
            "current": target_company_service.get_current_company().display_name,
            "available_companies": len(target_company_service.companies)
        }
    }

    return services_status
```

---

## Best Practices

### 1. Error Handling

Always handle service errors gracefully:

```python
try:
    results = qdrant_service.search(query)
except Exception as e:
    logging.error(f"Qdrant search failed: {e}")
    # Fall back to alternative method
    results = fallback_search(query)
```

### 2. Service Availability

Check service availability before use:

```python
if qdrant_service.client:
    # Qdrant is available
    results = qdrant_service.search(query)
else:
    # Use alternative knowledge source
    results = search_local_cache(query)
```

### 3. Async Operations

Use async/await for I/O operations:

```python
# Good
results = await firecrawl_service.scrape_url(url)

# Bad (blocking)
results = firecrawl_service.scrape_url(url)  # If sync
```

### 4. Resource Management

Limit concurrent operations:

```python
# Firecrawl service already implements this
semaphore = asyncio.Semaphore(5)

async def process_with_limit(url):
    async with semaphore:
        return await firecrawl_service.scrape_url(url)
```

### 5. Monitoring and Metrics

Regularly monitor service health:

```python
# Periodic health check
async def monitor_services():
    while True:
        metrics = await check_all_services()
        log_metrics(metrics)
        await asyncio.sleep(60)  # Every minute
```

### 6. Configuration Management

Use environment variables for configuration:

```python
# Good
qdrant_url = os.getenv('QDRANT_URL')
firecrawl_key = os.getenv('FIRECRAWL_API_KEY')

# Bad (hardcoded)
qdrant_url = "https://my-cluster.qdrant.io"
```

### 7. Testing

Mock services for testing:

```python
# Use memory mode for Qdrant in tests
test_qdrant = QdrantService(use_memory=True)

# Firecrawl automatically uses mock mode without API key
# Just don't set FIRECRAWL_API_KEY in test environment
```

---

## Related Documentation

- [API.md](API.md) - API endpoints using these services
- [KNOWLEDGE_SYSTEM.md](KNOWLEDGE_SYSTEM.md) - Knowledge retrieval system
- [TESTING.md](TESTING.md) - Service testing strategies
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
