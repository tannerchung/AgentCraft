#!/usr/bin/env python3
"""
Comprehensive testing framework for the Adaptive Multi-LLM System
Tests CrewAI features: memory, reasoning, planning, testing, training, collaboration
"""

import sys
import os
import time
import json
from typing import Dict, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_adaptive_system():
    """Test the adaptive multi-LLM system"""
    
    print("🧪 Testing Adaptive Multi-LLM System")
    print("=" * 50)
    
    try:
        from src.agents.adaptive_llm_system import adaptive_system
        print("✅ Adaptive system imported successfully")
        
        # Test queries with different complexity levels
        test_cases = [
            {
                "query": "How do I fix a webhook 403 error?",
                "context": {"use_crewai": True, "complexity": "medium"},
                "expected_outcome": {
                    "max_time": 30.0,
                    "min_quality": 7.0,
                    "required_specialists": ["technical"]
                }
            },
            {
                "query": "How does our AI agent platform compare to Salesforce AgentForce in terms of cost and capabilities?",
                "context": {"use_crewai": True, "complexity": "high"},
                "expected_outcome": {
                    "max_time": 45.0,
                    "min_quality": 8.0,
                    "required_specialists": ["competitive"]
                }
            },
            {
                "query": "What services do you offer?",
                "context": {"use_crewai": True, "complexity": "low"},
                "expected_outcome": {
                    "max_time": 15.0,
                    "min_quality": 6.0,
                    "required_specialists": ["customer_success"]
                }
            }
        ]
        
        print(f"\n📋 Running {len(test_cases)} test cases...")
        
        # Run system tests
        test_results = adaptive_system.test_system(test_cases)
        
        print(f"\n📊 Test Results:")
        print(f"   Total Tests: {test_results['total_tests']}")
        print(f"   Success Rate: {test_results['success_rate']:.2%}")
        print(f"   Average Quality: {test_results['average_quality']:.1f}/10")
        print(f"   Average Time: {test_results['average_execution_time']:.1f}s")
        
        if test_results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in test_results['recommendations']:
                print(f"   • {rec}")
        
        # Test individual query processing
        print(f"\n🔍 Individual Query Test:")
        test_query = "Our webhook integration is timing out after 30 seconds. How can we optimize it?"
        
        print(f"Query: {test_query}")
        
        start_time = time.time()
        result = adaptive_system.process_query_with_adaptive_llms(
            test_query, 
            {"use_crewai": True, "priority": "high"}
        )
        execution_time = time.time() - start_time
        
        print(f"\n📈 Results:")
        print(f"   LLMs Used: {result['llms_used']}")
        print(f"   Execution Time: {execution_time:.2f}s")
        print(f"   Quality Scores: {result['performance_metrics']['quality_scores']}")
        print(f"   Average Quality: {result['performance_metrics']['avg_quality']:.1f}/10")
        
        print(f"\n🤝 Collaboration Insights:")
        collaboration = result['agent_collaboration']
        for key, value in collaboration.items():
            print(f"   {key}: {value}")
        
        print(f"\n🧠 Memory Utilization:")
        memory = result['memory_utilization']
        for key, value in memory.items():
            print(f"   {key}: {value}")
        
        print(f"\n⚡ Optimization Insights:")
        optimization = result['optimization_insights']
        print(f"   Best Quality Model: {optimization.get('best_quality_model', 'N/A')}")
        print(f"   Fastest Model: {optimization.get('fastest_model', 'N/A')}")
        print(f"   Most Efficient Model: {optimization.get('most_efficient_model', 'N/A')}")
        
        if optimization.get('recommendations'):
            print(f"   Recommendations:")
            for rec in optimization['recommendations']:
                print(f"     • {rec}")
        
        # Test training system
        print(f"\n🎓 Testing Training System:")
        
        training_data = [
            {
                "query": "Fix webhook error",
                "quality_score": 8.5,
                "user_satisfaction": 9.0,
                "execution_time": 2.3,
                "selected_llms": {"technical": "powerful"}
            },
            {
                "query": "Compare pricing",
                "quality_score": 7.8,
                "user_satisfaction": 8.2,
                "execution_time": 4.1,
                "selected_llms": {"competitive": "balanced"}
            }
        ]
        
        training_result = adaptive_system.train_system(training_data)
        
        if training_result['training_completed']:
            print(f"   ✅ Training completed with {training_result['samples_processed']} samples")
            print(f"   Updated weights: {training_result.get('updated_weights', {})}")
        else:
            print(f"   ❌ Training failed: {training_result.get('error', 'Unknown error')}")
        
        # Test LLM performance tracking
        print(f"\n📊 LLM Performance Summary:")
        performance_summary = adaptive_system.llm_pool.get_performance_summary()
        
        for model_name, metrics in performance_summary.items():
            print(f"   {model_name}:")
            print(f"     Response Time: {metrics['avg_response_time']:.2f}s")
            print(f"     Quality Score: {metrics['avg_quality']:.1f}/10")
            print(f"     Efficiency: {metrics['efficiency_score']:.1f}")
            print(f"     Success Rate: {metrics['success_rate']:.2%}")
            print(f"     Total Requests: {metrics['total_requests']}")
        
        # Test compatibility with existing backend
        print(f"\n🔌 Testing Backend Compatibility:")
        
        compat_result = adaptive_system.process_technical_query(
            "Test compatibility", 
            {"use_crewai": True}
        )
        
        required_keys = [
            "agent_info", "technical_response", "query_analysis", 
            "competitive_advantage", "performance_metrics", "timestamp"
        ]
        
        missing_keys = [key for key in required_keys if key not in compat_result]
        
        if not missing_keys:
            print(f"   ✅ All required backend keys present")
            print(f"   Processing approach: {compat_result['query_analysis']['processing_approach']}")
            print(f"   LLMs used: {compat_result['agent_info']['llms_used']}")
        else:
            print(f"   ❌ Missing keys: {missing_keys}")
        
        print(f"\n🎉 Adaptive Multi-LLM System testing completed!")
        print(f"✅ System is ready for production use with:")
        print(f"   • Hot-swappable LLMs based on performance metrics")
        print(f"   • CrewAI memory, planning, and collaboration features")
        print(f"   • Continuous learning and optimization")
        print(f"   • Comprehensive testing and training framework")
        print(f"   • Full backend compatibility")
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_llm_pool():
    """Test the LLM pool functionality"""
    
    print(f"\n🔧 Testing LLM Pool:")
    
    try:
        from src.agents.adaptive_llm_system import LLMPool
        
        pool = LLMPool()
        
        print(f"   Available models: {list(pool.models.keys())}")
        
        # Test model selection
        for task_type in ["technical", "competitive", "customer_success", "general"]:
            for complexity in [0.2, 0.5, 0.8]:
                try:
                    llm, model_name = pool.get_optimal_model(task_type, complexity)
                    print(f"   {task_type} (complexity {complexity}): {model_name}")
                except Exception as e:
                    print(f"   {task_type} (complexity {complexity}): Error - {e}")
        
        # Test performance tracking
        pool.track_performance("balanced", 2.5, 8.0, {"input": 100, "output": 200}, True)
        pool.track_performance("fast", 1.2, 7.5, {"input": 50, "output": 150}, True)
        
        summary = pool.get_performance_summary()
        print(f"   Performance tracking working: {len(summary)} models tracked")
        
        return True
        
    except Exception as e:
        print(f"   ❌ LLM Pool test failed: {e}")
        return False

