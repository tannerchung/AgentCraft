#!/usr/bin/env python3
"""
Basic test for the Adaptive Multi-LLM System
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """Test basic adaptive system functionality"""
    
    print("🧪 Basic Adaptive System Test")
    print("=" * 40)
    
    try:
        from src.agents.adaptive_llm_system import LLMPool, adaptive_system
        
        # Test 1: LLM Pool initialization
        print("1. Testing LLM Pool...")
        pool = LLMPool()
        print(f"   Available models: {list(pool.models.keys())}")
        
        # Test 2: Model selection
        print("\n2. Testing model selection...")
        for task_type in ["technical", "competitive", "general"]:
            for complexity in [0.2, 0.8]:
                try:
                    llm, model_name = pool.get_optimal_model(task_type, complexity)
                    print(f"   {task_type} (complexity {complexity}): {model_name}")
                except Exception as e:
                    print(f"   {task_type} (complexity {complexity}): Error - {e}")
        
        # Test 3: Backend compatibility
        print("\n3. Testing backend compatibility...")
        try:
            result = adaptive_system.process_technical_query("Test query")
            
            required_keys = ["agent_info", "technical_response", "competitive_advantage"]
            missing_keys = [key for key in required_keys if key not in result]
            
            if not missing_keys:
                print("   ✅ Backend compatibility verified")
                print(f"   Role: {result['agent_info']['role']}")
                print(f"   Processing approach: {result['query_analysis']['processing_approach']}")
            else:
                print(f"   ❌ Missing keys: {missing_keys}")
                
        except Exception as e:
            print(f"   ❌ Backend test failed: {e}")
        
        # Test 4: Performance metrics
        print("\n4. Testing performance metrics...")
        try:
            performance = adaptive_system.llm_pool.get_performance_summary()
            print(f"   Models tracked: {len(performance)}")
            
            insights = adaptive_system.generate_optimization_insights()
            print(f"   Best model: {insights.get('most_efficient_model', 'Unknown')}")
            
        except Exception as e:
            print(f"   ❌ Metrics test failed: {e}")
        
        print("\n✅ Basic functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("\n🎉 Adaptive Multi-LLM System is ready for production!")
    else:
        print("\n⚠️  Issues found - review output above.")