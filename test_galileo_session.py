#!/usr/bin/env python3
"""
Test Galileo session management and proper initialization
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
    
    # Initialize logger
    logger = GalileoLogger()
    print("✓ GalileoLogger initialized")
    
    # Try to start session explicitly
    print("\n--- Starting session ---")
    session_result = logger.start_session()
    print(f"Session start result: {session_result}")
    print(f"Logger session active: {hasattr(logger, '_session') and logger._session is not None}")
    
    if hasattr(logger, '_session') and logger._session:
        session = logger._session
        print(f"Session object: {session}")
        if hasattr(session, 'project_id'):
            print(f"Project ID: {session.project_id}")
        if hasattr(session, 'log_stream_id'): 
            print(f"Log stream ID: {session.log_stream_id}")
    
    # Now try logging after session is started
    print(f"\n--- Logging trace after session start ---")
    prompt = "Session test: What is 5 + 5?"
    response = "5 + 5 equals 10."
    
    result = logger.add_single_llm_span_trace(
        input=prompt,
        output=response,
        model="session-test-model",
        name="session_trace_test"
    )
    
    print(f"Trace result: {result}")
    print(f"Logger traces count: {len(logger.traces) if hasattr(logger, 'traces') else 'No traces attr'}")
    
    # Flush
    print(f"\n--- Flushing data ---")
    flush_result = logger.flush()
    print(f"Flush result: {flush_result}")
    
    print(f"\n✓ Session test completed!")
    
except Exception as e:
    print(f"❌ Error during session test: {e}")
    import traceback
    traceback.print_exc()