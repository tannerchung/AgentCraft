#!/usr/bin/env python3
"""
Test Galileo with proper log stream configuration
"""
import os
import json
import time
from datetime import datetime

# Set environment variables exactly as in .env
os.environ['GALILEO_API_KEY'] = 'aK_Ez6s58fD5U-FNqY7cfgvi8AiDTne10HMqnzUMszI'
os.environ['GALILEO_PROJECT'] = 'AgentCraft'
os.environ['GALILEO_LOG_STREAM'] = 'production'
os.environ['GALILEO_CONSOLE_URL'] = 'https://app.galileo.ai'

try:
    import galileo
    from galileo import GalileoLogger
    print("✓ Galileo imported successfully")
    
    # Initialize logger
    logger = GalileoLogger()
    print("✓ GalileoLogger initialized")
    
    # Check all environment variables
    print("\n--- Environment check ---")
    for key in ['GALILEO_API_KEY', 'GALILEO_PROJECT', 'GALILEO_LOG_STREAM', 'GALILEO_CONSOLE_URL']:
        value = os.environ.get(key, 'NOT SET')
        print(f"{key}: {value[:20]}..." if len(str(value)) > 20 else f"{key}: {value}")
    
    # Start session
    print("\n--- Starting session ---")
    session_result = logger.start_session()
    print(f"Session start result: {session_result}")
    
    # Wait a moment for session to initialize
    time.sleep(1)
    
    # Check session state again
    print(f"Logger session active: {hasattr(logger, '_session') and logger._session is not None}")
    
    # Log a simple trace
    print(f"\n--- Logging trace ---")
    result = logger.add_single_llm_span_trace(
        input="Stream test: What is the weather today?",
        output="I don't have access to current weather data.",
        model="stream-test-model", 
        name="stream_trace_test"
    )
    
    print(f"Trace result: {result}")
    
    # Check internal state
    if hasattr(logger, 'traces'):
        print(f"Logger traces: {len(logger.traces)}")
        if logger.traces:
            print(f"First trace: {logger.traces[0]}")
    
    # Manually flush and check result
    print(f"\n--- Flushing ---")
    flush_result = logger.flush()
    print(f"Flush result: {flush_result}")
    print(f"Flush result length: {len(flush_result) if isinstance(flush_result, list) else 'not a list'}")
    
    # Wait for network transmission
    time.sleep(3)
    print("✓ Waited for transmission")
    
    print(f"\n✓ Stream test completed!")
    print(f"Check: https://app.galileo.ai/projects/AgentCraft")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()