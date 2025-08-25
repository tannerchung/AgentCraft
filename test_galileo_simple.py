#!/usr/bin/env python3
"""
Test with the most basic Galileo logging approach
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
    
    # Use the most basic method - just add_llm_span
    print("--- Trying add_llm_span ---")
    span_result = logger.add_llm_span(
        input="Hello world",
        output="Hi there!",
        model="test"
    )
    print(f"LLM span result: {span_result}")
    
    # Check traces
    if hasattr(logger, 'traces') and logger.traces:
        print(f"✓ Traces found: {len(logger.traces)}")
        print(f"First trace content: {logger.traces[0]}")
    else:
        print("❌ No traces found")
    
    # Flush
    flush_result = logger.flush()  
    print(f"Flush: {flush_result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()