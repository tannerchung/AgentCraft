#!/usr/bin/env python3
"""
Test script for Galileo integration with CrewAI
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_galileo_integration():
    """Test Galileo integration setup"""
    
    print("🔬 Testing Galileo Integration...")
    print("=" * 50)
    
    # Check environment variables
    galileo_api_key = os.getenv('GALILEO_API_KEY')
    galileo_project = os.getenv('GALILEO_PROJECT', 'AgentCraft')
    galileo_log_stream = os.getenv('GALILEO_LOG_STREAM', 'production')
    
    print(f"✅ GALILEO_PROJECT: {galileo_project}")
    print(f"✅ GALILEO_LOG_STREAM: {galileo_log_stream}")
    
    if galileo_api_key:
        print(f"✅ GALILEO_API_KEY: {'*' * 8}{galileo_api_key[-4:]} (masked)")
    else:
        print("❌ GALILEO_API_KEY: Not set")
        print("   Please add your Galileo API key to the .env file")
        return False
    
    # Test Galileo import
    try:
        from galileo.handlers.crewai.handler import CrewAIEventListener
        print("✅ Galileo CrewAI handler imported successfully")
    except ImportError as e:
        print(f"❌ Galileo import failed: {e}")
        print("   Install with: uv add galileo")
        return False
    
    # Test python-dotenv
    try:
        import dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError:
        print("❌ python-dotenv not available")
        print("   Install with: uv add python-dotenv")
        return False
    
    # Test event listener initialization
    try:
        listener = CrewAIEventListener()
        print("✅ CrewAI Event Listener initialized successfully")
    except Exception as e:
        print(f"❌ Event listener initialization failed: {e}")
        return False
    
    print("\n🎉 Galileo integration test completed successfully!")
    print("\nNext steps:")
    print("1. Run your CrewAI agents - traces will automatically be logged")
    print("2. Check your Galileo dashboard for observability data")
    print(f"3. Project: {galileo_project}")
    print(f"4. Stream: {galileo_log_stream}")
    
    return True

if __name__ == "__main__":
    success = test_galileo_integration()
    sys.exit(0 if success else 1)