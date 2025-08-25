
"""
Knowledge Base API endpoints for AgentCraft
Manages vector database, training data, and Firecrawl integration
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.services.qdrant_service import qdrant_service
    from src.services.firecrawl_service import firecrawl_service
    from src.services.training_data_service import training_data_service
    from src.services.target_company_service import target_company_service
except ImportError as e:
    logging.error(f"Failed to import services: {e}")
    qdrant_service = None
    firecrawl_service = None
    training_data_service = None
    target_company_service = None

router = APIRouter()
logger = logging.getLogger(__name__)

class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 5
    category_filter: Optional[str] = None
    company_context: Optional[str] = None

class CompanySwitchRequest(BaseModel):
    company_id: str

class CrawlRequest(BaseModel):
    urls: List[str]
    max_pages_per_url: int = 10

@router.get("/companies")
async def get_available_companies():
    """Get all available target companies"""
    try:
        if not target_company_service:
            raise HTTPException(status_code=503, detail="Target company service not available")
        
        companies = target_company_service.get_all_companies()
        return {
            "success": True,
            "companies": {
                company_id: {
                    "id": company.id,
                    "name": company.display_name,
                    "emoji": company.logo_emoji,
                    "color": company.primary_color,
                    "industry": company.industry,
                    "description": company.description
                }
                for company_id, company in companies.items()
            },
            "current_company": target_company_service.current_company
        }
    except Exception as e:
        logger.error(f"Error getting companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch-company")
async def switch_target_company(request: CompanySwitchRequest):
    """Switch to a different target company context"""
    try:
        if not target_company_service:
            raise HTTPException(status_code=503, detail="Target company service not available")
        
        success = target_company_service.set_current_company(request.company_id)
        if not success:
            raise HTTPException(status_code=400, detail=f"Invalid company ID: {request.company_id}")
        
        # Regenerate knowledge base for new company
        if qdrant_service:
            company_context = target_company_service.get_company_context()
            articles = qdrant_service.generate_mock_knowledge_base(company_context)
            qdrant_service.index_knowledge_base(articles)
        
        return {
            "success": True,
            "message": f"Switched to {request.company_id}",
            "current_company": target_company_service.get_current_company().display_name,
            "knowledge_base_updated": qdrant_service is not None
        }
    except Exception as e:
        logger.error(f"Error switching company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base/status")
async def get_knowledge_base_status():
    """Get current knowledge base status and metrics"""
    try:
        status = {
            "qdrant_available": qdrant_service is not None,
            "firecrawl_available": firecrawl_service is not None,
            "training_data_available": training_data_service is not None,
            "target_company_service_available": target_company_service is not None
        }
        
        if qdrant_service:
            status["qdrant_metrics"] = qdrant_service.get_metrics()
        
        if target_company_service:
            current_company = target_company_service.get_current_company()
            status["current_company"] = {
                "name": current_company.display_name,
                "industry": current_company.industry,
                "focus_areas": current_company.technical_focus_areas[:3]
            }
        
        return {
            "success": True,
            "status": status,
            "timestamp": "2024-01-27T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting knowledge base status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/search")
async def search_knowledge_base(request: KnowledgeSearchRequest):
    """Search the knowledge base using semantic similarity"""
    try:
        if not qdrant_service:
            raise HTTPException(status_code=503, detail="Qdrant service not available")
        
        # Add company context to search
        company_context = None
        if target_company_service and request.company_context:
            company_context = target_company_service.get_company_context(request.company_context)
        
        results = qdrant_service.search(
            query=request.query,
            limit=request.limit,
            category_filter=request.category_filter
        )
        
        return {
            "success": True,
            "results": results,
            "query": request.query,
            "company_context": company_context,
            "total_results": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge-base/rebuild")
async def rebuild_knowledge_base():
    """Rebuild the knowledge base with current company context"""
    try:
        if not qdrant_service:
            raise HTTPException(status_code=503, detail="Qdrant service not available")
        
        # Get current company context
        company_context = None
        if target_company_service:
            company_context = target_company_service.get_company_context()
        
        # Generate and index new knowledge base
        articles = qdrant_service.generate_mock_knowledge_base(company_context)
        success = qdrant_service.index_knowledge_base(articles)
        
        return {
            "success": success,
            "articles_indexed": len(articles),
            "company_context": company_context,
            "message": "Knowledge base rebuilt successfully"
        }
    except Exception as e:
        logger.error(f"Error rebuilding knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training-data/generate")
async def generate_training_data(count: int = 100):
    """Generate mock training tickets for current company"""
    try:
        if not training_data_service:
            raise HTTPException(status_code=503, detail="Training data service not available")
        
        # Get company context
        company_context = None
        if target_company_service:
            company_context = target_company_service.get_company_context()
        
        # Generate tickets
        tickets = training_data_service.generate_mock_tickets(count, company_context)
        insights = training_data_service.get_training_insights(tickets)
        
        return {
            "success": True,
            "tickets_generated": len(tickets),
            "insights": insights,
            "company_context": company_context,
            "sample_tickets": tickets[:3]  # Return first 3 as examples
        }
    except Exception as e:
        logger.error(f"Error generating training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl/urls")
async def crawl_urls(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Crawl URLs and add to knowledge base"""
    try:
        if not firecrawl_service:
            raise HTTPException(status_code=503, detail="Firecrawl service not available")
        
        # Start crawling in background
        background_tasks.add_task(
            perform_crawling_task,
            request.urls,
            request.max_pages_per_url
        )
        
        return {
            "success": True,
            "message": f"Started crawling {len(request.urls)} URLs",
            "urls": request.urls,
            "status": "crawling_started"
        }
    except Exception as e:
        logger.error(f"Error starting crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crawl/company-urls")
