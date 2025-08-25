#!/usr/bin/env python3
"""
Test Galileo with proper trace context management
"""
import os

# Set environment variables
os.environ['GALILEO_API_KEY'] = 'aK_Ez6s58fD5U-FNqY7cfgvi8AiDTne10HMqnzUMszI'
os.environ['GALILEO_PROJECT'] = 'AgentCraft'  
os.environ['GALILEO_LOG_STREAM'] = 'production'
os.environ['GALILEO_CONSOLE_URL'] = 'https://app.galileo.ai'

try:
    import galileo
    from galileo import GalileoLogger
    print("✓ Galileo imported")
    
    # Create logger
    logger = GalileoLogger()
    print("✓ Logger created")
    
    # Start trace first
    print("--- Starting trace ---")
    trace_id = logger.start_trace(name="proper_test_trace")
    print(f"Trace started: {trace_id}")
    
    # Now add LLM span within the trace context
    print("--- Adding LLM span ---")
    span_result = logger.add_llm_span(
        input="Hello, what is 2+2?",
        output="2+2 equals 4",
        model="test-model"
    )
    print(f"LLM span result: {span_result}")
    
    # Check traces
    if hasattr(logger, 'traces') and logger.traces:
        print(f"✓ Traces found: {len(logger.traces)}")
        for i, trace in enumerate(logger.traces):
            print(f"Trace {i}: {trace}")
    else:
        print("❌ No traces found")
    
    # Flush to send data
    print("--- Flushing ---")
    flush_result = logger.flush()
    print(f"Flush result: {flush_result}")
    print(f"Flush length: {len(flush_result) if isinstance(flush_result, list) else 'not list'}")
    
    if flush_result:
        print("✅ Data was flushed successfully!")
        for item in flush_result:
            print(f"Flushed item: {item}")
    else:
        print("⚠️ Flush result was empty")
    
    print(f"\nCheck dashboard: https://app.galileo.ai/projects/AgentCraft")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()