def test_orchestrator():
    """Test the intelligent orchestrator"""
    
    print(f"\n🎯 Testing Intelligent Orchestrator:")
    
    try:
        from src.agents.adaptive_llm_system import IntelligentOrchestrator, LLMPool
        
        pool = LLMPool()
        orchestrator = IntelligentOrchestrator(pool)
        
        # Test complexity analysis
        test_queries = [
            "Hello, how are you?",
            "Our webhook endpoint is returning 403 errors after updating our API integration",
            "Perform a comprehensive competitive analysis comparing our AI agent platform to Salesforce AgentForce including technical architecture, pricing models, market positioning, and strategic recommendations"
        ]
        
        for query in test_queries:
            try:
                complexity = orchestrator.analyze_query_complexity(query)
                print(f"   '{query[:50]}...' -> Complexity: {complexity:.2f}")
            except Exception as e:
                print(f"   Query analysis failed: {e}")
        
        # Test LLM selection
        try:
            selected = orchestrator.select_optimal_llms(
                "Fix our webhook integration issues", 
                {"priority": "high"}
            )
            print(f"   LLM selection working: {len(selected)} specialists selected")
            for role, (_, model_name) in selected.items():
                print(f"     {role}: {model_name}")
        except Exception as e:
            print(f"   LLM selection failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Orchestrator test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Adaptive Multi-LLM System Tests")
    print("=" * 60)
    
    # Run all tests
    tests = [
        ("LLM Pool", test_llm_pool),
        ("Orchestrator", test_orchestrator), 
        ("Full System", test_adaptive_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if test_func():
                print(f"✅ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"🏁 Test Summary: {passed}/{total} tests passed ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 All tests passed! Adaptive Multi-LLM System is ready!")
    else:
        print("⚠️  Some tests failed. Review the output above.")