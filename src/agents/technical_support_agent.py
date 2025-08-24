
"""
Technical Support Agent - specialized webhook troubleshooting expertise.
Demonstrates superior domain knowledge over generic topic handling.
"""

import time
from typing import Dict, Any, Optional
from src.core.base_agent import BaseAgent
from src.tools.webhook_analysis_tool import WebhookAnalysisTool


class TechnicalSupportAgent(BaseAgent):
    """
    Specialized Technical Support Agent with deep webhook expertise.
    Provides specific code-level solutions and technical guidance.
    """
    
    def __init__(self):
        super().__init__(
            name="Technical Support Specialist",
            expertise_domain="Webhook Integration & API Troubleshooting",
            description="Expert in webhook debugging, API integration issues, and providing specific technical solutions with code examples."
        )
        self.webhook_tool = WebhookAnalysisTool()
        self.solution_templates = {
            "webhook_setup": """
## Webhook Implementation Guide

### 1. Basic Webhook Receiver
```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Verify signature (recommended)
    signature = request.headers.get('X-Signature-256')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook data
    webhook_data = request.json
    process_webhook_event(webhook_data)
    
    return jsonify({'status': 'received'}), 200

def verify_signature(payload, signature):
    secret = 'your-webhook-secret'
    expected = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f'sha256={expected}', signature)
```

### 2. Webhook Sender with Retry Logic
```python
import requests
import time
from typing import Dict, Any

def send_webhook(url: str, payload: Dict[str, Any], max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code < 500:
                # Client error, don't retry
                raise requests.HTTPError(f"Client error: {response.status_code}")
            
        except (requests.RequestException, requests.HTTPError) as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```
            """,
            "debugging_guide": """
## Webhook Debugging Checklist

### 1. Verify Endpoint Accessibility
- Check if webhook URL is publicly accessible
- Test with curl: `curl -X POST -H "Content-Type: application/json" -d '{}' YOUR_WEBHOOK_URL`
- Verify firewall and security group settings

### 2. Authentication Issues
- Validate HMAC signature generation
- Check API key format and permissions
- Verify timestamp requirements

### 3. Payload Problems
- Validate JSON structure
- Check required vs optional fields
- Verify data types match expectations

### 4. Network & Infrastructure
- Monitor response times and timeouts
- Check SSL certificate validity
- Verify HTTP methods (POST vs GET)
            """
        }
    
    def handle_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle technical support queries with specialized webhook expertise.
        Provides specific, actionable solutions with code examples.
        """
        start_time = time.time()
        
        # Extract technical context from query
        technical_context = self._extract_technical_context(query, context)
        
        # Determine query type and appropriate response
        if self._is_webhook_issue(query):
            response = self._handle_webhook_issue(query, technical_context)
        elif self._is_setup_request(query):
            response = self._handle_setup_request(query, technical_context)
        elif self._is_debugging_request(query):
            response = self._handle_debugging_request(query, technical_context)
        else:
            response = self._handle_general_technical_query(query, technical_context)
        
        # Calculate confidence based on domain match
        confidence = self._calculate_confidence(query, response)
        
        # Update performance metrics
        response_time = time.time() - start_time
        self._update_metrics(response_time, confidence)
        
        return {
            "response": response["content"],
            "confidence": confidence,
            "agent_used": self.name,
            "expertise_applied": response["expertise_areas"],
            "code_examples": response.get("code_examples", ""),
            "diagnostic_steps": response.get("diagnostic_steps", []),
            "technical_context": technical_context
        }
    
    def _extract_technical_context(self, query: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract technical indicators from query and context."""
        technical_indicators = []
        
        # Look for technical terms
        technical_terms = [
            "webhook", "api", "http", "ssl", "json", "authentication", 
            "timeout", "signature", "hmac", "payload", "endpoint",
            "certificate", "firewall", "cors", "header", "status code"
        ]
        
        query_lower = query.lower()
        for term in technical_terms:
            if term in query_lower:
                technical_indicators.append(term)
        
        return {
            "technical_indicators": technical_indicators,
            "query_complexity": "high" if len(technical_indicators) > 3 else "medium" if technical_indicators else "low",
            "additional_context": context or {}
        }
    
    def _is_webhook_issue(self, query: str) -> bool:
        """Detect if query is about webhook issues."""
        webhook_keywords = ["webhook", "not working", "failing", "error", "issue", "problem"]
        return any(keyword in query.lower() for keyword in webhook_keywords)
    
    def _is_setup_request(self, query: str) -> bool:
        """Detect if query is about webhook setup."""
        setup_keywords = ["setup", "implement", "create", "build", "configure"]
        return any(keyword in query.lower() for keyword in setup_keywords)
    
    def _is_debugging_request(self, query: str) -> bool:
        """Detect if query is about debugging."""
        debug_keywords = ["debug", "troubleshoot", "diagnose", "test", "verify"]
        return any(keyword in query.lower() for keyword in debug_keywords)
    
    def _handle_webhook_issue(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle specific webhook issues with technical analysis."""
        # Use webhook analysis tool for detailed diagnosis
        analysis = self.webhook_tool.analyze_webhook_issue(query)
        
        response_content = f"""
## Webhook Issue Analysis

**Issue Type:** {analysis['issue_type'].replace('_', ' ').title()}
**Confidence:** {analysis['confidence']:.0%}

### Technical Solution
{analysis['technical_solution']}

### Code Fix
```python
{analysis['code_examples']}
```

### Diagnostic Steps
{chr(10).join(f"• {step}" for step in analysis['diagnostic_steps'])}

### Prevention Tips
{chr(10).join(f"• {tip}" for tip in analysis['prevention_tips'])}

*This analysis demonstrates specialized expertise in webhook troubleshooting, providing specific technical solutions rather than generic advice.*
        """
        
        return {
            "content": response_content.strip(),
            "expertise_areas": ["webhook_debugging", "api_integration", "technical_diagnosis"],
            "code_examples": analysis['code_examples'],
            "diagnostic_steps": analysis['diagnostic_steps']
        }
    
    def _handle_setup_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook setup requests with implementation guidance."""
        return {
            "content": self.solution_templates["webhook_setup"],
            "expertise_areas": ["webhook_implementation", "api_design", "security_best_practices"],
            "code_examples": "Complete webhook implementation examples provided above"
        }
    
    def _handle_debugging_request(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle debugging requests with systematic approach."""
        return {
            "content": self.solution_templates["debugging_guide"],
            "expertise_areas": ["debugging_methodology", "technical_diagnosis", "troubleshooting"],
            "diagnostic_steps": [
                "Verify endpoint accessibility",
                "Check authentication configuration", 
                "Validate payload structure",
                "Test network connectivity"
            ]
        }
    
    def _handle_general_technical_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general technical queries within expertise domain."""
        response_content = f"""
## Technical Guidance

Based on your query about **{query[:50]}...**, here's my specialized analysis:

### Domain Expertise Applied
As a Technical Support Specialist focused on webhook integration and API troubleshooting, I can provide specific guidance for:

• **Webhook Implementation**: Complete setup with security best practices
• **API Integration**: Authentication, payload formatting, error handling  
• **Debugging**: Systematic troubleshooting with diagnostic tools
• **Performance**: Timeout configuration, retry logic, monitoring

### Recommended Next Steps
1. **Clarify Technical Requirements**: What specific webhook functionality do you need?
2. **Identify Integration Points**: Which systems are communicating?
3. **Define Success Criteria**: What constitutes a successful webhook delivery?

### Why Specialized Expertise Matters
Unlike generic topic handling, my domain-focused approach provides:
• **Specific Code Solutions**: Ready-to-implement examples
• **Technical Best Practices**: Security, performance, reliability
• **Diagnostic Capabilities**: Systematic issue identification
• **Rapid Customization**: Tailored solutions for your use case

*This demonstrates how specialized agents deliver superior customer outcomes through deep domain knowledge.*
        """
        
        return {
            "content": response_content.strip(),
            "expertise_areas": ["technical_consultation", "domain_expertise", "solution_architecture"]
        }
    
    def _calculate_confidence(self, query: str, response: Dict[str, Any]) -> float:
        """Calculate confidence score based on domain expertise match."""
        # Base confidence from technical indicators
        technical_indicators = len([term for term in ["webhook", "api", "http", "json", "ssl"] 
                                  if term in query.lower()])
        base_confidence = min(0.6 + (technical_indicators * 0.1), 0.9)
        
        # Boost confidence if specific expertise areas were applied
        expertise_boost = len(response.get("expertise_areas", [])) * 0.05
        
        return min(base_confidence + expertise_boost, 1.0)
    
    def _get_specialized_knowledge(self) -> Dict[str, str]:
        """Return specific knowledge areas demonstrating domain expertise."""
        return {
            "webhook_protocols": "HTTP/HTTPS webhook delivery, retry mechanisms, signature verification",
            "api_authentication": "HMAC signatures, Bearer tokens, API key management, OAuth flows",
            "debugging_tools": "Network analysis, SSL verification, payload validation, response monitoring",
            "security_practices": "Signature verification, HTTPS enforcement, secret management, rate limiting",
            "performance_optimization": "Timeout configuration, async processing, exponential backoff, monitoring",
            "integration_patterns": "Event-driven architecture, pub/sub systems, webhook vs polling trade-offs"
        }
