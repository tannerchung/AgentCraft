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

# Create router
router = APIRouter(tags=["knowledge"])

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
            "indexed_pages": 145,
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
            "indexed_pages": 238,
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
            "indexed_pages": 312,
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
        "indexed_pages": company_data.get("indexed_pages", 0),
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
            "indexed_pages": data["indexed_pages"],
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
        "indexed_pages": company_data.get("indexed_pages", 0)
    }

@router.post("/switch-company")
async def switch_company(request: CompanySwitchRequest):
    """Switch to a different company knowledge base"""
    if request.company not in knowledge_store["companies"]:
        # Create new company if it doesn't exist
        knowledge_store["companies"][request.company] = {
            "name": request.company.title(),
            "domain": f"{request.company}.com",
            "indexed_pages": 0,
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
    """Search the knowledge base for relevant information"""
    company = request.company or knowledge_store["current_company"]
    
    if company not in knowledge_store["companies"]:
        raise HTTPException(status_code=404, detail=f"Company {company} not found")
    
    company_data = knowledge_store["companies"][company]
    results = []
    
    # Simple keyword search simulation
    query_lower = request.query.lower()
    for entry in company_data.get("knowledge_entries", []):
        if query_lower in entry.get("title", "").lower() or \
           query_lower in entry.get("content", "").lower():
            results.append({
                "title": entry["title"],
                "content": entry["content"][:200] + "...",
                "url": entry["url"],
                "relevance": entry["relevance"]
            })
    
    # Add mock results if no real matches
    if not results and company_data.get("indexed_pages", 0) > 0:
        results = [
            {
                "title": f"{company.title()} - {request.query}",
                "content": f"Information about {request.query} from {company.title()} knowledge base...",
                "url": f"https://{company_data['domain']}/search?q={request.query}",
                "relevance": 0.75
            }
        ]
    
    return {
        "success": True,
        "query": request.query,
        "company": company,
        "results": results[:request.limit],
        "total_results": len(results)
    }

@router.get("/training-data/generate")
async def generate_training_data(count: int = Query(default=50, ge=1, le=200)):
    """Generate training data from the knowledge base"""
    current = knowledge_store["current_company"]
    company_data = knowledge_store["companies"].get(current, {})
    
    # Generate mock training data
    training_data = []
    topics = ["integration", "API", "webhooks", "authentication", "pricing", "features"]
    
    for i in range(min(count, 10)):  # Limit to 10 for demo
        topic = topics[i % len(topics)]
        training_data.append({
            "question": f"How does {current.title()} handle {topic}?",
            "answer": f"{current.title()} provides comprehensive {topic} capabilities...",
            "context": f"Based on documentation from {company_data.get('domain', 'website')}",
            "relevance": 0.8 + (i * 0.01)
        })
    
    return {
        "success": True,
        "company": current,
        "training_data": training_data,
        "count": len(training_data),
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

@router.post("/crawl/urls")
async def crawl_urls(request: CrawlUrlsRequest):
    """Crawl specified URLs to add to the knowledge base"""
    if request.company not in knowledge_store["companies"]:
        raise HTTPException(status_code=404, detail=f"Company {request.company} not found")
    
    company_data = knowledge_store["companies"][request.company]
    
    # Add URLs to company data (simulate crawling)
    new_urls = []
    for url in request.urls:
        if url not in company_data.get("urls", []):
            company_data["urls"].append(url)
            new_urls.append(url)
    
    # Update indexed pages count
    company_data["indexed_pages"] = company_data.get("indexed_pages", 0) + len(new_urls)
    company_data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    company_data["status"] = "indexing"
    
    # Simulate adding knowledge entries
    for url in new_urls:
        company_data["knowledge_entries"].append({
            "title": f"Content from {url}",
            "content": f"Crawled content from {url} at depth {request.depth}...",
            "url": url,
            "relevance": 0.85
        })
    
    # Set status back to ready after "indexing"
    company_data["status"] = "ready"
    
    return {
        "success": True,
        "message": f"Started crawling {len(request.urls)} URLs",
        "company": request.company,
        "urls_processed": new_urls,
        "total_indexed": company_data["indexed_pages"],
        "status": company_data["status"]
    }

@router.post("/knowledge-base/rebuild")
async def rebuild_knowledge_base(request: RebuildRequest):
    """Rebuild the knowledge base for a company"""
    if request.company not in knowledge_store["companies"]:
        raise HTTPException(status_code=404, detail=f"Company {request.company} not found")
    
    company_data = knowledge_store["companies"][request.company]
    
    # Simulate rebuild
    company_data["status"] = "rebuilding"
    company_data["last_updated"] = datetime.utcnow().isoformat() + "Z"
    
    if request.force:
        # Clear and rebuild from scratch
        company_data["knowledge_entries"] = []
        company_data["indexed_pages"] = len(company_data.get("urls", []))
        
        # Re-add entries
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
        "message": f"Knowledge base rebuilt for {request.company}",
        "company": request.company,
        "indexed_pages": company_data["indexed_pages"],
        "total_entries": len(company_data["knowledge_entries"]),
        "status": company_data["status"]
    }

# Health check endpoint
@router.get("/health")
async def knowledge_health():
    """Check health of knowledge base system"""
    return {
        "success": True,
        "status": "operational",
        "companies_loaded": len(knowledge_store["companies"]),
        "current_company": knowledge_store["current_company"]
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

@router.post("/services/test")
async def test_services():
    """Test connectivity to all external services"""
    qdrant_status = _check_qdrant_service()
    firecrawl_status = _check_firecrawl_service()
    
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
                "message": "Web scraping ready" if firecrawl_status else "Add FIRECRAWL_API_KEY to .env file"
            }
        },
        "overall_status": "fully_operational" if (qdrant_status and firecrawl_status) else "partial_functionality"
    }