
"""
Target Company Service for AgentCraft
Manages hot-swappable company contexts and configurations
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TargetCompany:
    """Configuration for a target company context"""
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

class TargetCompanyService:
    """Service for managing target company configurations"""
    
    def __init__(self):
        self.companies = self._initialize_companies()
        self.current_company = "zapier"  # Default to Zapier
    
    def _initialize_companies(self) -> Dict[str, TargetCompany]:
        """Initialize predefined company configurations"""
        return {
            "zapier": TargetCompany(
                id="zapier",
                name="zapier",
                display_name="Zapier",
                description="Integration platform connecting 7000+ apps",
                industry="Integration & Automation",
                primary_color="#FF4A00",
                logo_emoji="⚡",
                
                documentation_urls=[
                    "https://docs.zapier.com/platform/home",
                    "https://platform.zapier.com/docs",
                    "https://zapier.com/developer"
                ],
                community_urls=[
                    "https://community.zapier.com/",
                    "https://community.zapier.com/developer-discussion-13"
                ],
                marketing_urls=[
                    "https://zapier.com/",
                    "https://zapier.com/features",
                    "https://zapier.com/pricing"
                ],
                blog_urls=[
                    "https://zapier.com/blog/"
                ],
                learning_urls=[
                    "https://learn.zapier.com/",
                    "https://zapier.com/resources/guides"
                ],
                
                primary_use_cases=[
                    "Webhook troubleshooting and debugging",
                    "API integration setup and optimization",
                    "Automation workflow design",
                    "Data transformation and mapping",
                    "Error handling and retry logic"
                ],
                
                technical_focus_areas=[
                    "REST API integrations",
                    "Webhook signature verification",
                    "Authentication (OAuth, API keys)",
                    "Rate limiting and performance",
                    "Data validation and transformation",
                    "Error handling and monitoring"
                ],
                
                customer_pain_points=[
                    "Complex webhook signature verification",
                    "API rate limiting issues",
                    "Authentication failures",
                    "Data transformation challenges",
                    "Integration performance problems",
                    "Error debugging and troubleshooting"
                ],
                
                main_competitors=[
                    "Microsoft Power Automate",
                    "Salesforce MuleSoft",
                    "Workato",
                    "Integromat (Make.com)",
                    "Pipedream",
                    "IFTTT"
                ],
                
                competitive_advantages=[
                    "Largest app ecosystem (7000+ integrations)",
                    "No-code/low-code approach",
                    "Enterprise-grade security and compliance",
                    "Advanced workflow automation",
                    "Developer platform for custom integrations"
                ],
                
                pricing_model="Freemium with usage-based tiers",
                target_market="SMB to Enterprise automation needs"
            ),
            
            "hubspot": TargetCompany(
                id="hubspot",
                name="hubspot",
                display_name="HubSpot",
                description="CRM and marketing automation platform",
                industry="CRM & Marketing",
                primary_color="#FF7A59",
                logo_emoji="🧲",
                
                documentation_urls=[
                    "https://developers.hubspot.com/",
                    "https://developers.hubspot.com/docs/api/overview"
                ],
                community_urls=[
                    "https://community.hubspot.com/",
                    "https://developers.hubspot.com/community"
                ],
                marketing_urls=[
                    "https://www.hubspot.com/",
                    "https://www.hubspot.com/products"
                ],
                blog_urls=[
                    "https://blog.hubspot.com/"
                ],
                learning_urls=[
                    "https://academy.hubspot.com/"
                ],
                
                primary_use_cases=[
                    "CRM data synchronization",
                    "Marketing automation workflows",
                    "Contact management and segmentation",
                    "Sales pipeline optimization",
                    "Customer journey tracking"
                ],
                
                technical_focus_areas=[
                    "HubSpot API integrations",
                    "CRM data synchronization",
                    "Webhook event handling",
                    "Contact and deal management",
                    "Marketing automation APIs"
                ],
                
                customer_pain_points=[
                    "Complex CRM data mapping",
                    "API rate limiting",
                    "Contact deduplication",
                    "Integration data consistency",
                    "Custom property synchronization"
                ],
                
                main_competitors=[
                    "Salesforce",
                    "Pipedrive",
                    "Marketo",
                    "Pardot",
                    "ActiveCampaign"
                ],
                
                competitive_advantages=[
                    "All-in-one platform approach",
                    "Free CRM tier",
                    "Integrated marketing tools",
                    "Strong developer ecosystem"
                ],
                
                pricing_model="Freemium with feature-based tiers",
                target_market="SMB to Mid-market sales and marketing teams"
            ),
            
            "shopify": TargetCompany(
                id="shopify",
                name="shopify",
                display_name="Shopify",
                description="E-commerce platform and ecosystem",
                industry="E-commerce",
                primary_color="#7AB55C",
                logo_emoji="🛍️",
                
                documentation_urls=[
                    "https://shopify.dev/",
                    "https://shopify.dev/docs/api"
                ],
                community_urls=[
                    "https://community.shopify.com/",
                    "https://community.shopify.com/c/shopify-apis-and-technology"
                ],
                marketing_urls=[
                    "https://www.shopify.com/",
                    "https://www.shopify.com/plus"
                ],
                blog_urls=[
                    "https://www.shopify.com/blog/"
                ],
                learning_urls=[
                    "https://www.shopify.com/learn"
                ],
                
                primary_use_cases=[
                    "E-commerce integrations",
                    "Payment processing",
                    "Inventory management",
                    "Order fulfillment",
                    "App development"
                ],
                
                technical_focus_areas=[
                    "Shopify API integrations",
                    "Webhook event processing",
                    "Payment gateway integrations",
                    "App development and deployment",
                    "GraphQL and REST APIs"
                ],
                
                customer_pain_points=[
                    "Complex app development requirements",
                    "API rate limiting",
                    "Webhook reliability",
                    "Payment processing issues",
                    "Inventory synchronization"
                ],
                
                main_competitors=[
                    "WooCommerce",
                    "BigCommerce",
                    "Magento",
                    "Squarespace Commerce",
                    "Salesforce Commerce Cloud"
                ],
                
                competitive_advantages=[
                    "Comprehensive app ecosystem",
                    "Scalable infrastructure",
                    "Integrated payment processing",
                    "Strong developer tools"
                ],
                
                pricing_model="Subscription with transaction fees",
                target_market="SMB to Enterprise e-commerce businesses"
            )
        }
    
    def get_current_company(self) -> TargetCompany:
        """Get the currently selected company configuration"""
        return self.companies[self.current_company]
    
    def set_current_company(self, company_id: str) -> bool:
        """Switch to a different target company"""
        if company_id in self.companies:
            self.current_company = company_id
            return True
        return False
    
    def get_all_companies(self) -> Dict[str, TargetCompany]:
        """Get all available company configurations"""
        return self.companies
    
    def get_company_context(self, company_id: str = None) -> Dict[str, Any]:
        """Get contextual information for agents"""
        company = self.companies.get(company_id or self.current_company)
        if not company:
            return {}
        
        return {
            "company_name": company.display_name,
            "industry": company.industry,
            "primary_use_cases": company.primary_use_cases,
            "technical_focus": company.technical_focus_areas,
            "customer_pain_points": company.customer_pain_points,
            "competitive_landscape": {
                "main_competitors": company.main_competitors,
                "our_advantages": company.competitive_advantages
            },
            "knowledge_sources": {
                "documentation": company.documentation_urls,
                "community": company.community_urls,
                "learning": company.learning_urls
            }
        }
    
    def get_crawl_urls(self, company_id: str = None) -> List[str]:
        """Get all URLs to crawl for knowledge base"""
        company = self.companies.get(company_id or self.current_company)
        if not company:
            return []
        
        all_urls = []
        all_urls.extend(company.documentation_urls)
        all_urls.extend(company.community_urls)
        all_urls.extend(company.marketing_urls)
        all_urls.extend(company.blog_urls)
        all_urls.extend(company.learning_urls)
        
        return all_urls

# Global service instance
target_company_service = TargetCompanyService()
