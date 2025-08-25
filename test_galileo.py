#!/usr/bin/env python3
"""
Simple Galileo logging test
"""
import os
import time
from datetime import datetime

# Set environment variables
os.environ['GALILEO_API_KEY'] = 'aK_Ez6s58fD5U-FNqY7cfgvi8AiDTne10HMqnzUMszI'
os.environ['GALILEO_PROJECT'] = 'AgentCraft'
os.environ['GALILEO_CONSOLE_URL'] = 'https://app.galileo.ai'

try:
    import galileo
    from galileo import GalileoLogger
    print("✓ Galileo imported successfully")
    
    # Initialize logger
    logger = GalileoLogger()
    print("✓ GalileoLogger initialized")
    
    # Simple prompt/response logging
    prompt = "What is 2+2?"
    response = "2+2 equals 4"
    
    # Log multiple traces to test
    for i in range(3):
        logger.add_single_llm_span_trace(
            input=f"{prompt} (test #{i+1})",
            output=f"{response} (response #{i+1})",
            model="test-model",
            name=f"test_trace_{i+1}"
        )
        print(f"✓ Test trace #{i+1} added")
    
    # Flush to ensure data is sent immediately
    logger.flush()
    print("✓ Data flushed to Galileo")
    
    print(f"\nTest completed! Check your Galileo dashboard at:")
    print(f"https://app.galileo.ai/projects/AgentCraft")
    
except ImportError as e:
    print(f"❌ Error importing Galileo: {e}")
except Exception as e:
    print(f"❌ Error during test: {e}")
    import traceback
    traceback.print_exc()