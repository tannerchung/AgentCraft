#!/usr/bin/env python3
"""
Test API endpoints for the enhanced Technical Support Agent
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_endpoint():
    """Test the main chat endpoint"""
    print("🔧 Testing Chat Endpoint...")
    
    payload = {
        "agent_type": "technical",
        "message": "Our webhook integration is failing with 403 errors after your API update",
        "context": {}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working")
            print(f"Success: {data.get('success')}")
            if data.get('success'):
                print(f"Agent: {data['agent_info']['role']}")
                print(f"Response Time: {data['agent_info']['response_time']}")
                print(f"Competitive Advantage: {data['competitive_advantage']['vs_agentforce']}")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def test_demo_scenarios_endpoint():
    """Test the demo scenarios endpoint"""
    print("\n🎯 Testing Demo Scenarios Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/demo-scenarios", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Demo scenarios endpoint working")
            scenarios = data.get('technical_scenarios', {})
            print(f"Available scenarios: {len(scenarios)}")
            for scenario_name in list(scenarios.keys())[:3]:
                print(f"- {scenario_name.replace('_', ' ').title()}")
            return True
        else:
            print(f"❌ Demo scenarios endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Demo scenarios endpoint error: {e}")
        return False

def test_competitive_analysis_endpoint():
    """Test the competitive analysis endpoint"""
    print("\n📊 Testing Competitive Analysis Endpoint...")
    
    payload = {
        "competitor": "AgentForce",
        "focus_areas": ["webhook_handling", "technical_support"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/competitive-analysis", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Competitive analysis endpoint working")
            
            if 'our_capability' in data:
                capability = data['our_capability']
                print(f"Competitor: {capability.get('competitor')}")
                print(f"Cost Savings: {capability.get('cost_comparison', {}).get('savings', 'N/A')}")
                
            if 'agentforce_simulation' in data:
                simulation = data['agentforce_simulation']
                print(f"AgentForce Limitation: {simulation.get('limitation')}")
                
            return True
        else:
            print(f"❌ Competitive analysis endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Competitive analysis endpoint error: {e}")
        return False

def test_metrics_endpoint():
    """Test the metrics endpoint"""
    print("\n📈 Testing Metrics Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/metrics", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Metrics endpoint working")
            
            agent_perf = data.get('agent_performance', {})
            print(f"Our Response Time: {agent_perf.get('response_time')}")
            print(f"Our Resolution Rate: {agent_perf.get('resolution_rate')}")
            
            agentforce_perf = data.get('agentforce_comparison', {})
            print(f"AgentForce Response Time: {agentforce_perf.get('response_time')}")
            print(f"AgentForce Resolution Rate: {agentforce_perf.get('resolution_rate')}")
            
            cost_analysis = data.get('cost_analysis', {})
            print(f"Annual Savings: {cost_analysis.get('annual_savings')}")
            
            return True
        else:
            print(f"❌ Metrics endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Metrics endpoint error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 AgentCraft API Endpoints - Test Suite")
    print("=" * 50)
    
    print("Note: Make sure the API server is running with:")
    print("uv run python backend/main.py")
    print()
    
    # Give server time to start if just launched
    time.sleep(1)
    
    tests = [
        test_chat_endpoint,
        test_demo_scenarios_endpoint,
        test_competitive_analysis_endpoint,
        test_metrics_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} endpoints working")
    
    if passed == total:
        print("✅ All API endpoints are functional!")
        print("\nReady for frontend integration and demo presentations.")
    else:
        print("❌ Some endpoints need attention.")
        print("Check server logs for detailed error information.")

if __name__ == "__main__":
    main()