async def get_company_crawl_urls():
    """Get crawl URLs for current target company"""
    try:
        if not target_company_service:
            raise HTTPException(status_code=503, detail="Target company service not available")
        
        urls = target_company_service.get_crawl_urls()
        company = target_company_service.get_current_company()
        
        return {
            "success": True,
            "company": company.display_name,
            "urls": urls,
            "url_categories": {
                "documentation": company.documentation_urls,
                "community": company.community_urls,
                "marketing": company.marketing_urls,
                "blog": company.blog_urls,
                "learning": company.learning_urls
            }
        }
    except Exception as e:
        logger.error(f"Error getting company URLs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def perform_crawling_task(urls: List[str], max_pages_per_url: int):
    """Background task to perform crawling and update knowledge base"""
    try:
        logger.info(f"Starting crawl of {len(urls)} URLs")
        
        # Crawl URLs
        crawl_results = await firecrawl_service.bulk_scrape_urls(urls)
        
        # Convert crawl results to knowledge articles
        articles = []
        for result in crawl_results:
            if result.get('success'):
                # Convert to knowledge article format
                article_id = f"crawled_{hash(result['url'])}"
                articles.append({
                    "id": article_id,
                    "title": result.get('title', 'Crawled Content'),
                    "content": result.get('content', ''),
                    "category": "Crawled Documentation",
                    "tags": ["crawled", "documentation"],
                    "created_at": result.get('scraped_at'),
                    "updated_at": result.get('scraped_at'),
                    "source_url": result['url']
                })
        
        # Index in knowledge base
        if qdrant_service and articles:
            # Convert to KnowledgeArticle objects
            from src.services.qdrant_service import KnowledgeArticle
            knowledge_articles = [
                KnowledgeArticle(
                    id=article["id"],
                    title=article["title"],
                    content=article["content"],
                    category=article["category"],
                    tags=article["tags"],
                    created_at=article["created_at"],
                    updated_at=article["updated_at"]
                ) for article in articles
            ]
            
            qdrant_service.index_knowledge_base(knowledge_articles)
            logger.info(f"Indexed {len(knowledge_articles)} crawled articles")
        
    except Exception as e:
        logger.error(f"Error in crawling task: {e}")

@router.get("/demo/scenarios")
async def get_demo_scenarios():
    """Get pre-built demo scenarios for current company"""
    try:
        current_company = "zapier"  # Default
        if target_company_service:
            current_company = target_company_service.get_current_company().name
        
        scenarios = {
            "zapier": [
                {
                    "title": "Webhook Signature Verification Issue",
                    "query": "Our Zapier webhook integration stopped working after the API update. Getting 403 Forbidden errors on signature verification. This is blocking our automation workflows.",
                    "category": "technical",
                    "expected_agents": ["technical", "orchestrator"]
                },
                {
                    "title": "Zapier vs Power Automate Comparison",
                    "query": "We're evaluating Zapier versus Microsoft Power Automate for our enterprise automation needs. Can you provide a detailed comparison of features, pricing, and integration capabilities?",
                    "category": "competitive",
                    "expected_agents": ["competitive", "orchestrator"]
                },
                {
                    "title": "API Rate Limiting Problem",
                    "query": "Our Zapier integration is hitting rate limits when processing large batches of data. We need to optimize our API usage patterns and implement proper retry logic.",
                    "category": "technical",
                    "expected_agents": ["technical", "orchestrator"]
                }
            ],
            "hubspot": [
                {
                    "title": "CRM Data Sync Issues",
                    "query": "Our HubSpot integration is not syncing custom properties correctly. Standard fields work but custom fields are empty or contain wrong values.",
                    "category": "technical",
                    "expected_agents": ["technical", "orchestrator"]
                }
            ],
            "shopify": [
                {
                    "title": "Shopify App Development Issue",
                    "query": "Our Shopify app integration works in development but fails in production. The webhook payloads have different structures.",
                    "category": "technical",
                    "expected_agents": ["technical", "orchestrator"]
                }
            ]
        }
        
        return {
            "success": True,
            "company": current_company,
            "scenarios": scenarios.get(current_company, scenarios["zapier"])
        }
    except Exception as e:
        logger.error(f"Error getting demo scenarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))
