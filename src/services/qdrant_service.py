"""
Qdrant Vector Database Service for AgentCraft
Handles knowledge base indexing and semantic search
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
from dataclasses import dataclass
import logging

# Qdrant imports
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, 
        VectorParams, 
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not installed. Run: pip install qdrant-client")

# Embedding model imports
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    logging.warning("Sentence transformers not installed. Run: pip install sentence-transformers")

@dataclass
class KnowledgeArticle:
    """Represents a knowledge base article"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: str
    updated_at: str
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None

class QdrantService:
    """Service for managing vector database operations"""
    
    def __init__(
        self, 
        collection_name: str = "agentcraft_knowledge",
        host: str = "localhost",
        port: int = 6333,
        use_memory: bool = True  # Use in-memory for demo
    ):
        self.collection_name = collection_name
        self.embedding_dim = 384  # MiniLM dimension
        
        if QDRANT_AVAILABLE:
            if use_memory:
                # Use in-memory Qdrant for demo (no server needed)
                self.client = QdrantClient(":memory:")
            else:
                # Connect to Qdrant server
                self.client = QdrantClient(host=host, port=port)
            
            self._initialize_collection()
        else:
            self.client = None
            logging.error("Qdrant not available")
        
        if EMBEDDINGS_AVAILABLE:
            # Use MiniLM for fast embeddings
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.encoder = None
            logging.error("Sentence transformers not available")
    
    def _initialize_collection(self):
        """Initialize or recreate the collection"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                # Create collection with vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logging.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logging.error(f"Failed to initialize collection: {e}")
    
    def generate_mock_knowledge_base(self, company_context: Dict[str, Any] = None) -> List[KnowledgeArticle]:
        """Generate mock support articles for the target company"""
        
        # Import here to avoid circular imports
        try:
            from .target_company_service import target_company_service
            current_company = target_company_service.get_current_company()
            company_name = current_company.display_name
            focus_areas = current_company.technical_focus_areas
            pain_points = current_company.customer_pain_points
        except ImportError:
            company_name = "Zapier"
            focus_areas = ["webhook", "api", "integration"]
            pain_points = ["signature verification", "rate limiting"]
        
        articles = [
            # Zapier Integration-related articles
            KnowledgeArticle(
                id="kb_001",
                title=f"{company_name} Webhook Signature Verification Guide",
                content=f"""
                Complete guide to implementing webhook signature verification for {company_name} Platform API v2.1.3.
                
                Common Issues:
                - 403 Forbidden errors after platform API upgrade
                - HMAC signature mismatches in {company_name} webhooks
                - Header case sensitivity changes in new API version
                - Integration authentication failures
                
                Solution for {company_name} Platform:
                1. Verify you're using the correct header names (x-{company_name.lower()}-signature)
                2. Include sha256= prefix in signature format per {company_name} standards
                3. Use constant-time comparison for security
                4. Handle webhook retries properly
                
                {company_name} Code Example:
                ```python
                import hmac
                import hashlib
                
                def verify_{company_name.lower()}_signature(payload, signature, secret):
                    expected = hmac.new(
                        secret.encode(),
                        payload.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    return hmac.compare_digest(f"sha256={{expected}}", signature)
                
                # {company_name}-specific webhook handling
                def handle_{company_name.lower()}_webhook(request):
                    signature = request.headers.get('X-{company_name}-Signature')
                    if not verify_{company_name.lower()}_signature(request.body, signature, WEBHOOK_SECRET):
                        return {'error': 'Invalid signature'}, 403
                    
                    # Process {company_name} event
                    return process_automation_event(request.json)
                ```
                
                {company_name} Platform Specific Notes:
                - Use HTTPS endpoints only for production integrations
                - Implement exponential backoff for webhook retries
                - Handle {company_name}'s rate limiting appropriately
                """,
                category="Technical Integration",
                tags=["webhook", "signature", "security", "api", "zapier", "automation"],
                created_at="2024-01-15T10:00:00Z",
                updated_at="2024-08-20T14:30:00Z"
            ),
            KnowledgeArticle(
                id="kb_002",
                title="SSL Certificate Troubleshooting",
                content="""
                Resolve SSL certificate verification errors in webhook integrations.
                
                Symptoms:
                - SSL: CERTIFICATE_VERIFY_FAILED errors
                - Connection refused on HTTPS endpoints
                - Certificate chain validation failures
                
                Solutions:
                1. Update certificate bundle
                2. Verify certificate chain completeness
                3. Check certificate expiration
                4. Test with curl: curl -v https://your-endpoint.com
                
                For development only:
                - Disable SSL verification (not recommended for production)
                - Use custom certificate bundle
                """,
                category="Technical Integration",
                tags=["ssl", "certificate", "https", "security", "troubleshooting"],
                created_at="2024-02-10T09:00:00Z",
                updated_at="2024-08-15T11:00:00Z"
            ),
            KnowledgeArticle(
                id="kb_003",
                title="API Rate Limiting Best Practices",
                content="""
                Handle API rate limits effectively to prevent service disruptions.
                
                Rate Limit Headers:
                - X-RateLimit-Limit: Maximum requests
                - X-RateLimit-Remaining: Requests left
                - X-RateLimit-Reset: Reset timestamp
                
                Implementation:
                1. Implement exponential backoff
                2. Use queue-based request management
                3. Monitor rate limit headers
                4. Implement circuit breaker pattern
                
                Retry Strategy:
                - Initial delay: 1 second
                - Max retries: 3
                - Backoff multiplier: 2
                """,
                category="API Management",
                tags=["rate-limit", "api", "retry", "performance"],
                created_at="2024-03-05T12:00:00Z",
                updated_at="2024-08-10T16:00:00Z"
            ),
            # Billing-related articles
            KnowledgeArticle(
                id="kb_004",
                title="Subscription Proration Calculations",
                content="""
                Understanding subscription proration for mid-cycle changes.
                
                Scenarios:
                1. Upgrade: Charge prorated difference immediately
                2. Downgrade: Credit applied to next invoice
                3. Cancellation: Refund unused portion
                
                Formula:
                Prorated Amount = (New Price - Old Price) × (Days Remaining / Days in Period)
                
                Examples:
                - Monthly to Annual: Calculate daily rate difference
                - Plan upgrade: Immediate charge for difference
                - Mid-cycle cancellation: Refund calculation
                """,
                category="Billing",
                tags=["billing", "subscription", "proration", "refund"],
                created_at="2024-01-20T11:00:00Z",
                updated_at="2024-08-18T13:00:00Z"
            ),
            KnowledgeArticle(
                id="kb_005",
                title="Payment Failure Handling",
                content="""
                Automated payment failure recovery strategies.
                
                Failure Types:
                - Insufficient funds
                - Expired cards
                - Bank declines
                - Network errors
                
                Dunning Process:
                1. Immediate retry (network errors only)
                2. Day 3: First retry with email notification
                3. Day 7: Second retry with warning
                4. Day 14: Final retry before suspension
                5. Day 21: Account suspension
                
                Best Practices:
                - Send pre-dunning notifications
                - Offer payment method update reminders
                - Implement grace periods
                """,
                category="Billing",
                tags=["payment", "dunning", "retry", "billing"],
                created_at="2024-02-25T10:00:00Z",
                updated_at="2024-08-12T14:00:00Z"
            ),
            # Integration guides
            KnowledgeArticle(
                id="kb_006",
                title="Quick Start: Webhook Integration",
                content="""
                Set up webhook integration in 5 minutes.
                
                Steps:
                1. Register webhook endpoint in settings
                2. Configure events to receive
                3. Implement signature verification
                4. Handle events asynchronously
                5. Implement retry logic
                
                Required Headers:
                - Content-Type: application/json
                - X-Webhook-Signature: sha256=...
                - X-Webhook-Timestamp: Unix timestamp
                
                Testing:
                - Use webhook testing tool
                - Verify with ngrok for local development
                - Monitor webhook logs
                """,
                category="Getting Started",
                tags=["webhook", "integration", "quickstart", "setup"],
                created_at="2024-01-01T08:00:00Z",
                updated_at="2024-08-22T10:00:00Z"
            ),
            # Troubleshooting guides
            KnowledgeArticle(
                id="kb_007",
                title="Debugging 403 Forbidden Errors",
                content="""
                Systematic approach to resolving 403 errors.
                
                Common Causes:
                1. Invalid API key or token
                2. Signature verification failure
                3. IP whitelist restrictions
                4. Rate limit exceeded
                5. Incorrect permissions/scopes
                
                Debugging Steps:
                1. Check authentication headers
                2. Verify signature calculation
                3. Review API logs
                4. Test with minimal payload
                5. Verify account permissions
                
                Tools:
                - Postman for API testing
                - curl for command-line debugging
                - Request bin for webhook inspection
                """,
                category="Troubleshooting",
                tags=["403", "forbidden", "authentication", "debugging"],
                created_at="2024-03-10T09:00:00Z",
                updated_at="2024-08-20T15:00:00Z"
            ),
            # Best practices
            KnowledgeArticle(
                id="kb_008",
                title="Webhook Security Best Practices",
                content="""
                Secure your webhook implementation.
                
                Security Measures:
                1. Always verify signatures
                2. Use HTTPS only
                3. Implement request timeouts
                4. Validate timestamp freshness
                5. Store secrets securely
                6. Log security events
                7. Implement rate limiting
                
                Code Security:
                - Never log sensitive data
                - Use constant-time comparisons
                - Rotate secrets regularly
                - Monitor for anomalies
                
                Compliance:
                - PCI DSS for payment webhooks
                - GDPR for user data
                - SOC 2 requirements
                """,
                category="Security",
                tags=["security", "webhook", "compliance", "best-practices"],
                created_at="2024-04-01T10:00:00Z",
                updated_at="2024-08-19T12:00:00Z"
            )
        ]
        
        return articles
    
    def index_knowledge_base(self, articles: List[KnowledgeArticle] = None):
        """Index knowledge base articles into Qdrant"""
        if not self.client or not self.encoder:
            logging.error("Qdrant or encoder not available")
            return False
        
        if articles is None:
            articles = self.generate_mock_knowledge_base()
        
        points = []
        for article in articles:
            # Combine title and content for embedding
            text_to_embed = f"{article.title}\n\n{article.content}"
            
            # Generate embedding
            embedding = self.encoder.encode(text_to_embed).tolist()
            
            # Create point with metadata
            point = PointStruct(
                id=hashlib.md5(article.id.encode()).hexdigest()[:8],
                vector=embedding,
                payload={
                    "id": article.id,
                    "title": article.title,
                    "content": article.content[:500],  # Store truncated content
                    "category": article.category,
                    "tags": article.tags,
                    "created_at": article.created_at,
                    "updated_at": article.updated_at
                }
            )
            points.append(point)
        
        # Upload points to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        logging.info(f"Indexed {len(points)} articles into Qdrant")
        return True
    
    def search(
        self, 
        query: str, 
        limit: int = 5,
        category_filter: Optional[str] = None,
        tags_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search knowledge base using semantic similarity"""
        if not self.client or not self.encoder:
            logging.error("Qdrant or encoder not available")
            return []
        
        # Generate query embedding
        query_vector = self.encoder.encode(query).tolist()
        
        # Build filter conditions
        filter_conditions = []
        if category_filter:
            filter_conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category_filter)
                )
            )
        
        # Perform search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )
        
        # Format results
        results = []
        for hit in search_result:
            result = {
                "id": hit.payload.get("id"),
                "title": hit.payload.get("title"),
                "content": hit.payload.get("content"),
                "category": hit.payload.get("category"),
                "tags": hit.payload.get("tags"),
                "similarity_score": hit.score,
                "updated_at": hit.payload.get("updated_at")
            }
            results.append(result)
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get Qdrant performance metrics"""
        if not self.client:
            return {
                "status": "unavailable",
                "message": "Qdrant not connected"
            }
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "status": "healthy",
                "collection": self.collection_name,
                "vector_count": collection_info.vectors_count,
                "indexed_points": collection_info.points_count,
                "embedding_dimension": self.embedding_dim,
                "distance_metric": "cosine",
                "search_performance": {
                    "average_latency_ms": 12,  # Mock data
                    "p95_latency_ms": 25,
                    "p99_latency_ms": 45,
                    "queries_per_second": 150
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

# Singleton instance
qdrant_service = QdrantService(use_memory=True)