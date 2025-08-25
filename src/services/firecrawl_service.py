
"""
Firecrawl Integration Service for AgentCraft
Real-time web scraping for knowledge base updates
"""

import asyncio
import aiohttp
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse

# Try to import firecrawl-py (install with: pip install firecrawl-py)
try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    logging.warning("Firecrawl not installed. Run: pip install firecrawl-py")

logger = logging.getLogger(__name__)

class FirecrawlService:
    """Service for web scraping using Firecrawl"""
    
    def __init__(self):
        self.api_key = os.getenv('FIRECRAWL_API_KEY')
        self.app = None
        
        if FIRECRAWL_AVAILABLE and self.api_key:
            self.app = FirecrawlApp(api_key=self.api_key)
            logger.info("Firecrawl service initialized successfully")
        else:
            logger.warning("Firecrawl service not available - missing API key or library")
    
    async def scrape_url(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Scrape a single URL and extract structured content"""
        if not self.app:
            return await self._mock_scrape_url(url)
        
        try:
            # Default scraping options
            scrape_options = {
                'formats': ['markdown', 'html'],
                'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'article', 'main'],
                'excludeTags': ['nav', 'footer', 'aside', 'script', 'style'],
                'onlyMainContent': True,
                'removeBase64Images': True
            }
            
            if options:
                scrape_options.update(options)
            
            # Scrape the URL
            result = self.app.scrape_url(url, params=scrape_options)
            
            if result.get('success'):
                return {
                    'success': True,
                    'url': url,
                    'title': result.get('data', {}).get('metadata', {}).get('title', ''),
                    'content': result.get('data', {}).get('markdown', ''),
                    'html': result.get('data', {}).get('html', ''),
                    'metadata': result.get('data', {}).get('metadata', {}),
                    'scraped_at': datetime.now().isoformat()
                }
            else:
                logger.error(f"Firecrawl scraping failed for {url}: {result}")
                return {'success': False, 'url': url, 'error': str(result)}
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {'success': False, 'url': url, 'error': str(e)}
    
    async def crawl_site(self, base_url: str, max_pages: int = 50, 
                        options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Crawl an entire site and extract content"""
        if not self.app:
            return await self._mock_crawl_site(base_url, max_pages)
        
        try:
            crawl_options = {
                'limit': max_pages,
                'scrapeOptions': {
                    'formats': ['markdown'],
                    'onlyMainContent': True,
                    'removeBase64Images': True,
                    'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'article', 'main'],
                    'excludeTags': ['nav', 'footer', 'aside', 'script', 'style']
                }
            }
            
            if options:
                crawl_options.update(options)
            
            # Start crawling
            crawl_result = self.app.crawl_url(base_url, params=crawl_options)
            
            if crawl_result.get('success'):
                return {
                    'success': True,
                    'base_url': base_url,
                    'pages_crawled': len(crawl_result.get('data', [])),
                    'data': crawl_result.get('data', []),
                    'crawled_at': datetime.now().isoformat()
                }
            else:
                logger.error(f"Firecrawl crawling failed for {base_url}: {crawl_result}")
                return {'success': False, 'base_url': base_url, 'error': str(crawl_result)}
                
        except Exception as e:
            logger.error(f"Error crawling {base_url}: {e}")
            return {'success': False, 'base_url': base_url, 'error': str(e)}
    
    async def bulk_scrape_urls(self, urls: List[str], 
                              options: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently"""
        if not urls:
            return []
        
        # Limit concurrent requests to avoid overwhelming the service
        semaphore = asyncio.Semaphore(5)
        
        async def scrape_with_limit(url):
            async with semaphore:
                return await self.scrape_url(url, options)
        
        tasks = [scrape_with_limit(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping {urls[i]}: {result}")
                successful_results.append({
                    'success': False, 
                    'url': urls[i], 
                    'error': str(result)
                })
            else:
                successful_results.append(result)
        
        return successful_results
    
    async def _mock_scrape_url(self, url: str) -> Dict[str, Any]:
        """Mock scraping for demo purposes when Firecrawl is not available"""
        domain = urlparse(url).netloc
        
        mock_content = {
            'zapier.com': self._generate_zapier_mock_content(url),
            'docs.zapier.com': self._generate_zapier_docs_content(url),
            'community.zapier.com': self._generate_zapier_community_content(url),
            'learn.zapier.com': self._generate_zapier_learning_content(url)
        }
        
        # Get mock content based on domain
        content_generator = mock_content.get(domain, self._generate_generic_mock_content)
        mock_data = content_generator(url)
        
        return {
            'success': True,
            'url': url,
            'title': mock_data['title'],
            'content': mock_data['content'],
            'metadata': {
                'description': mock_data.get('description', ''),
                'keywords': mock_data.get('keywords', [])
            },
            'scraped_at': datetime.now().isoformat(),
            'mock': True
        }
    
    async def _mock_crawl_site(self, base_url: str, max_pages: int) -> Dict[str, Any]:
        """Mock site crawling for demo purposes"""
        urls = [
            f"{base_url}/webhooks",
            f"{base_url}/api-docs",
            f"{base_url}/integrations",
            f"{base_url}/troubleshooting",
            f"{base_url}/best-practices"
        ][:max_pages]
        
        scraped_data = await self.bulk_scrape_urls(urls)
        
        return {
            'success': True,
            'base_url': base_url,
            'pages_crawled': len(scraped_data),
            'data': scraped_data,
            'crawled_at': datetime.now().isoformat(),
            'mock': True
        }
    
    def _generate_zapier_mock_content(self, url: str) -> Dict[str, Any]:
        """Generate realistic Zapier mock content"""
        return {
            'title': 'Zapier - Automate Your Work',
            'description': 'Connect your apps and automate workflows',
            'keywords': ['automation', 'integration', 'workflow', 'zapier'],
            'content': '''# Zapier - Connect Your Apps

Zapier is the easiest way to automate your work. Connect 7,000+ apps to create automated workflows that get your work done.

## Popular Integrations
- Gmail + Slack
- Google Sheets + Salesforce  
- Shopify + QuickBooks
- Webhook + Database

## Key Features
- No-code automation
- 7,000+ app integrations
- Enterprise security
- Advanced workflow logic

## Getting Started
1. Choose your trigger app
2. Select your action app
3. Connect your accounts
4. Test your automation
5. Turn on your Zap
'''
        }
    
    def _generate_zapier_docs_content(self, url: str) -> Dict[str, Any]:
        """Generate Zapier documentation mock content"""
        return {
            'title': 'Zapier Platform Documentation',
            'description': 'Build integrations for the Zapier platform',
            'keywords': ['api', 'platform', 'integration', 'webhook', 'developer'],
            'content': '''# Zapier Platform Documentation

## Authentication Methods
- API Key authentication
- OAuth 2.0 flows
- Session-based auth
- Custom authentication

## Webhook Best Practices
1. **Signature Verification**
   - Always verify webhook signatures
   - Use HMAC-SHA256 for validation
   - Implement replay attack protection

2. **Error Handling**
   - Return 2xx status codes for success
   - Handle timeouts gracefully
   - Implement exponential backoff

3. **Performance Optimization**
   - Process webhooks asynchronously
   - Use proper HTTP status codes
   - Implement idempotency

## Common Issues
- **403 Forbidden Errors**: Check authentication
- **Timeout Issues**: Optimize endpoint performance
- **Rate Limiting**: Implement proper retry logic
'''
        }
    
    def _generate_zapier_community_content(self, url: str) -> Dict[str, Any]:
        """Generate Zapier community mock content"""
        return {
            'title': 'Zapier Community - Get Help & Share Ideas',
            'description': 'Connect with other Zapier users and experts',
            'keywords': ['community', 'support', 'help', 'discussion'],
            'content': '''# Zapier Community

## Popular Topics
- Webhook troubleshooting
- API integration help
- Automation best practices
- Platform development

## Recent Discussions
### "Webhook signature verification failing after API update"
*Posted by: developer123*

Our webhook integration stopped working after the latest API update. Getting 403 errors on signature verification. Has anyone else experienced this?

**Solutions suggested:**
- Check for header case changes
- Verify HMAC calculation
- Update to latest API version

### "Rate limiting best practices"
*Posted by: integration_expert*

What are the best practices for handling rate limits in Zapier integrations?

**Key recommendations:**
- Implement exponential backoff
- Use webhook queuing
- Monitor rate limit headers
'''
        }
    
    def _generate_zapier_learning_content(self, url: str) -> Dict[str, Any]:
        """Generate Zapier learning content"""
        return {
            'title': 'Zapier University - Learn Automation',
            'description': 'Master automation with Zapier courses',
            'keywords': ['learning', 'courses', 'automation', 'training'],
            'content': '''# Zapier University

## Course Categories
- Automation Fundamentals
- Advanced Workflows
- Business Process Optimization
- Developer Training

## Featured Course: "Advanced Webhook Integration"
Learn how to build robust webhook integrations that handle:
- Signature verification
- Error handling and retries
- Performance optimization
- Security best practices

### Module 1: Webhook Fundamentals
- Understanding webhook architecture
- Implementing proper endpoints
- Handling different event types

### Module 2: Security & Authentication
- HMAC signature verification
- Implementing authentication
- Preventing replay attacks

### Module 3: Error Handling
- Graceful error responses
- Retry mechanisms
- Monitoring and alerting
'''
        }
    
    def _generate_generic_mock_content(self, url: str) -> Dict[str, Any]:
        """Generate generic mock content for unknown domains"""
        return {
            'title': f'Documentation - {urlparse(url).netloc}',
            'description': 'Technical documentation and guides',
            'keywords': ['documentation', 'api', 'integration'],
            'content': f'''# Technical Documentation

This is mock content for {url}

## Overview
Comprehensive documentation for developers and integrators.

## Key Topics
- API Reference
- Integration Guides
- Best Practices
- Troubleshooting

## Getting Started
Follow our quick start guide to begin integrating with our platform.
'''
        }

# Global service instance
firecrawl_service = FirecrawlService()
