#!/usr/bin/env python3
"""
Test script to verify all API endpoints are working
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(method, path, data=None, expected_status=[200]):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data or {})
        elif method == "PUT":
            response = requests.put(url, json=data or {})
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            return f"❓ Unknown method: {method}"
        
        if response.status_code in expected_status:
            return f"✅ {response.status_code}"
        else:
            return f"❌ {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "🔌 Server not running"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    print("Testing AgentCraft API Endpoints")
    print("=" * 50)
    print()
    
    # Test basic connectivity
    print("Basic Connectivity:")
    print(f"  GET /                           : {test_endpoint('GET', '/')}")
    print()
    
    # Agent Management Endpoints
    print("Agent Management (/api/agents):")
    print(f"  GET  /api/agents/list           : {test_endpoint('GET', '/api/agents/list')}")
    print(f"  GET  /api/agents/status         : {test_endpoint('GET', '/api/agents/status')}")
    print(f"  GET  /api/agents/metrics        : {test_endpoint('GET', '/api/agents/metrics')}")
    print(f"  POST /api/agents/cache/refresh  : {test_endpoint('POST', '/api/agents/cache/refresh')}")
    print()
    
    # Efficiency API Endpoints
    print("Efficiency API (/api/efficiency):")
    print(f"  GET  /api/efficiency/templates  : {test_endpoint('GET', '/api/efficiency/templates')}")
    print(f"  GET  /api/efficiency/agent-presets : {test_endpoint('GET', '/api/efficiency/agent-presets')}")
    print(f"  GET  /api/efficiency/health-check : {test_endpoint('GET', '/api/efficiency/health-check')}")
    print(f"  GET  /api/efficiency/usage-statistics : {test_endpoint('GET', '/api/efficiency/usage-statistics')}")
    print()
    
    # Knowledge API Endpoints
    print("Knowledge API (/api/knowledge):")
    print(f"  GET  /api/knowledge/knowledge-base/status : {test_endpoint('GET', '/api/knowledge/knowledge-base/status')}")
    print(f"  GET  /api/knowledge/companies   : {test_endpoint('GET', '/api/knowledge/companies')}")
    print(f"  GET  /api/knowledge/crawl/company-urls : {test_endpoint('GET', '/api/knowledge/crawl/company-urls')}")
    print(f"  GET  /api/knowledge/health      : {test_endpoint('GET', '/api/knowledge/health')}")
    print()
    
    # WebSocket Management Endpoints
    print("WebSocket Management (/api/ws):")
    print(f"  GET  /api/ws/stats              : {test_endpoint('GET', '/api/ws/stats')}")
    print(f"  GET  /api/test/websocket-status : {test_endpoint('GET', '/api/test/websocket-status')}")
    print()
    
    # Main Chat Endpoint
    print("Main Chat Endpoint:")
    print(f"  POST /api/chat                  : {test_endpoint('POST', '/api/chat', {'agent_type': 'test', 'message': 'test'})}")
    print()

if __name__ == "__main__":
    main()