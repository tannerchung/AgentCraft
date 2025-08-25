#!/usr/bin/env python3
"""
Test Galileo with proper trace creation
"""
import os

# Set environment variables
os.environ['GALILEO_API_KEY'] = 'aK_Ez6s58fD5U-FNqY7cfgvi8AiDTne10HMqnzUMszI'
os.environ['GALILEO_PROJECT'] = 'AgentCraft'
os.environ['GALILEO_LOG_STREAM'] = 'testing'
os.environ['GALILEO_CONSOLE_URL'] = 'https://app.galileo.ai'

try:
    import galileo
    from galileo import GalileoLogger
    print("✓ Galileo imported")
    
    # Create logger
    logger = GalileoLogger()
    print("✓ Logger created")
    
    # Start a trace
    print("--- Starting trace ---")
    trace_result = logger.start_trace(
        trace_id="test-trace-001",
        input_text="Test user query"
    )
    print(f"Trace result: {trace_result}")
    
    # Add an LLM span
    print("--- Adding LLM span ---")
    span_result = logger.add_llm_span(
        input="Hello world",
        output="Hi there!",
        model="gpt-3.5-turbo"
    )
    print(f"LLM span result: {span_result}")
    
    # End trace
    print("--- Ending trace ---")
    end_result = logger.end_trace(output_text="Final response")
    print(f"End trace result: {end_result}")
    
    # Check traces
    if hasattr(logger, 'traces') and logger.traces:
        print(f"✓ Traces found: {len(logger.traces)}")
    else:
        print("❌ No traces found")
    
    # Flush to send to API
    print("--- Flushing ---")
    flush_result = logger.flush()  
    print(f"Flush result: {flush_result}")
    
    print("✅ Test completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
