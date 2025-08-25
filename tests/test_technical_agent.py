#!/usr/bin/env python3
"""
Test script for the enhanced Technical Support Agent
Demonstrates webhook expertise and competitive intelligence
"""

import sys
import os
sys.path.append('.')

from src.core.agent_router import agent_router
from src.agents.technical_support_agent import get_technical_demo_scenarios

def test_webhook_expertise():
    """Test webhook troubleshooting capabilities"""
    print("🔧 Testing Webhook Expertise...")
    print("=" * 50)
    
    # Test webhook signature failure scenario
    webhook_query = "Our webhook integration stopped working after your API update. Getting 403 Forbidden errors on all POST requests. The signature verification is failing but we haven't changed our code."
    
    result = agent_router.route_query(webhook_query)
    
    print(f"Query: {webhook_query[:80]}...")
    print(f"Agent: {result['routing_info']['selected_agent']}")
    print(f"Response Time: {result['agent_response']['agent_info']['response_time']}")
    print("\nTechnical Analysis:")
    
    if 'issue_analysis' in result['agent_response']['technical_response']:
        analysis = result['agent_response']['technical_response']['issue_analysis']
        print(f"- Diagnosis: {analysis['diagnosis']}")
        print(f"- Root Cause: {analysis['root_cause']}")
        print(f"- Implementation Time: {analysis['implementation_time']}")
        print(f"- Code Solution Available: {'Yes' if analysis['fix_code'] else 'No'}")
    
    print(f"\nCompetitive Advantage: {result['agent_response']['competitive_advantage']['vs_agentforce']}")
    print()

def test_competitive_intelligence():
    """Test competitive analysis capabilities"""
    print("📊 Testing Competitive Intelligence...")
    print("=" * 50)
    
    # Test AgentForce comparison
    competitive_query = "How does your webhook handling compare to Salesforce AgentForce?"
    
    result = agent_router.route_query(competitive_query)
    
    print(f"Query: {competitive_query}")
    print(f"Agent: {result['routing_info']['selected_agent']}")
    
    if 'competitor_limitations' in result['agent_response']['technical_response']:
        analysis = result['agent_response']['technical_response']
        print("\nCompetitor Limitations:")
        for limitation in analysis['competitor_limitations']:
            print(f"- {limitation}")
        
        print(f"\nCost Comparison:")
        cost = analysis['cost_comparison']
        print(f"- AgentForce True Cost: {cost['competitor_true_cost']}")
        print(f"- Our Solution Cost: {cost['our_solution_cost']}")
        print(f"- Annual Savings: {cost['savings']}")
        
        print(f"\nAgentForce Response Simulation: '{analysis['agentforce_response_simulation']}'")
        print(f"Our Capability: {analysis['our_capability']}")
    
    print()

def test_demo_scenarios():
    """Test all demo scenarios"""
    print("🎯 Testing Demo Scenarios...")
    print("=" * 50)
    
    scenarios = get_technical_demo_scenarios()
    
    for scenario_name, scenario_query in scenarios.items():
        print(f"\nScenario: {scenario_name.replace('_', ' ').title()}")
        print(f"Query: {scenario_query[:100]}...")
        
        result = agent_router.route_query(scenario_query)
        
        print(f"Selected Agent: {result['routing_info']['selected_agent']}")
        print(f"Routing Confidence: {result['routing_info']['confidence']:.2f}")
        print(f"Response Time: {result['agent_response']['agent_info']['response_time']}")
        
        # Show key response elements
        if 'technical_response' in result['agent_response']:
            response = result['agent_response']['technical_response']
            if isinstance(response, dict):
                if 'issue_analysis' in response:
                    print(f"Technical Solution: {response['issue_analysis']['solution'][:80]}...")
                elif 'competitor_limitations' in response:
                    print(f"Competitive Analysis: Available (vs blocked in AgentForce)")
                elif 'response' in response:
                    print(f"General Response: {response['response'][:80]}...")
        
        print("-" * 30)

def main():
    """Run all tests"""
    print("🚀 AgentCraft Technical Support Agent - Test Suite")
    print("=" * 60)
    print("Demonstrating specialized webhook expertise vs AgentForce generic responses")
    print()
    
    try:
        test_webhook_expertise()
        test_competitive_intelligence()
        test_demo_scenarios()
        
        print("✅ All tests completed successfully!")
        print("\nKey Demonstrations:")
        print("- Specific webhook code solutions vs generic responses")
        print("- Real-time competitive intelligence vs platform guardrails")
        print("- Sub-30-second technical resolutions vs escalation delays")
        print("- Specialized expertise vs generic 'Technical Issues Topic #3'")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()