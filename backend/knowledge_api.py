"""
Knowledge Base API Endpoints
Handles company knowledge management, web crawling, and search functionality
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
import socket
import requests
import asyncio

# Import database managers
try:
    from database.models import knowledge_manager, db_manager
    DATABASE_INTEGRATION = True
except ImportError:
    DATABASE_INTEGRATION = False
    print("Warning: Database models not available")

# Import Qdrant service
try:
    from src.services.qdrant_service import qdrant_service
    QDRANT_INTEGRATION = True
except ImportError:
    QDRANT_INTEGRATION = False
    print("Warning: Qdrant service not available")

# Import Firecrawl
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_INTEGRATION = True
except ImportError:
    FIRECRAWL_INTEGRATION = False
    print("Warning: Firecrawl library not available")

# Create router
router = APIRouter(tags=["knowledge"])

# Database helper functions
async def ensure_db_initialized():
    """Ensure database connection is initialized"""
    if DATABASE_INTEGRATION and not db_manager.pool:
        await db_manager.initialize()

async def get_current_company() -> str:
    """Get current company from database"""
    if not DATABASE_INTEGRATION:
        return "zapier"
    await ensure_db_initialized()
    return await knowledge_manager.get_current_company()

async def get_company_urls(company_name: str) -> List[str]:
    """Get URLs for a company from database"""
    if not DATABASE_INTEGRATION:
        return []
    await ensure_db_initialized()
    return await knowledge_manager.get_company_crawl_urls(company_name)

async def add_company_url(company_name: str, url: str):
    """Add URL for a company to database"""
    if not DATABASE_INTEGRATION:
        return
    await ensure_db_initialized()
    await knowledge_manager.add_crawl_url(company_name, url)

async def get_all_companies() -> List[Dict]:
    """Get all companies from database"""
    if not DATABASE_INTEGRATION:
        return [{"name": "zapier", "domain": "zapier.com"}]
    await ensure_db_initialized()
    return await knowledge_manager.get_all_companies()

async def set_current_company(company_name: str):
    """Set current company in database"""
    if not DATABASE_INTEGRATION:
        return
    await ensure_db_initialized()
    await knowledge_manager.set_current_company(company_name)

def get_real_indexed_pages(company: str) -> int:
    """Get real number of indexed pages from Qdrant collection"""
    if not QDRANT_INTEGRATION or not qdrant_service.client:
        return 0
    
    try:
        base_collection = "agentcraft_knowledge"  # Always use the base name
        collection_name = f"{base_collection}_{company}"
        collection_info = qdrant_service.client.get_collection(collection_name)
        return collection_info.points_count or 0
    except Exception:
        return 0

def generate_common_child_urls(base_url: str, max_pages: int = 10) -> List[str]:
    """Generate common child URL patterns for testing when Firecrawl is unavailable"""
    # Common URL patterns based on base URL
    child_urls = []
    
    if '/blog' in base_url:
        # Common blog patterns
        patterns = [
            f"{base_url}/api-automation",
            f"{base_url}/workflow-automation", 
            f"{base_url}/integration-tips",
            f"{base_url}/productivity-tips",
            f"{base_url}/zapier-updates"
        ]
        child_urls.extend(patterns[:max_pages])
    elif '/docs' in base_url:
        # Common docs patterns
        patterns = [
            f"{base_url}/getting-started",
            f"{base_url}/api-reference", 
            f"{base_url}/tutorials",
            f"{base_url}/troubleshooting"
        ]
        child_urls.extend(patterns[:max_pages])
    elif '/features' in base_url:
        # Common feature patterns
        patterns = [
            f"{base_url}/integrations",
            f"{base_url}/automation",
            f"{base_url}/workflows"
        ]
        child_urls.extend(patterns[:max_pages])
    
    return child_urls

def discover_child_urls(base_url: str, max_pages: int = 10) -> List[str]:
    """Discover child URLs by crawling a base URL and extracting links"""
    if not FIRECRAWL_INTEGRATION:
        print(f"Firecrawl not available, using common patterns for: {base_url}")
        return generate_common_child_urls(base_url, max_pages)
    
    try:
        from firecrawl import FirecrawlApp
        firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        if not firecrawl_api_key:
            print(f"No Firecrawl API key, using common patterns for: {base_url}")
            return generate_common_child_urls(base_url, max_pages)
            
        app = FirecrawlApp(api_key=firecrawl_api_key)
        
        # Try using Firecrawl's crawl method for bulk crawling
        try:
            # Check if Firecrawl supports crawl method for discovering multiple pages
            if hasattr(app, 'crawl'):
                # Try different parameter formats for the crawl method
                try:
                    crawl_result = app.crawl(base_url, params={'limit': max_pages})
                except:
                    crawl_result = app.crawl(base_url)
                    
                if crawl_result and hasattr(crawl_result, 'data'):
                    urls = []
                    for page in crawl_result.data:
                        if hasattr(page, 'metadata') and hasattr(page.metadata, 'url'):
                            urls.append(page.metadata.url)
                    return urls
        except Exception as e:
            print(f"Firecrawl crawl method failed: {e}")
        
        # Fallback: scrape the base URL and extract links  
        try:
            result = app.scrape(base_url)
            print(f"Scrape result type: {type(result)}")
            if result:
                print(f"Scrape result attributes: {[attr for attr in dir(result) if not attr.startswith('_')][:10]}")
            else:
                print("Scrape returned None - likely rate limited")
                return generate_common_child_urls(base_url, max_pages)
        except Exception as scrape_err:
            print(f"Scrape failed: {scrape_err}")
            return generate_common_child_urls(base_url, max_pages)
        
        if result:
            # Check what's available in the result
            links_found = []
            
            # Try different ways to access links
            if hasattr(result, 'links') and result.links:
                print(f"Found {len(result.links)} links in result.links")
                for i, link in enumerate(result.links[:5]):  # Show first 5 for debugging
                    print(f"Link {i}: {link} (type: {type(link)})")
                    try:
                        link_url = str(link)
                        if link_url.startswith(base_url.rstrip('/')) and link_url != base_url:
                            links_found.append(link_url)
                    except Exception as e:
                        print(f"Error processing link {link}: {e}")
                        continue
            
            # Try extracting from HTML if available
            elif hasattr(result, 'html') and result.html:
                print("Trying to extract links from HTML content")
                import re
                html_content = result.html
                # Simple regex to find href links
                href_pattern = r'href=["\']([^"\']+)["\']'
                found_hrefs = re.findall(href_pattern, html_content)
                for href in found_hrefs[:20]:  # Limit to first 20
                    if href.startswith(base_url.rstrip('/')) and href != base_url:
                        links_found.append(href)
                print(f"Found {len(found_hrefs)} hrefs in HTML, {len(links_found)} matching base URL")
            
            # Try extracting from markdown content
            elif hasattr(result, 'markdown') and result.markdown:
                print("Trying to extract links from markdown content")
                import re
                markdown_content = result.markdown
                # Simple regex to find markdown links
                link_pattern = r'\[.*?\]\(([^)]+)\)'
                found_links = re.findall(link_pattern, markdown_content)
                for link in found_links[:20]:  # Limit to first 20
                    if link.startswith(base_url.rstrip('/')) and link != base_url:
                        links_found.append(link)
                print(f"Found {len(found_links)} markdown links, {len(links_found)} matching base URL")
            
            else:
                print(f"No extractable links found. Available attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            
            print(f"Total child URLs found: {len(links_found)}")
            return links_found[:max_pages]
        else:
            print("No result from scraping")
            return []
                    
    except Exception as e:
        print(f"URL discovery error for {base_url}: {e}")
        
    # Final fallback: use common patterns when Firecrawl discovery fails
    print(f"Firecrawl discovery failed, trying common URL patterns for: {base_url}")
    common_urls = generate_common_child_urls(base_url, max_pages)
    if common_urls:
        print(f"Generated {len(common_urls)} common child URLs: {common_urls}")
        return common_urls
    else:
        print(f"No common patterns available for: {base_url}")
        return []

def crawl_with_firecrawl(url: str) -> dict:
    """Crawl URL using real Firecrawl API"""
    if not FIRECRAWL_INTEGRATION:
        return None
    
    try:
        firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        if not firecrawl_api_key:
            return None
            
        app = FirecrawlApp(api_key=firecrawl_api_key)
        
        # Scrape the URL with Firecrawl (correct method name)
        scrape_result = app.scrape(url)
        
        if scrape_result:
            # Handle Firecrawl response format - it might be a Document object
            if hasattr(scrape_result, 'data'):
                content = scrape_result.data
            else:
                content = scrape_result
            
            # Extract title and content safely
            if hasattr(content, 'metadata') and content.metadata:
                if hasattr(content.metadata, 'get'):
                    title = content.metadata.get('title', f"Content from {url}")
                    metadata = dict(content.metadata) if content.metadata else {}
                else:
                    title = getattr(content.metadata, 'title', f"Content from {url}")
                    metadata = {}
            else:
                title = f"Content from {url}"
                metadata = {}
            
            # Extract content text
            if hasattr(content, 'markdown'):
                final_content = content.markdown
            elif hasattr(content, 'content'):
                final_content = content.content
            else:
                final_content = str(content)
            
            return {
                'title': title,
                'content': final_content,
                'url': url,
                'metadata': metadata,
                'source': 'firecrawl_live'
            }
    except Exception as e:
        print(f"Firecrawl error for {url}: {str(e)}")
    
    return None

def _check_qdrant_service() -> bool:
    """Check if Qdrant vector database service is running"""
    try:
        # Check for cloud Qdrant URL first
        qdrant_url = os.getenv('QDRANT_URL')
        qdrant_api_key = os.getenv('QDRANT_API_KEY')
        
        if qdrant_url and qdrant_api_key:
            # Test Qdrant cloud service
            headers = {'api-key': qdrant_api_key}
            response = requests.get(f"{qdrant_url}/", headers=headers, timeout=5)
            return response.status_code == 200
        
        # Fallback to local Qdrant check
        qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
        qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
        
        # Try to connect to local Qdrant API
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((qdrant_host, qdrant_port))
        sock.close()
        
        if result == 0:
            # Try to make an API call to verify it's actually Qdrant
            try:
                response = requests.get(f"http://{qdrant_host}:{qdrant_port}/", timeout=2)
                return response.status_code == 200
            except:
                return True  # Port is open, assume it's Qdrant
        return False
    except Exception as e:
        print(f"Qdrant check error: {e}")
        return False

def _check_firecrawl_service() -> bool:
    """Check if Firecrawl service is available"""
    try:
        firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        if not firecrawl_api_key:
            return False
        
        # Try to make a test API call to Firecrawl
        headers = {
            'Authorization': f'Bearer {firecrawl_api_key}',
            'Content-Type': 'application/json'
        }
        
        # Use a test endpoint or health check
        response = requests.get('https://api.firecrawl.dev/v0/crawl/status/test', 
                              headers=headers, timeout=5)
        
        # If we get any response (even 404), the service is available
        return response.status_code in [200, 404, 401, 403]
    except:
        return False

# Pydantic models
class CompanySwitchRequest(BaseModel):
    company: str = Field(..., min_length=1, max_length=100)

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    company: Optional[str] = Field(None, max_length=100)
    limit: int = Field(default=10, ge=1, le=100)

class CrawlUrlsRequest(BaseModel):
    urls: List[str] = Field(..., min_items=1, max_items=100)
    company: str = Field(..., min_length=1, max_length=100)
    depth: int = Field(default=1, ge=0, le=3)
    re_crawl: bool = Field(default=False)

class RebuildRequest(BaseModel):
    company: str = Field(..., min_length=1, max_length=100)
    force: bool = Field(default=False)

# In-memory storage for demo purposes
knowledge_store = {
    "current_company": "zapier",
    "companies": {
        "zapier": {
            "name": "Zapier",
            "domain": "zapier.com",
            "last_updated": "2024-12-20T10:30:00Z",
            "status": "ready",
            "urls": [
                "https://zapier.com",
                "https://zapier.com/apps",
                "https://zapier.com/pricing",
                "https://zapier.com/learn",
                "https://zapier.com/blog"
            ],
            "knowledge_entries": [
                {
                    "title": "Zapier Platform Overview",
                    "content": "Zapier is an automation platform that connects over 5,000 apps...",
                    "url": "https://zapier.com/platform",
                    "relevance": 0.95
                }
            ]
        },
        "hubspot": {
            "name": "HubSpot",
            "domain": "hubspot.com",
            "last_updated": "2024-12-19T15:45:00Z",
            "status": "ready",
            "urls": [
                "https://hubspot.com",
                "https://hubspot.com/products",
                "https://hubspot.com/pricing"
            ],
            "knowledge_entries": [
                {
                    "title": "HubSpot CRM Platform",
                    "content": "HubSpot offers a full platform of marketing, sales, customer service...",
                    "url": "https://hubspot.com/products/crm",
                    "relevance": 0.92
                }
            ]
        },
        "shopify": {
            "name": "Shopify",
            "domain": "shopify.com",
            "last_updated": "2024-12-18T09:15:00Z",
            "status": "ready",
            "urls": [
                "https://shopify.com",
                "https://shopify.com/online",
                "https://shopify.com/pricing"
            ],
            "knowledge_entries": [
                {
                    "title": "Shopify E-commerce Platform",
                    "content": "Shopify is a complete commerce platform that lets anyone start...",
                    "url": "https://shopify.com/online",
                    "relevance": 0.94
                }
            ]
        }
    }
}

@router.get("/knowledge-base/status")
async def get_knowledge_base_status():
    """Get the current status of the knowledge base"""
    current = knowledge_store["current_company"]
    company_data = knowledge_store["companies"].get(current, {})
    
    # Check for Qdrant service (mock check)
    qdrant_available = _check_qdrant_service()
    firecrawl_available = _check_firecrawl_service()
    
    return {
        "success": True,
        "current_company": current,
        "status": {
            "knowledge_base": company_data.get("status", "not_initialized"),
            "qdrant_available": qdrant_available,
            "firecrawl_available": firecrawl_available,
            "vector_database": "operational" if qdrant_available else "disabled",
            "web_crawler": "operational" if firecrawl_available else "mock_mode"
        },
        "indexed_pages": get_real_indexed_pages(current),
        "last_updated": company_data.get("last_updated"),
        "available_companies": list(knowledge_store["companies"].keys())
    }

@router.get("/companies")
async def get_companies():
    """Get list of available companies in the knowledge base"""
    companies = []
    for key, data in knowledge_store["companies"].items():
        companies.append({
            "id": key,
            "name": data["name"],
            "domain": data["domain"],
            "indexed_pages": get_real_indexed_pages(key),
            "status": data["status"],
            "last_updated": data["last_updated"]
        })
    
    return {
        "success": True,
        "companies": companies,
        "current": knowledge_store["current_company"]
    }

@router.get("/crawl/company-urls")
async def get_company_urls():
    """Get URLs that have been crawled for the current company"""
    current = knowledge_store["current_company"]
    company_data = knowledge_store["companies"].get(current, {})
    
    return {
        "success": True,
        "company": current,
        "urls": company_data.get("urls", []),
        "total_count": len(company_data.get("urls", [])),
        "indexed_pages": get_real_indexed_pages(current)
    }

@router.post("/switch-company")
async def switch_company(request: CompanySwitchRequest):
    """Switch to a different company knowledge base"""
    if request.company not in knowledge_store["companies"]:
        # Create new company if it doesn't exist
        knowledge_store["companies"][request.company] = {
            "name": request.company.title(),
            "domain": f"{request.company}.com",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "status": "initializing",
            "urls": [],
            "knowledge_entries": []
        }
    
    knowledge_store["current_company"] = request.company
    
    return {
        "success": True,
        "message": f"Switched to {request.company} knowledge base",
        "company": request.company,
        "status": knowledge_store["companies"][request.company]["status"]
    }

@router.post("/knowledge-base/search")
async def search_knowledge_base(request: SearchRequest):
    """Search the knowledge base using live Qdrant semantic search"""
    company = request.company or knowledge_store["current_company"]
    
    if company not in knowledge_store["companies"]:
        raise HTTPException(status_code=404, detail=f"Company {company} not found")
    
    if QDRANT_INTEGRATION and qdrant_service.client:
        try:
            # Use company-specific collection for semantic search  
            original_collection = "agentcraft_knowledge"  # Always use clean base name
            # Ensure we always use the base collection name to avoid duplicates
            base_collection = "agentcraft_knowledge"  # Always use the base name
            company_collection = f"{base_collection}_{company}"
            qdrant_service.collection_name = company_collection
            
            # Perform semantic search
            search_results = qdrant_service.search(request.query, limit=request.limit)
            
            # Restore original collection name
            qdrant_service.collection_name = original_collection
            
            # Format results for frontend compatibility
            results = []
            for result in search_results:
                # Extract source URL from metadata if available, otherwise use ID
                source_url = result.get("id", "")  # Default to ID
                metadata = result.get("metadata", {})
                if isinstance(metadata, dict) and metadata.get("source_url"):
                    source_url = metadata["source_url"]
                
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", "")[:200] + "..." if len(result.get("content", "")) > 200 else result.get("content", ""),
                    "url": source_url,
                    "relevance": result.get("similarity_score", 0.0),
                    "similarity_score": result.get("similarity_score", 0.0),
                    "category": result.get("category", ""),
                    "updated_at": result.get("updated_at", "")
                })
            
            return {
                "success": True,
                "query": request.query,
                "company": company,
                "results": results,
                "total_results": len(results),
                "search_type": "semantic_vector",
                "collection": company_collection
            }
            
        except Exception as e:
            # Fallback to mock if Qdrant search fails
            company_data = knowledge_store["companies"][company]
            results = [{
                "title": f"Search Error - {company.title()}",
                "content": f"Qdrant search failed: {str(e)}. Using fallback for '{request.query}'...",
                "url": f"error://{company}",
                "relevance": 0.0,
                "similarity_score": 0.0,
                "error": str(e)
            }]
            
            return {
                "success": False,
                "query": request.query,
                "company": company,
                "results": results,
                "total_results": len(results),
                "search_type": "error_fallback",
                "error": str(e)
            }
    else:
        # Fallback when Qdrant not available
        company_data = knowledge_store["companies"][company]
        results = [{
            "title": f"Qdrant Unavailable - {company.title()}",
            "content": f"Vector search not available. Query: '{request.query}'. Please ensure Qdrant service is running.",
            "url": f"mock://{company}",
            "relevance": 0.0,
            "similarity_score": 0.0
        }]
        
        return {
            "success": True,
            "query": request.query,
            "company": company,
            "results": results,
            "total_results": len(results),
            "search_type": "mock_fallback",
            "message": "Qdrant integration not available"
        }

@router.get("/training-data/generate")
async def generate_training_data(count: int = Query(default=50, ge=1, le=200)):
    """Generate training data from crawled URLs and knowledge base content"""
    current = knowledge_store["current_company"]
    company_data = knowledge_store["companies"].get(current, {})
    
    if not company_data:
        raise HTTPException(status_code=404, detail=f"Company {current} not found")
    
    training_data = []
    crawled_urls = company_data.get("urls", [])
    knowledge_entries = company_data.get("knowledge_entries", [])
    
    # Generate training data from actual crawled content
    if knowledge_entries:
        # Use actual knowledge entries from crawled URLs
        for i, entry in enumerate(knowledge_entries):
            if len(training_data) >= count:
                break
                
            # Extract meaningful questions from crawled content
            url = entry.get("url", "")
            title = entry.get("title", "")
            content = entry.get("content", "")
            
            # Determine the type of content based on URL patterns
            content_type = "documentation"
            if "community" in url.lower() or "forum" in url.lower():
                content_type = "community"
            elif "help" in url.lower() or "support" in url.lower():
                content_type = "support"
            elif "api" in url.lower():
                content_type = "api"
            elif "blog" in url.lower():
                content_type = "blog"
            
            # Generate contextual questions based on content type and title
            if content_type == "community":
                questions = [
                    f"How can I {title.lower().replace(current.title(), '').strip()}?",
                    f"What's the best way to implement {title.split()[-1] if title else 'this feature'}?",
                    f"I'm having trouble with {title.split()[0] if title else 'integration'} - any solutions?",
                    f"Has anyone successfully {title.lower().replace('how to', '').strip()}?",
                ]
            elif content_type == "support":
                questions = [
                    f"How do I troubleshoot {title.lower().replace(current.title(), '').strip()}?",
                    f"What should I do if {title.lower().replace('troubleshooting', '').strip()}?",
                    f"Why is {title.split()[-1] if title else 'my integration'} not working?",
                ]
            elif content_type == "api":
                questions = [
                    f"How do I use the {title.replace('API', '').strip()} API?",
                    f"What are the parameters for {title.lower()}?",
                    f"How do I authenticate with {current.title()} API?",
                ]
            else:
                questions = [
                    f"How does {current.title()} handle {title.lower()}?",
                    f"What are the best practices for {title.lower()}?",
                    f"Can you explain {title.lower()}?",
                ]
            
            # Create training entries
            for question in questions[:2]:  # Max 2 questions per entry
                if len(training_data) >= count:
                    break
                    
                training_data.append({
                    "question": question,
                    "answer": content[:500] + "..." if len(content) > 500 else content,
                    "context": f"Source: {url}",
                    "content_type": content_type,
                    "source_url": url,
                    "relevance": entry.get("relevance", 0.8),
                    "crawl_source": True
                })
    
    # If we don't have enough from crawled content, supplement with generated content
    while len(training_data) < min(count, 20):  # Cap at 20 total
        topics = ["integration", "API", "webhooks", "authentication", "pricing", "features", 
                 "troubleshooting", "setup", "configuration", "automation", "workflows", "connectors"]
        
        topic = topics[len(training_data) % len(topics)]
        training_data.append({
            "question": f"How does {current.title()} handle {topic}?",
            "answer": f"{current.title()} provides {topic} capabilities through its platform. This includes comprehensive tools and documentation to help users implement {topic} effectively.",
            "context": f"Generated from {current.title()} knowledge base",
            "content_type": "generated",
            "source_url": f"https://{company_data.get('domain', current + '.com')}",
            "relevance": 0.7,
            "crawl_source": False
        })
    
    # Analyze the training data for insights
    community_count = len([t for t in training_data if t.get("content_type") == "community"])
    crawled_count = len([t for t in training_data if t.get("crawl_source", False)])
    
    return {
        "success": True,
        "company": current,
        "training_data": training_data,
        "count": len(training_data),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "sources": {
            "crawled_urls": len(crawled_urls),
            "knowledge_entries": len(knowledge_entries),
            "community_content": community_count,
            "from_crawled_data": crawled_count,
            "generated_content": len(training_data) - crawled_count
        },
        "url_breakdown": {
            url_type: len([t for t in training_data if t.get("content_type") == url_type])
            for url_type in ["community", "support", "api", "documentation", "blog", "generated"]
        }
    }

@router.post("/crawl/urls")
async def crawl_urls(request: CrawlUrlsRequest):
    """Crawl specified URLs using Firecrawl and add to knowledge base"""
    if request.company not in knowledge_store["companies"]:
        raise HTTPException(status_code=404, detail=f"Company {request.company} not found")
    
    company_data = knowledge_store["companies"][request.company]
    is_re_crawl = getattr(request, 're_crawl', False)
    
    # Expand wildcard URLs (e.g., https://example.com/docs/* -> multiple child URLs)
    expanded_urls = []
    wildcard_discovered = 0
    
    print(f"Processing URLs: {request.urls}")
    
    for url in request.urls:
        print(f"Processing URL: {url}, ends with /*: {url.endswith('/*')}")
        if url.endswith('/*'):
            # Handle wildcard URL - discover child pages
            base_url = url[:-2]  # Remove /*
            print(f"Discovering child URLs for: {base_url}")
            child_urls = discover_child_urls(base_url, max_pages=20)
            print(f"Child URLs discovered: {child_urls}")
            expanded_urls.extend(child_urls)
            expanded_urls.append(base_url)  # Also include the base URL
            wildcard_discovered += len(child_urls)
            print(f"Discovered {len(child_urls)} child URLs for {base_url}")
        else:
            expanded_urls.append(url)
    
    # Remove duplicates while preserving order
    urls_to_process = list(dict.fromkeys(expanded_urls))
    operation_type = "re-crawling" if is_re_crawl else "crawling"
    
    # Log wildcard expansion results
    if wildcard_discovered > 0:
        print(f"Wildcard expansion: {len(request.urls)} patterns -> {len(urls_to_process)} total URLs ({wildcard_discovered} discovered)")
    
    # Add new URLs to company data if not re-crawling
    new_urls = []
    if not is_re_crawl:
        for url in request.urls:
            if url not in company_data.get("urls", []):
                company_data["urls"].append(url)
                new_urls.append(url)
    else:
        # For re-crawling, process all existing URLs
        new_urls = urls_to_process
    
    company_data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    company_data["status"] = "crawling"
    
    # Check if Firecrawl is available
    firecrawl_available = _check_firecrawl_service()
    crawled_content = []
    
    try:
        if firecrawl_available and FIRECRAWL_INTEGRATION:
            # Real Firecrawl integration
            for url in urls_to_process:
                try:
                    firecrawl_result = crawl_with_firecrawl(url)
                    if firecrawl_result:
                        crawled_content.append({
                            "title": firecrawl_result["title"],
                            "content": firecrawl_result["content"],
                            "url": url,
                            "relevance": 0.95,  # High relevance for real content
                            "source": "firecrawl_live",
                            "crawl_timestamp": datetime.utcnow().isoformat(),
                            "metadata": firecrawl_result.get("metadata", {})
                        })
                    else:
                        # Fallback to mock if Firecrawl fails for this URL
                        crawled_content.append({
                            "title": f"Content from {url} (Firecrawl failed)",
                            "content": f"Mock content for {url} - Firecrawl extraction failed",
                            "url": url,
                            "relevance": 0.70,
                            "source": "mock_fallback"
                        })
                except Exception as e:
                    print(f"Error crawling {url}: {str(e)}")
        else:
            # Mock mode fallback
            for url in urls_to_process:
                mock_content = {
                    "title": f"Mock Content from {url}",
                    "content": f"Simulated crawled content from {url} (Firecrawl not available)",
                    "url": url,
                    "relevance": 0.75,
                    "source": "mock_crawl"
                }
                crawled_content.append(mock_content)
        
        # Update knowledge entries
        if is_re_crawl:
            # Clear existing entries for re-crawled URLs
            company_data["knowledge_entries"] = [
                entry for entry in company_data.get("knowledge_entries", [])
                if entry.get("url") not in urls_to_process
            ]
        
        # Add new crawled content
        company_data["knowledge_entries"].extend(crawled_content)
        
        # Automatically index crawled content into Qdrant for search
        indexed_count = 0
        if QDRANT_INTEGRATION and qdrant_service.client and crawled_content:
            try:
                from src.services.qdrant_service import KnowledgeArticle
                articles = []
                
                for i, content in enumerate(crawled_content):
                    article = KnowledgeArticle(
                        id=f"{request.company}_crawl_{i}_{int(datetime.utcnow().timestamp())}",
                        title=content.get("title", f"Crawled content {i+1}"),
                        content=content.get("content", ""),
                        category="Crawled Content",
                        tags=[request.company, "crawled", content.get("source", "web")],
                        created_at=datetime.utcnow().isoformat() + "Z",
                        updated_at=datetime.utcnow().isoformat() + "Z",
                        metadata={
                            "source_url": content.get("url", ""),
                            "crawl_timestamp": content.get("crawl_timestamp", ""),
                            "firecrawl_used": content.get("source") == "firecrawl_live"
                        }
                    )
                    articles.append(article)
                
                if articles:
                    # Index into company-specific collection
                    original_collection = "agentcraft_knowledge"  # Always use clean base name
                    base_collection = "agentcraft_knowledge"  # Always use the base name
                    company_collection = f"{base_collection}_{request.company}"
                    
                    # Ensure collection exists
                    try:
                        qdrant_service.client.get_collection(company_collection)
                    except:
                        from qdrant_client.models import VectorParams, Distance
                        qdrant_service.client.create_collection(
                            collection_name=company_collection,
                            vectors_config=VectorParams(
                                size=qdrant_service.embedding_dim,
                                distance=Distance.COSINE
                            )
                        )
                    
                    qdrant_service.collection_name = company_collection
                    success = qdrant_service.index_knowledge_base(articles)
                    qdrant_service.collection_name = original_collection
                    
                    if success:
                        indexed_count = len(articles)
            except Exception as e:
                print(f"Error indexing crawled content: {str(e)}")
        
        company_data["status"] = "ready"
        crawl_method = "Live Firecrawl API" if firecrawl_available else "Mock crawl (Firecrawl unavailable)"
        
        # Build response message with wildcard info
        base_message = f"Successfully {operation_type} {len(urls_to_process)} URLs using {crawl_method}"
        if wildcard_discovered > 0:
            base_message += f" ({wildcard_discovered} URLs discovered from wildcard patterns)"
        
        return {
            "success": True,
            "message": base_message,
            "company": request.company,
            "operation": operation_type,
            "crawl_method": crawl_method,
            "urls_processed": urls_to_process,
            "original_patterns": request.urls,
            "wildcard_discovered": wildcard_discovered,
            "content_extracted": len(crawled_content),
            "content_indexed": indexed_count,
            "total_indexed": get_real_indexed_pages(request.company),
            "firecrawl_used": firecrawl_available,
            "auto_indexed": indexed_count > 0,
            "status": company_data["status"]
        }
        
    except Exception as e:
        company_data["status"] = "error"
        return {
            "success": False,
            "message": f"Failed to crawl URLs: {str(e)}",
            "company": request.company,
            "error": str(e),
            "firecrawl_used": firecrawl_available
        }

@router.post("/knowledge-base/rebuild")
async def rebuild_knowledge_base(request: RebuildRequest):
    """Rebuild the knowledge base for a company with live Qdrant integration"""
    if request.company not in knowledge_store["companies"]:
        raise HTTPException(status_code=404, detail=f"Company {request.company} not found")
    
    company_data = knowledge_store["companies"][request.company]
    company_data["status"] = "rebuilding"
    company_data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    
    try:
        if QDRANT_INTEGRATION and qdrant_service.client:
            # Live Qdrant rebuild
            if request.force:
                # Clear existing collection and recreate
                try:
                    base_collection = "agentcraft_knowledge"  # Always use the base name
                    qdrant_service.client.delete_collection(
                        collection_name=f"{base_collection}_{request.company}"
                    )
                except:
                    pass  # Collection may not exist
                
                # Recreate collection for this company
                from qdrant_client.models import VectorParams, Distance
                base_collection = "agentcraft_knowledge"  # Always use the base name
                qdrant_service.client.create_collection(
                    collection_name=f"{base_collection}_{request.company}",
                    vectors_config=VectorParams(
                        size=qdrant_service.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
            
            # Convert knowledge entries to KnowledgeArticle objects
            if company_data.get("knowledge_entries"):
                from src.services.qdrant_service import KnowledgeArticle
                articles = []
                
                for i, entry in enumerate(company_data["knowledge_entries"]):
                    article = KnowledgeArticle(
                        id=f"{request.company}_{i}",
                        title=entry.get("title", f"Article {i+1}"),
                        content=entry.get("content", ""),
                        category="Crawled Content",
                        tags=[request.company, "crawled", "live"],
                        created_at=datetime.utcnow().isoformat() + "Z",
                        updated_at=datetime.utcnow().isoformat() + "Z"
                    )
                    articles.append(article)
                
                # Index articles into company-specific collection
                original_collection = "agentcraft_knowledge"  # Always use clean base name
                base_collection = "agentcraft_knowledge"  # Always use the base name
                qdrant_service.collection_name = f"{base_collection}_{request.company}"
                
                success = qdrant_service.index_knowledge_base(articles)
                
                # Restore original collection name
                qdrant_service.collection_name = original_collection
                
                if success:
                    company_data["qdrant_indexed"] = len(articles)
                    base_collection = "agentcraft_knowledge"  # Always use the base name
                    company_data["qdrant_collection"] = f"{base_collection}_{request.company}"
                else:
                    raise Exception("Failed to index articles in Qdrant")
            else:
                # No knowledge entries to index
                company_data["qdrant_indexed"] = 0
        
        else:
            # Fallback to mock rebuild if Qdrant not available
            if request.force:
                company_data["knowledge_entries"] = []
                # URLs will be indexed into Qdrant, not stored as indexed_pages count
                
                for url in company_data.get("urls", []):
                    company_data["knowledge_entries"].append({
                        "title": f"Rebuilt content from {url}",
                        "content": f"Fresh content from {url}...",
                        "url": url,
                        "relevance": 0.90
                    })
        
        company_data["status"] = "ready"
        
        return {
            "success": True,
            "message": f"Knowledge base rebuilt for {request.company}" + 
                      (" with Qdrant integration" if QDRANT_INTEGRATION else " (mock mode)"),
            "company": request.company,
            "indexed_pages": get_real_indexed_pages(request.company),
            "total_entries": len(company_data.get("knowledge_entries", [])),
            "qdrant_indexed": company_data.get("qdrant_indexed", 0),
            "qdrant_collection": company_data.get("qdrant_collection"),
            "integration": "live" if QDRANT_INTEGRATION else "mock",
            "status": company_data["status"]
        }
        
    except Exception as e:
        company_data["status"] = "error"
        company_data["error"] = str(e)
        
        return {
            "success": False,
            "message": f"Failed to rebuild knowledge base: {str(e)}",
            "company": request.company,
            "status": "error",
            "error": str(e)
        }


@router.post("/training-data/integrate")
async def integrate_training_data(request: dict):
    """Integrate generated training data into knowledge base for agent use"""
    company = request.get("company", knowledge_store["current_company"])
    training_data = request.get("training_data", [])
    
    if not training_data:
        return {"success": False, "message": "No training data provided"}
    
    if company not in knowledge_store["companies"]:
        return {"success": False, "message": f"Company {company} not found"}
    
    company_data = knowledge_store["companies"][company]
    integrated_count = 0
    
    try:
        if QDRANT_INTEGRATION and qdrant_service.client:
            # Convert training data to knowledge articles for Qdrant indexing
            from src.services.qdrant_service import KnowledgeArticle
            articles = []
            
            for i, item in enumerate(training_data):
                question = item.get("question", "")
                answer = item.get("answer", "")
                
                if question and answer:
                    article = KnowledgeArticle(
                        id=f"{company}_training_{i}",
                        title=f"Training Q&A: {question[:50]}...",
                        content=f"Q: {question}\n\nA: {answer}",
                        category="Training Data",
                        tags=[company, "training", "qa", "community"],
                        created_at=datetime.utcnow().isoformat() + "Z",
                        updated_at=datetime.utcnow().isoformat() + "Z"
                    )
                    articles.append(article)
            
            if articles:
                # Index training articles into company-specific collection
                original_collection = "agentcraft_knowledge"  # Always use clean base name
                base_collection = "agentcraft_knowledge"  # Always use the base name
                company_collection = f"{base_collection}_{company}"
                
                # Ensure collection exists
                try:
                    qdrant_service.client.get_collection(company_collection)
                except:
                    # Create collection if it doesn't exist
                    from qdrant_client.models import VectorParams, Distance
                    qdrant_service.client.create_collection(
                        collection_name=company_collection,
                        vectors_config=VectorParams(
                            size=qdrant_service.embedding_dim,
                            distance=Distance.COSINE
                        )
                    )
                
                qdrant_service.collection_name = company_collection
                success = qdrant_service.index_knowledge_base(articles)
                qdrant_service.collection_name = original_collection
                
                if success:
                    integrated_count = len(articles)
                    
                    # Update company knowledge entries for tracking
                    for article in articles:
                        company_data["knowledge_entries"].append({
                            "title": article.title,
                            "content": article.content[:200],
                            "url": f"training://qa_{article.id}",
                            "relevance": 0.90,
                            "source": "training_data"
                        })
        
        return {
            "success": True,
            "message": f"Integrated {integrated_count} training items into {company} knowledge base",
            "company": company,
            "integrated_count": integrated_count,
            "total_kb_entries": len(company_data.get("knowledge_entries", [])),
            "integration_type": "live" if QDRANT_INTEGRATION else "mock"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to integrate training data: {str(e)}",
            "error": str(e)
        }

# Health check endpoint
@router.get("/health")
async def knowledge_health():
    """Check health of knowledge base system"""
    return {
        "success": True,
        "status": "operational",
        "companies_loaded": len(knowledge_store["companies"]),
        "current_company": knowledge_store["current_company"],
        "qdrant_integration": QDRANT_INTEGRATION,
        "qdrant_available": QDRANT_INTEGRATION and qdrant_service.client is not None
    }

@router.get("/services/setup-guide")
async def get_services_setup_guide():
    """Get setup instructions for Qdrant and Firecrawl services"""
    return {
        "success": True,
        "services": {
            "qdrant": {
                "name": "Qdrant Vector Database",
                "current_status": "inactive" if not _check_qdrant_service() else "active",
                "setup_instructions": [
                    "Install Qdrant using Docker:",
                    "docker run -p 6333:6333 qdrant/qdrant",
                    "",
                    "Or install locally:",
                    "1. Download from https://github.com/qdrant/qdrant/releases",
                    "2. Run: ./qdrant",
                    "3. Service will be available at http://localhost:6333",
                    "",
                    "Environment variables (optional):",
                    "QDRANT_HOST=localhost",
                    "QDRANT_PORT=6333"
                ],
                "test_command": "curl http://localhost:6333/",
                "required_for": ["Vector search", "Semantic similarity", "Content recommendations"]
            },
            "firecrawl": {
                "name": "Firecrawl Web Scraping Service", 
                "current_status": "mock_mode" if not _check_firecrawl_service() else "active",
                "setup_instructions": [
                    "Get API key from Firecrawl:",
                    "1. Sign up at https://firecrawl.dev",
                    "2. Get your API key from the dashboard", 
                    "3. Add to your .env file:",
                    "   FIRECRAWL_API_KEY=your_api_key_here",
                    "",
                    "Firecrawl provides:",
                    "- Web scraping without getting blocked",
                    "- Clean markdown extraction",
                    "- Automated crawling with rate limiting"
                ],
                "test_command": "curl -H 'Authorization: Bearer YOUR_API_KEY' https://api.firecrawl.dev/v0/crawl/status/test",
                "required_for": ["Web crawling", "Content extraction", "Real-time data updates"]
            }
        },
        "quick_start": {
            "qdrant": "docker run -p 6333:6333 qdrant/qdrant",
            "firecrawl": "Add FIRECRAWL_API_KEY to .env file"
        }
    }

@router.get("/services/test")
async def test_services():
    """Test connectivity to all external services with detailed debugging"""
    qdrant_status = _check_qdrant_service()
    
    # Enhanced Firecrawl testing
    firecrawl_debug = {
        "basic_check": _check_firecrawl_service(),
        "api_key_present": bool(os.getenv('FIRECRAWL_API_KEY')),
        "integration_enabled": FIRECRAWL_INTEGRATION,
        "test_scrape": None
    }
    
    # Test actual scraping
    if FIRECRAWL_INTEGRATION:
        try:
            from firecrawl import FirecrawlApp
            firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
            if firecrawl_api_key:
                app = FirecrawlApp(api_key=firecrawl_api_key)
                test_result = app.scrape("https://example.com")
                
                if test_result:
                    # Detailed analysis of the response
                    analysis = {
                        "success": True,
                        "type": str(type(test_result)),
                        "attributes": [attr for attr in dir(test_result) if not attr.startswith('_')][:10],
                        "has_data": hasattr(test_result, 'data'),
                        "has_metadata": hasattr(test_result, 'metadata'),
                        "has_content": hasattr(test_result, 'content'),
                        "has_markdown": hasattr(test_result, 'markdown'),
                    }
                    
                    # Test our parsing logic
                    try:
                        parsed = crawl_with_firecrawl("https://example.com")
                        analysis["parsing_result"] = {
                            "success": parsed is not None,
                            "title": parsed.get("title") if parsed else None,
                            "content_length": len(parsed.get("content", "")) if parsed else 0
                        }
                    except Exception as parse_err:
                        analysis["parsing_result"] = {
                            "success": False,
                            "error": str(parse_err)
                        }
                    
                    firecrawl_debug["test_scrape"] = analysis
                else:
                    firecrawl_debug["test_scrape"] = {"success": False, "reason": "No result returned"}
        except Exception as e:
            firecrawl_debug["test_scrape"] = {"success": False, "error": str(e)}
    
    firecrawl_status = firecrawl_debug["basic_check"]
    
    return {
        "success": True,
        "services": {
            "qdrant": {
                "available": qdrant_status,
                "status": "✅ Connected" if qdrant_status else "❌ Not available",
                "message": "Vector database ready" if qdrant_status else "Run: docker run -p 6333:6333 qdrant/qdrant"
            },
            "firecrawl": {
                "available": firecrawl_status, 
                "status": "✅ Connected" if firecrawl_status else "⚠️ Mock mode",
                "message": "Web scraping ready" if firecrawl_status else "Add FIRECRAWL_API_KEY to .env file",
                "debug_info": firecrawl_debug
            }
        },
        "overall_status": "fully_operational" if (qdrant_status and firecrawl_status) else "partial_functionality"
    }