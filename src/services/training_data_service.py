
"""
Training Data Service for AgentCraft
Generates realistic mock tickets and resolutions for training
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from uuid import uuid4

@dataclass
class MockTicket:
    """Represents a customer support ticket"""
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    customer_type: str
    tags: List[str]
    created_at: str
    resolved_at: Optional[str]
    resolution: Optional[str]
    agent_notes: List[str]
    escalated: bool
    satisfaction_rating: Optional[int]

class TrainingDataService:
    """Service for generating and managing training data"""
    
    def __init__(self):
        self.ticket_templates = self._initialize_ticket_templates()
    
    def _initialize_ticket_templates(self) -> Dict[str, Dict]:
        """Initialize ticket templates for different categories"""
        return {
            "webhook_issues": {
                "titles": [
                    "Webhook suddenly stopped working after integration update",
                    "Getting 403 forbidden errors on webhook endpoint",
                    "Webhook signature verification failing intermittently",
                    "Webhook deliveries timing out after 30 seconds",
                    "Missing webhook events for automated workflows",
                    "Webhook retries not working as expected",
                    "Duplicate webhook events causing data inconsistency"
                ],
                "descriptions": [
                    "Our Zapier integration was working perfectly for months, but after the recent platform update, we're getting 403 errors on all webhook deliveries. The signature verification seems to be failing even though we haven't changed our code. This is blocking our automated order processing workflow.",
                    "We have a webhook endpoint that processes automation triggers, but it's randomly failing signature verification. About 20% of webhooks fail with 'invalid signature' errors. The same code works fine in our staging environment. Our production workflow is becoming unreliable.",
                    "Our webhook endpoint is taking 25-35 seconds to process incoming data, which causes Zapier to timeout and retry. This creates duplicate entries in our system. We need help optimizing our endpoint or handling the retries properly."
                ],
                "tags": ["webhook", "integration", "signature", "403", "timeout", "automation", "api"],
                "priority_distribution": {"high": 0.4, "medium": 0.5, "low": 0.1},
                "customer_types": ["enterprise", "pro", "startup"]
            },
            
            "api_integration": {
                "titles": [
                    "API rate limits blocking our automation workflows",
                    "Authentication errors with OAuth 2.0 integration",
                    "API responses are inconsistent between environments",
                    "Integration setup failing during app authorization",
                    "API endpoints returning unexpected data format",
                    "Bulk data sync hitting API timeout limits",
                    "Custom integration not appearing in app directory"
                ],
                "descriptions": [
                    "We're hitting rate limits on the Zapier Platform API when syncing large datasets. Our automation needs to process 5000+ records per hour, but we're being throttled. Is there a way to get higher rate limits or optimize our API usage pattern?",
                    "Our OAuth 2.0 integration randomly fails during the authorization flow. Users get redirected properly, but about 30% of the time the token exchange fails with 'invalid_grant' errors. This is frustrating our customers who are trying to set up automations.",
                    "We have a custom integration that works in development but fails in production. The API responses have different field names and the webhook payload structure is inconsistent. Our automation workflows are breaking because of these discrepancies."
                ],
                "tags": ["api", "rate-limit", "oauth", "authentication", "integration", "bulk-sync"],
                "priority_distribution": {"high": 0.3, "medium": 0.6, "low": 0.1},
                "customer_types": ["enterprise", "pro", "developer"]
            },
            
            "workflow_automation": {
                "titles": [
                    "Multi-step automation workflow not triggering properly",
                    "Data transformation failing in complex workflows",
                    "Conditional logic not working as expected in Zaps",
                    "Workflow performance degrading with large datasets",
                    "Error handling not catching integration failures",
                    "Automation workflow stuck in infinite loop",
                    "Filter conditions not properly excluding records"
                ],
                "descriptions": [
                    "We built a complex automation that should trigger when a form is submitted, update multiple databases, and send notifications. However, the workflow only completes about 60% of the time. The other 40% fail at different steps without clear error messages.",
                    "Our data transformation logic worked fine with small datasets, but now that we're processing 1000+ records per day, the automation is timing out. We need help optimizing the workflow or breaking it into smaller chunks.",
                    "We set up conditional logic to route different types of leads to different sales reps, but the conditions aren't working correctly. All leads are going to the default rep instead of being distributed based on our rules."
                ],
                "tags": ["automation", "workflow", "transformation", "conditional", "performance", "error-handling"],
                "priority_distribution": {"high": 0.2, "medium": 0.7, "low": 0.1},
                "customer_types": ["business", "pro", "enterprise"]
            },
            
            "data_sync": {
                "titles": [
                    "Customer data not syncing between CRM and marketing platform",
                    "Duplicate records being created in data synchronization",
                    "Data mapping incorrect for custom fields in integration",
                    "Real-time sync delays causing workflow issues",
                    "Data validation errors preventing sync completion",
                    "Historical data migration failing for large datasets",
                    "Field mapping lost after platform update"
                ],
                "descriptions": [
                    "Our CRM and email marketing platform integration was syncing perfectly, but now customer data is taking 4-6 hours to sync instead of the expected real-time updates. This delay is causing issues with our marketing campaigns and lead nurturing workflows.",
                    "Every time a customer record is updated, we're getting duplicate entries in our destination system. The automation should update existing records, not create new ones. This is causing data integrity issues across our platforms.",
                    "After mapping custom fields in our integration, the data is not transferring correctly. Standard fields work fine, but our custom properties are either empty or contain incorrect values. Our sales team relies on this data for lead qualification."
                ],
                "tags": ["data-sync", "crm", "mapping", "duplicates", "custom-fields", "real-time"],
                "priority_distribution": {"high": 0.3, "medium": 0.6, "low": 0.1},
                "customer_types": ["business", "enterprise", "pro"]
            },
            
            "competitive_analysis": {
                "titles": [
                    "Comparing Zapier vs Microsoft Power Automate for enterprise",
                    "Cost analysis: Zapier vs custom integration development",
                    "Feature comparison with Integromat for complex workflows",
                    "Migration strategy from Workato to Zapier platform",
                    "Performance benchmarking against competitor solutions",
                    "Zapier vs Pipedream for developer-focused integrations",
                    "ROI analysis for switching from legacy integration platform"
                ],
                "descriptions": [
                    "Our enterprise team is evaluating automation platforms and we need a detailed comparison between Zapier and Microsoft Power Automate. We're particularly interested in enterprise features, security compliance, and total cost of ownership for 500+ users.",
                    "We're currently using Workato but considering migrating to Zapier for better app ecosystem and pricing. Can you provide a detailed migration strategy and feature comparison? We have 50+ active workflows that need to be migrated.",
                    "Our development team is comparing Zapier vs Pipedream for building custom integrations. We need code-level control but also want the ease of no-code for business users. What are the pros and cons of each platform for our hybrid approach?"
                ],
                "tags": ["competitive", "comparison", "enterprise", "migration", "roi", "power-automate", "workato"],
                "priority_distribution": {"high": 0.4, "medium": 0.5, "low": 0.1},
                "customer_types": ["enterprise", "business", "developer"]
            }
        }
    
    def generate_mock_tickets(self, count: int = 100, 
                            company_context: Dict[str, Any] = None) -> List[MockTicket]:
        """Generate realistic mock tickets based on company context"""
        tickets = []
        
        # Get company-specific context
        try:
            from .target_company_service import target_company_service
            current_company = target_company_service.get_current_company()
            focus_areas = current_company.technical_focus_areas
            pain_points = current_company.customer_pain_points
        except ImportError:
            focus_areas = ["webhook", "api", "integration"]
            pain_points = ["signature verification", "rate limiting"]
        
        categories = list(self.ticket_templates.keys())
        
        for i in range(count):
            category = random.choice(categories)
            template = self.ticket_templates[category]
            
            # Generate ticket details
            ticket_id = f"TK-{str(uuid4())[:8].upper()}"
            title = random.choice(template["titles"])
            description = random.choice(template["descriptions"])
            
            # Determine priority based on category distribution
            priority_rand = random.random()
            priority_dist = template["priority_distribution"]
            if priority_rand < priority_dist["high"]:
                priority = "high"
            elif priority_rand < priority_dist["high"] + priority_dist["medium"]:
                priority = "medium"
            else:
                priority = "low"
            
            # Generate timestamps
            created_days_ago = random.randint(1, 90)
            created_at = (datetime.now() - timedelta(days=created_days_ago)).isoformat()
            
            # Determine if ticket is resolved
            is_resolved = random.random() < 0.75  # 75% of tickets are resolved
            resolved_at = None
            resolution = None
            satisfaction_rating = None
            
            if is_resolved:
                resolution_hours = random.randint(1, 48)
                resolved_at = (datetime.fromisoformat(created_at) + 
                             timedelta(hours=resolution_hours)).isoformat()
                resolution = self._generate_resolution(category, title, description)
                satisfaction_rating = random.randint(3, 5)  # Mostly satisfied customers
            
            # Generate agent notes
            agent_notes = self._generate_agent_notes(category, is_resolved)
            
            # Determine escalation
            escalated = priority == "high" and random.random() < 0.3
            
            # Status based on resolution and priority
            if is_resolved:
                status = "resolved"
            elif priority == "high":
                status = "in_progress"
            else:
                status = random.choice(["open", "in_progress"])
            
            ticket = MockTicket(
                id=ticket_id,
                title=title,
                description=description,
                category=category,
                priority=priority,
                status=status,
                customer_type=random.choice(template["customer_types"]),
                tags=template["tags"],
                created_at=created_at,
                resolved_at=resolved_at,
                resolution=resolution,
                agent_notes=agent_notes,
                escalated=escalated,
                satisfaction_rating=satisfaction_rating
            )
            
            tickets.append(ticket)
        
        return sorted(tickets, key=lambda t: t.created_at, reverse=True)
    
    def _generate_resolution(self, category: str, title: str, description: str) -> str:
        """Generate realistic resolution based on ticket category"""
        resolutions = {
            "webhook_issues": [
                "Updated webhook signature verification to use new header format (x-zapier-signature). Provided code example for proper HMAC-SHA256 validation. Customer confirmed issue resolved after implementation.",
                "Identified timeout issue caused by synchronous database operations. Recommended implementing asynchronous processing and webhook queue. Customer optimized endpoint to respond within 5 seconds.",
                "Resolved 403 errors by updating API authentication headers. Issue was caused by deprecated header format after platform upgrade. Provided migration guide for new authentication method."
            ],
            "api_integration": [
                "Increased rate limit quota for enterprise customer from 1000 to 5000 requests/hour. Provided guidance on implementing exponential backoff for optimal API usage patterns.",
                "Fixed OAuth 2.0 integration by updating redirect URI whitelist and token refresh logic. Issue was caused by expired refresh tokens not being handled properly.",
                "Identified API response inconsistency between environments. Updated staging environment to match production schema. Provided field mapping documentation for future integrations."
            ],
            "workflow_automation": [
                "Optimized automation workflow by splitting large dataset processing into smaller batches of 100 records. Implemented error handling and retry logic for failed operations.",
                "Fixed conditional logic by updating filter conditions to use exact string matching instead of contains. Provided testing guide for complex workflow conditions.",
                "Resolved workflow infinite loop by adding proper exit conditions and workflow execution limits. Implemented monitoring to prevent similar issues."
            ],
            "data_sync": [
                "Resolved sync delays by optimizing webhook delivery priority for real-time operations. Customer data now syncs within 30 seconds instead of 4-6 hours.",
                "Fixed duplicate record creation by implementing proper record matching logic based on unique identifiers. Updated field mapping to include primary key fields.",
                "Corrected custom field mapping by updating API endpoints to use latest field schema. Provided field mapping validation tool for future custom integrations."
            ],
            "competitive_analysis": [
                "Provided comprehensive comparison document highlighting Zapier's superior app ecosystem (7000+ vs 400+ apps), faster time-to-market, and 40% lower total cost of ownership for enterprise deployments.",
                "Created detailed migration strategy with timeline estimates, cost analysis, and risk mitigation plan. Scheduled technical consultation to review specific workflow migration requirements.",
                "Delivered ROI analysis showing 65% cost savings and 3x faster implementation compared to custom development. Included success metrics and implementation timeline."
            ]
        }
        
        category_resolutions = resolutions.get(category, ["Issue resolved through standard troubleshooting process."])
        return random.choice(category_resolutions)
    
    def _generate_agent_notes(self, category: str, is_resolved: bool) -> List[str]:
        """Generate realistic agent notes for ticket progression"""
        notes = [
            f"Initial triage: Categorized as {category} issue, assigned to specialist team",
            "Gathered additional system information and error logs from customer",
        ]
        
        if category == "webhook_issues":
            notes.append("Analyzed webhook signature verification code and identified header format issue")
            if is_resolved:
                notes.append("Provided updated code example and testing instructions")
                notes.append("Customer confirmed resolution after implementing suggested changes")
        
        elif category == "api_integration":
            notes.append("Reviewed API authentication flow and rate limiting patterns")
            if is_resolved:
                notes.append("Implemented rate limit increase and provided optimization guidance")
                notes.append("Customer tested integration successfully in production environment")
        
        elif category == "competitive_analysis":
            notes.append("Prepared competitive analysis documentation and ROI calculations")
            if is_resolved:
                notes.append("Scheduled technical consultation with customer's architecture team")
                notes.append("Delivered comprehensive comparison and migration strategy")
        
        if not is_resolved:
            notes.append("Awaiting customer response for additional testing")
        
        return notes
    
    def export_training_data(self, tickets: List[MockTicket], format: str = "json") -> str:
        """Export training data in specified format"""
        if format == "json":
            return json.dumps([
                {
                    "id": ticket.id,
                    "title": ticket.title,
                    "description": ticket.description,
                    "category": ticket.category,
                    "priority": ticket.priority,
                    "status": ticket.status,
                    "customer_type": ticket.customer_type,
                    "tags": ticket.tags,
                    "created_at": ticket.created_at,
                    "resolved_at": ticket.resolved_at,
                    "resolution": ticket.resolution,
                    "agent_notes": ticket.agent_notes,
                    "escalated": ticket.escalated,
                    "satisfaction_rating": ticket.satisfaction_rating
                } for ticket in tickets
            ], indent=2)
        
        # Add other formats as needed (CSV, etc.)
        return ""
    
    def get_training_insights(self, tickets: List[MockTicket]) -> Dict[str, Any]:
        """Generate insights from training data for system improvement"""
        total_tickets = len(tickets)
        resolved_tickets = [t for t in tickets if t.status == "resolved"]
        
        # Category distribution
        category_dist = {}
        for ticket in tickets:
            category_dist[ticket.category] = category_dist.get(ticket.category, 0) + 1
        
        # Priority distribution
        priority_dist = {}
        for ticket in tickets:
            priority_dist[ticket.priority] = priority_dist.get(ticket.priority, 0) + 1
        
        # Average resolution time
        resolution_times = []
        for ticket in resolved_tickets:
            if ticket.resolved_at:
                created = datetime.fromisoformat(ticket.created_at)
                resolved = datetime.fromisoformat(ticket.resolved_at)
                hours = (resolved - created).total_seconds() / 3600
                resolution_times.append(hours)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Satisfaction analysis
        ratings = [t.satisfaction_rating for t in resolved_tickets if t.satisfaction_rating]
        avg_satisfaction = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "total_tickets": total_tickets,
            "resolution_rate": len(resolved_tickets) / total_tickets if total_tickets > 0 else 0,
            "avg_resolution_time_hours": round(avg_resolution_time, 2),
            "avg_satisfaction_rating": round(avg_satisfaction, 2),
            "category_distribution": category_dist,
            "priority_distribution": priority_dist,
            "escalation_rate": len([t for t in tickets if t.escalated]) / total_tickets if total_tickets > 0 else 0,
            "common_tags": self._get_common_tags(tickets),
            "training_data_quality": "High - Diverse scenarios with realistic resolutions"
        }
    
    def _get_common_tags(self, tickets: List[MockTicket]) -> List[Dict[str, Any]]:
        """Get most common tags across all tickets"""
        tag_counts = {}
        for ticket in tickets:
            for tag in ticket.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"tag": tag, "count": count} for tag, count in sorted_tags[:10]]

# Global service instance
training_data_service = TrainingDataService()
