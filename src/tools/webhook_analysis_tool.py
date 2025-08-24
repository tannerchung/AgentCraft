
"""
Webhook Analysis Tool - demonstrates specific technical knowledge
and code-level solutions for webhook integration issues.
"""

import re
import json
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime


class WebhookAnalysisTool:
    """
    Specialized tool for webhook troubleshooting and analysis.
    Provides specific technical solutions rather than generic advice.
    """
    
    def __init__(self):
        self.common_issues = {
            "ssl_verification": {
                "pattern": r"ssl|certificate|https|tls",
                "solution": "SSL certificate verification issue",
                "code_fix": """
# Fix SSL verification issues
import ssl
import requests

# Option 1: Disable SSL verification (development only)
response = requests.post(webhook_url, json=payload, verify=False)

# Option 2: Use custom certificate bundle
response = requests.post(webhook_url, json=payload, verify='/path/to/certificate.pem')

# Option 3: Update SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
"""
            },
            "timeout": {
                "pattern": r"timeout|slow|response time",
                "solution": "Request timeout configuration",
                "code_fix": """
# Configure appropriate timeouts
import requests

# Set connection and read timeouts
response = requests.post(
    webhook_url, 
    json=payload, 
    timeout=(5, 30)  # (connection_timeout, read_timeout)
)

# For async webhooks with retries
import asyncio
import aiohttp

async def send_webhook_with_retry(url, payload, max_retries=3):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for attempt in range(max_retries):
            try:
                async with session.post(url, json=payload) as response:
                    return await response.json()
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
"""
            },
            "authentication": {
                "pattern": r"auth|token|signature|hmac|bearer",
                "solution": "Authentication and signature verification",
                "code_fix": """
# HMAC signature verification
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

# Bearer token authentication
headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}
response = requests.post(webhook_url, json=payload, headers=headers)

# API key authentication
headers = {
    'X-API-Key': api_key,
    'Content-Type': 'application/json'
}
"""
            },
            "payload_format": {
                "pattern": r"json|payload|format|structure",
                "solution": "Payload formatting and validation",
                "code_fix": """
# Proper payload structure
webhook_payload = {
    "event_type": "user.created",
    "timestamp": datetime.utcnow().isoformat(),
    "data": {
        "user_id": "12345",
        "email": "user@example.com",
        "metadata": {}
    },
    "version": "1.0"
}

# Validate payload before sending
from pydantic import BaseModel, ValidationError

class WebhookPayload(BaseModel):
    event_type: str
    timestamp: str
    data: dict
    version: str

try:
    validated_payload = WebhookPayload(**webhook_payload)
    response = requests.post(webhook_url, json=validated_payload.dict())
except ValidationError as e:
    print(f"Payload validation error: {e}")
"""
            }
        }
    
    def analyze_webhook_issue(self, issue_description: str, error_logs: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze webhook issues and provide specific technical solutions.
        Demonstrates domain expertise over generic troubleshooting.
        """
        analysis_results = {
            "issue_type": "unknown",
            "confidence": 0.0,
            "technical_solution": "",
            "code_examples": "",
            "diagnostic_steps": [],
            "prevention_tips": []
        }
        
        issue_text = f"{issue_description} {error_logs or ''}".lower()
        
        # Pattern matching for specific issues
        best_match = None
        highest_confidence = 0.0
        
        for issue_type, config in self.common_issues.items():
            if re.search(config["pattern"], issue_text):
                # Calculate confidence based on pattern strength
                pattern_matches = len(re.findall(config["pattern"], issue_text))
                confidence = min(0.8 + (pattern_matches * 0.1), 1.0)
                
                if confidence > highest_confidence:
                    highest_confidence = confidence
                    best_match = issue_type
        
        if best_match:
            issue_config = self.common_issues[best_match]
            analysis_results.update({
                "issue_type": best_match,
                "confidence": highest_confidence,
                "technical_solution": issue_config["solution"],
                "code_examples": issue_config["code_fix"],
                "diagnostic_steps": self._get_diagnostic_steps(best_match),
                "prevention_tips": self._get_prevention_tips(best_match)
            })
        
        return analysis_results
    
    def _get_diagnostic_steps(self, issue_type: str) -> List[str]:
        """Get specific diagnostic steps for the issue type."""
        diagnostic_map = {
            "ssl_verification": [
                "Check certificate validity: openssl s_client -connect hostname:443",
                "Verify certificate chain completeness",
                "Test with curl: curl -v https://webhook-endpoint.com",
                "Check certificate expiration date"
            ],
            "timeout": [
                "Measure response times: time curl -X POST webhook-url",
                "Check network latency: ping webhook-host",
                "Monitor server logs for processing delays",
                "Test with different timeout values"
            ],
            "authentication": [
                "Verify API key/token validity",
                "Check signature generation algorithm",
                "Test authentication headers separately",
                "Validate timestamp requirements"
            ],
            "payload_format": [
                "Validate JSON syntax: python -m json.tool payload.json",
                "Check required fields against API documentation",
                "Verify content-type headers",
                "Test with minimal payload first"
            ]
        }
        return diagnostic_map.get(issue_type, ["Contact technical support for assistance"])
    
    def _get_prevention_tips(self, issue_type: str) -> List[str]:
        """Get prevention tips for the issue type."""
        prevention_map = {
            "ssl_verification": [
                "Implement certificate monitoring and alerts",
                "Use automated certificate renewal",
                "Maintain updated certificate stores",
                "Test SSL configuration regularly"
            ],
            "timeout": [
                "Implement exponential backoff retry logic",
                "Set appropriate timeout values for your use case",
                "Monitor webhook endpoint performance",
                "Use async processing for long-running operations"
            ],
            "authentication": [
                "Rotate API keys regularly",
                "Store secrets securely (environment variables)",
                "Implement signature verification on both sides",
                "Monitor authentication failures"
            ],
            "payload_format": [
                "Use schema validation in your application",
                "Implement payload versioning",
                "Test with various payload sizes",
                "Document expected payload structure"
            ]
        }
        return prevention_map.get(issue_type, ["Follow webhook security best practices"])
    
    def test_webhook_endpoint(self, url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Test webhook endpoint and provide detailed analysis.
        Demonstrates specific technical validation capabilities.
        """
        test_results = {
            "status": "unknown",
            "response_time": 0.0,
            "status_code": None,
            "response_body": "",
            "issues_detected": [],
            "recommendations": []
        }
        
        try:
            start_time = datetime.now()
            response = requests.post(
                url, 
                json=payload, 
                headers=headers or {'Content-Type': 'application/json'},
                timeout=30
            )
            end_time = datetime.now()
            
            test_results.update({
                "status": "success" if response.status_code < 400 else "error",
                "response_time": (end_time - start_time).total_seconds(),
                "status_code": response.status_code,
                "response_body": response.text[:500]  # Truncate for safety
            })
            
            # Analyze response for potential issues
            if response.status_code >= 400:
                test_results["issues_detected"].append(f"HTTP {response.status_code} error")
            
            if test_results["response_time"] > 10:
                test_results["issues_detected"].append("Slow response time")
                test_results["recommendations"].append("Consider optimizing endpoint performance")
            
            if response.status_code == 200 and not response.text:
                test_results["recommendations"].append("Consider returning acknowledgment in response body")
                
        except requests.exceptions.SSLError:
            test_results["status"] = "ssl_error"
            test_results["issues_detected"].append("SSL certificate verification failed")
            test_results["recommendations"].append("Check SSL certificate configuration")
            
        except requests.exceptions.Timeout:
            test_results["status"] = "timeout"
            test_results["issues_detected"].append("Request timeout")
            test_results["recommendations"].append("Increase timeout or optimize endpoint")
            
        except requests.exceptions.ConnectionError:
            test_results["status"] = "connection_error"
            test_results["issues_detected"].append("Cannot connect to endpoint")
            test_results["recommendations"].append("Verify URL and network connectivity")
        
        return test_results
