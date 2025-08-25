#!/usr/bin/env python3
"""
Debug Galileo logging with detailed payload inspection
"""
import os
import json
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
    
    # Initialize logger with debug info
    logger = GalileoLogger()
    print("✓ GalileoLogger initialized")
    
    # Check logger state
    print(f"Logger session active: {hasattr(logger, '_session') and logger._session is not None}")
    print(f"Logger project: {getattr(logger, 'project_name', 'Unknown')}")
    
    # Simple prompt/response logging with return value capture
    prompt = "Debug test: What is the capital of France?"
    response = "The capital of France is Paris."
    
    print(f"\n--- Logging trace ---")
    result = logger.add_single_llm_span_trace(
        input=prompt,
        output=response,
        model="debug-test-model",
        name="debug_trace_test"
    )
    
    print(f"Trace result: {result}")
    print(f"Result type: {type(result)}")
    
    # Check if logger has any internal state about traces
    if hasattr(logger, 'traces'):
        print(f"Logger traces count: {len(logger.traces)}")
    if hasattr(logger, '_traces'):
        print(f"Logger _traces count: {len(logger._traces)}")
    if hasattr(logger, '_batch'):
        print(f"Logger batch size: {len(logger._batch) if logger._batch else 0}")
    
    # Manual flush with return value
    print(f"\n--- Flushing data ---")
    flush_result = logger.flush()
    print(f"Flush result: {flush_result}")
    print(f"Flush result type: {type(flush_result)}")
    
    # Wait a moment for network
    time.sleep(2)
    
    # Try to get session info
    if hasattr(logger, '_session'):
        session = logger._session
        print(f"Session info: {session}")
        if hasattr(session, 'project_id'):
            print(f"Project ID: {session.project_id}")
        if hasattr(session, 'log_stream_id'):
            print(f"Log stream ID: {session.log_stream_id}")
    
    print(f"\n✓ Debug test completed!")
    print(f"Check dashboard: https://app.galileo.ai/projects/AgentCraft")
    
except Exception as e:
    print(f"❌ Error during debug test: {e}")
    import traceback
    traceback.print_exc()