# AgentCraft Knowledge Retrieval System

Complete documentation for the knowledge retrieval, citation generation, and URL management system.

## Table of Contents

1. [Overview](#overview)
2. [Qdrant Integration](#qdrant-integration)
3. [Firecrawl Integration](#firecrawl-integration)
4. [Knowledge Pipeline](#knowledge-pipeline)
5. [Citation Generation](#citation-generation)
6. [URL Management](#url-management)
7. [Knowledge API](#knowledge-api)
8. [Best Practices](#best-practices)

---

## Overview

The AgentCraft Knowledge System combines vector database search (Qdrant) with real-time web scraping (Firecrawl) to provide accurate, up-to-date information with transparent source attribution.

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Knowledge Orchestrator                     │
│  ┌─────────────────┐         ┌────────────────────┐   │
│  │  Query Analysis │────────▶│ Retrieval Strategy │   │
│  └─────────────────┘         └────────────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
           ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│ Qdrant Vector DB │   │ Firecrawl Scraper│
│  Semantic Search │   │  Real-time Data  │
└────────┬─────────┘   └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Content Processing                         │
│  ┌──────────────┐  ┌────────────┐  ┌───────────────┐  │
│  │  Deduplication│→│ Ranking    │→│  Citation     │  │
│  └──────────────┘  └────────────┘  └───────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│          Response with Citations                        │
└─────────────────────────────────────────────────────────┘
```

### Key Features

- **Dual-Source Retrieval**: Vector search + web scraping
- **Automatic Citation**: All external sources cited
- **Freshness Guarantee**: Real-time web content when needed
- **Source Attribution**: Complete transparency
- **Multi-Format Support**: Markdown, HTML, text

---

## Qdrant Integration

### Configuration

```bash
# Qdrant Cloud (Production)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Collection Configuration
QDRANT_COLLECTION=agentcraft_knowledge
QDRANT_VECTOR_SIZE=384  # MiniLM embedding dimension
```

### Semantic Search

```python
from src.services.qdrant_service import qdrant_service

# Search knowledge base
results = qdrant_service.search(
    query="webhook signature verification",
    limit=5,
    category_filter="Technical Integration"
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Similarity: {result['similarity_score']:.2f}")
    print(f"Category: {result['category']}")
    print(f"Tags: {', '.join(result['tags'])}")
    print(f"Content Preview: {result['content'][:200]}...")
    print()
```

### Knowledge Article Structure

```python
{
    "id": "kb_001",
    "title": "Webhook Signature Verification Guide",
    "content": "Complete guide to implementing...",
    "category": "Technical Integration",
    "tags": ["webhook", "signature", "security", "api"],
    "similarity_score": 0.89,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-08-20T14:30:00Z"
}
```

### Indexing New Content

```python
from src.services.qdrant_service import KnowledgeArticle

# Create knowledge article
article = KnowledgeArticle(
    id="kb_new",
    title="Advanced Webhook Patterns",
    content="This guide covers advanced webhook implementation...",
    category="Technical Integration",
    tags=["webhook", "advanced", "patterns"],
    created_at=datetime.now().isoformat(),
    updated_at=datetime.now().isoformat()
)

# Index into Qdrant
qdrant_service.index_knowledge_base([article])
```

---

## Firecrawl Integration

### Configuration

```bash
# Firecrawl API
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### Real-Time Web Scraping

```python
from src.services.firecrawl_service import firecrawl_service

# Scrape single URL
result = await firecrawl_service.scrape_url(
    url="https://zapier.com/help/webhooks",
    options={
        'formats': ['markdown', 'html'],
        'onlyMainContent': True,
        'removeBase64Images': True
    }
)

if result['success']:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content Length: {len(result['content'])} chars")
    print(f"Scraped At: {result['scraped_at']}")
```

### Bulk Scraping

```python
# Scrape multiple URLs concurrently
urls = [
    "https://zapier.com/help/webhooks",
    "https://zapier.com/help/api",
    "https://zapier.com/help/troubleshooting"
]

results = await firecrawl_service.bulk_scrape_urls(urls)

for result in results:
    if result['success']:
        print(f"✓ {result['title']}")
    else:
        print(f"✗ {result['url']}: {result['error']}")
```

### Site Crawling

```python
# Crawl entire documentation site
crawl_result = await firecrawl_service.crawl_site(
    base_url="https://docs.zapier.com",
    max_pages=50
)

if crawl_result['success']:
    print(f"Crawled {crawl_result['pages_crawled']} pages")
    for page in crawl_result['data']:
        print(f"- {page['title']}")
```

---

## Knowledge Pipeline

### Complete Knowledge Retrieval Flow

```python
async def retrieve_knowledge(query: str, session_id: str = None):
    """Complete knowledge retrieval pipeline"""

    # Step 1: Query Analysis
    query_features = analyze_query(query)
    requires_current_info = query_features['temporal'] or query_features['specific']

    # Step 2: Vector Search (Always)
    qdrant_results = qdrant_service.search(
        query=query,
        limit=5
    )

    # Step 3: Web Scraping (If needed)
    firecrawl_results = []
    if requires_current_info or not qdrant_results:
        # Get relevant URLs
        urls = get_relevant_urls(query)

        # Scrape fresh content
        scraped_data = await firecrawl_service.bulk_scrape_urls(urls[:3])
        firecrawl_results = [
            {
                'title': data['title'],
                'content': data['content'],
                'url': data['url'],
                'source': 'firecrawl',
                'relevance_score': calculate_relevance(query, data['content'])
            }
            for data in scraped_data if data['success']
        ]

    # Step 4: Combine and Rank
    all_results = combine_results(qdrant_results, firecrawl_results)
    ranked_results = rank_by_relevance(all_results, query)

    # Step 5: Generate Citations
    citations = generate_citations(ranked_results)

    # Step 6: Build Context
    knowledge_context = build_knowledge_context(ranked_results[:3])

    return {
        'context': knowledge_context,
        'citations': citations,
        'sources': {
            'qdrant': len(qdrant_results),
            'firecrawl': len(firecrawl_results)
        },
        'debug': {
            'query_features': query_features,
            'total_results': len(all_results)
        }
    }
```

### Query Analysis

```python
def analyze_query(query: str) -> dict:
    """Analyze query to determine retrieval strategy"""

    features = {
        'temporal': False,   # Requires current information
        'specific': False,   # Requires specific documentation
        'technical': False,  # Technical content
        'comparison': False  # Competitive analysis
    }

    query_lower = query.lower()

    # Temporal indicators
    temporal_words = ['latest', 'current', 'recent', 'new', 'updated', '2024']
    features['temporal'] = any(word in query_lower for word in temporal_words)

    # Specificity indicators
    specific_words = ['how to', 'step by step', 'guide', 'tutorial', 'example']
    features['specific'] = any(word in query_lower for word in specific_words)

    # Technical indicators
    technical_words = ['api', 'webhook', 'integration', 'code', 'implementation']
    features['technical'] = any(word in query_lower for word in technical_words)

    # Comparison indicators
    comparison_words = ['compare', 'versus', 'vs', 'difference', 'better']
    features['comparison'] = any(word in query_lower for word in comparison_words)

    return features
```

### Result Ranking

```python
def rank_by_relevance(results: list, query: str) -> list:
    """Rank results by relevance to query"""

    scored_results = []

    for result in results:
        score = 0.0

        # Base similarity/relevance score
        score += result.get('similarity_score', result.get('relevance_score', 0)) * 0.5

        # Freshness bonus
        if 'updated_at' in result:
            days_old = (datetime.now() - datetime.fromisoformat(result['updated_at'])).days
            freshness_score = max(0, 1 - (days_old / 365))
            score += freshness_score * 0.2

        # Source bonus (prefer official docs)
        if 'source' in result:
            if result['source'] == 'firecrawl':
                score += 0.15  # Fresh content bonus
            elif result['source'] == 'qdrant':
                score += 0.10  # Indexed content

        # Title match bonus
        if any(word.lower() in result['title'].lower() for word in query.split()):
            score += 0.15

        scored_results.append({
            **result,
            'final_score': score
        })

    # Sort by final score
    return sorted(scored_results, key=lambda x: x['final_score'], reverse=True)
```

### Content Deduplication

```python
def deduplicate_results(results: list) -> list:
    """Remove duplicate content from results"""

    seen_content = set()
    unique_results = []

    for result in results:
        # Create content fingerprint
        content_preview = result['content'][:500].lower()
        fingerprint = hashlib.md5(content_preview.encode()).hexdigest()

        if fingerprint not in seen_content:
            seen_content.add(fingerprint)
            unique_results.append(result)

    return unique_results
```

---

## Citation Generation

### Automatic Citation

```python
def generate_citations(results: list) -> list:
    """Generate citations for knowledge sources"""

    citations = []

    for i, result in enumerate(results, 1):
        citation = {
            'id': i,
            'title': result['title'],
            'source': format_source(result),
            'relevance': result.get('final_score', result.get('similarity_score', 0)),
            'type': determine_citation_type(result)
        }

        # Add URL if available
        if 'url' in result:
            citation['url'] = result['url']

        # Add timestamp
        if 'scraped_at' in result:
            citation['accessed_at'] = result['scraped_at']
        elif 'updated_at' in result:
            citation['last_updated'] = result['updated_at']

        citations.append(citation)

    return citations
```

### Citation Formats

#### Markdown Citation
```markdown
Based on the following sources:

1. **Webhook Signature Verification Guide**
   Source: Zapier Official Documentation
   URL: https://zapier.com/help/webhooks
   Relevance: 92%

2. **API Authentication Best Practices**
   Source: Knowledge Base (Technical Integration)
   Last Updated: 2024-08-20
   Relevance: 87%
```

#### JSON Citation
```json
{
    "citations": [
        {
            "id": 1,
            "title": "Webhook Signature Verification Guide",
            "source": "Zapier Official Documentation",
            "url": "https://zapier.com/help/webhooks",
            "relevance": 0.92,
            "type": "external",
            "accessed_at": "2024-01-20T10:30:00Z"
        },
        {
            "id": 2,
            "title": "API Authentication Best Practices",
            "source": "Knowledge Base",
            "category": "Technical Integration",
            "relevance": 0.87,
            "type": "internal",
            "last_updated": "2024-08-20T14:30:00Z"
        }
    ]
}
```

### Citation Display

```python
def format_citation_for_display(citation: dict) -> str:
    """Format citation for user display"""

    parts = []

    # Title
    parts.append(f"**{citation['title']}**")

    # Source
    if 'url' in citation:
        parts.append(f"[{citation['source']}]({citation['url']})")
    else:
        parts.append(f"Source: {citation['source']}")

    # Relevance
    relevance_pct = int(citation['relevance'] * 100)
    parts.append(f"Relevance: {relevance_pct}%")

    # Timestamp
    if 'accessed_at' in citation:
        parts.append(f"Accessed: {citation['accessed_at']}")
    elif 'last_updated' in citation:
        parts.append(f"Updated: {citation['last_updated']}")

    return " | ".join(parts)
```

---

## URL Management

### URL Storage

URLs are managed per company in the Target Company Service:

```python
from src.services.target_company_service import target_company_service

# Get crawl URLs for current company
urls = target_company_service.get_crawl_urls()

# URLs organized by type:
# - documentation_urls
# - community_urls
# - marketing_urls
# - blog_urls
# - learning_urls
```

### Adding URLs via API

```http
POST /api/knowledge/urls
Content-Type: application/json

{
    "company_name": "Zapier",
    "url": "https://zapier.com/help/new-feature"
}
```

### Removing URLs

```http
DELETE /api/knowledge/urls
Content-Type: application/json

{
    "company_name": "Zapier",
    "url": "https://zapier.com/help/old-page"
}
```

### Getting Company URLs

```http
GET /api/knowledge/companies/Zapier/urls
```

**Response:**
```json
{
    "success": true,
    "company_name": "Zapier",
    "urls": [
        {
            "id": "url_001",
            "url": "https://zapier.com/help/webhooks",
            "is_active": true,
            "created_at": "2024-01-20T10:00:00Z",
            "last_crawled": "2024-01-20T15:30:00Z"
        }
    ],
    "total_urls": 10
}
```

---

## Knowledge API

### Search Knowledge Base

```http
GET /api/knowledge/search?q=webhook%20authentication&limit=10&company=Zapier
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
            "url": "https://zapier.com/help/webhooks",
            "category": "documentation",
            "created_at": "2024-01-20T10:00:00Z"
        }
    ],
    "total_results": 5,
    "query": "webhook authentication",
    "sources_used": ["qdrant", "firecrawl"]
}
```

### Trigger Crawl Job

```http
POST /api/knowledge/crawl
Content-Type: application/json

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

### Check Crawl Status

```http
GET /api/knowledge/crawl/{job_id}
```

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

### Debug Knowledge Retrieval

```http
GET /api/debug/knowledge/{query}
```

**Response:**
```json
{
    "query": "webhook signature verification",
    "analysis": {
        "temporal": false,
        "specific": true,
        "technical": true,
        "comparison": false
    },
    "sources_attempted": ["Qdrant Vector DB", "Firecrawl Web Scraping"],
    "sources_successful": ["Qdrant Vector DB", "Firecrawl Web Scraping"],
    "results_found": {
        "qdrant": 5,
        "firecrawl": 2,
        "total": 7
    },
    "top_results": [
        {
            "title": "Webhook Signature Verification Guide",
            "source": "firecrawl",
            "relevance": 0.94,
            "url": "https://zapier.com/help/webhooks"
        }
    ],
    "knowledge_analysis": {
        "content_type": "documentation",
        "key_topics": ["webhooks", "signature", "security"],
        "actionable_steps": 6,
        "knowledge_depth": "comprehensive"
    },
    "citation_tracking": {
        "citation_included": true,
        "citation_count": 3,
        "citation_format": "markdown_with_urls"
    }
}
```

---

## Best Practices

### 1. Query Optimization

**Use specific queries:**
```python
# Good
query = "How to implement HMAC SHA256 webhook signature verification in Python"

# Less effective
query = "webhooks"
```

**Include context:**
```python
# Better results with context
query_with_context = f"""
Previous conversation: User is implementing Zapier integration
Current question: {user_query}
"""
```

### 2. Source Selection Strategy

```python
def select_sources(query_features: dict) -> dict:
    """Determine which sources to use"""

    strategy = {
        'use_qdrant': True,  # Always search vector DB
        'use_firecrawl': False,
        'max_qdrant_results': 5,
        'max_firecrawl_urls': 3
    }

    # Use Firecrawl for current information
    if query_features['temporal']:
        strategy['use_firecrawl'] = True

    # Use Firecrawl for comparison queries
    if query_features['comparison']:
        strategy['use_firecrawl'] = True
        strategy['max_firecrawl_urls'] = 5

    # Increase Qdrant results for technical queries
    if query_features['technical']:
        strategy['max_qdrant_results'] = 10

    return strategy
```

### 3. Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_qdrant_search(query: str, limit: int):
    """Cache Qdrant search results"""
    return qdrant_service.search(query, limit)

# Cache scraped content
scraped_content_cache = {}

async def get_or_scrape(url: str, max_age_hours: int = 24):
    """Get cached content or scrape fresh"""

    # Check cache
    if url in scraped_content_cache:
        cached_data, timestamp = scraped_content_cache[url]
        age = datetime.now() - timestamp

        if age.total_seconds() < max_age_hours * 3600:
            return cached_data

    # Scrape fresh content
    result = await firecrawl_service.scrape_url(url)

    # Cache result
    scraped_content_cache[url] = (result, datetime.now())

    return result
```

### 4. Error Handling

```python
async def robust_knowledge_retrieval(query: str):
    """Knowledge retrieval with fallbacks"""

    results = []

    # Try Qdrant first
    try:
        qdrant_results = qdrant_service.search(query, limit=5)
        results.extend(qdrant_results)
    except Exception as e:
        logging.error(f"Qdrant search failed: {e}")

    # Try Firecrawl if needed
    if len(results) < 3:
        try:
            urls = get_relevant_urls(query)
            scraped_data = await firecrawl_service.bulk_scrape_urls(urls[:3])
            results.extend(scraped_data)
        except Exception as e:
            logging.error(f"Firecrawl scraping failed: {e}")

    # Fallback to mock data if all else fails
    if not results:
        results = get_mock_knowledge_data(query)

    return results
```

### 5. Citation Best Practices

**Always cite external sources:**
```python
def generate_response_with_citations(query: str, knowledge: dict):
    """Generate response with proper citations"""

    # Build response using knowledge
    response = build_response(query, knowledge['context'])

    # Add citations
    if knowledge['citations']:
        response += "\n\n**Sources:**\n"
        for i, citation in enumerate(knowledge['citations'], 1):
            response += f"{i}. {format_citation_for_display(citation)}\n"

    # Add AI disclaimer if no external sources
    if not knowledge['citations']:
        response += "\n\n*Note: This response is AI-generated based on general knowledge.*"

    return response
```

### 6. Performance Monitoring

```python
import time

async def monitored_knowledge_retrieval(query: str):
    """Track knowledge retrieval performance"""

    start_time = time.time()
    metrics = {
        'qdrant_time': 0,
        'firecrawl_time': 0,
        'total_time': 0,
        'results_count': 0
    }

    # Qdrant search
    qdrant_start = time.time()
    qdrant_results = qdrant_service.search(query, limit=5)
    metrics['qdrant_time'] = time.time() - qdrant_start

    # Firecrawl scraping
    firecrawl_start = time.time()
    scraped_data = await firecrawl_service.bulk_scrape_urls(urls[:3])
    metrics['firecrawl_time'] = time.time() - firecrawl_start

    metrics['total_time'] = time.time() - start_time
    metrics['results_count'] = len(qdrant_results) + len(scraped_data)

    # Log metrics
    logging.info(f"Knowledge retrieval metrics: {metrics}")

    return {
        'results': qdrant_results + scraped_data,
        'metrics': metrics
    }
```

---

## Related Documentation

- [SERVICES.md](SERVICES.md) - Qdrant and Firecrawl service details
- [API.md](API.md) - Knowledge API endpoints
- [CONVERSATION_SYSTEM.md](CONVERSATION_SYSTEM.md) - Context integration
- [TESTING.md](TESTING.md) - Testing knowledge retrieval
