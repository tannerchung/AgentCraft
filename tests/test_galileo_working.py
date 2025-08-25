#!/usr/bin/env python3
"""
Test Galileo with correct API
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
    
    # Start a trace using correct method
    print("--- Starting trace ---")
    trace_result = logger.start_trace(
        input_text="Test user query"
    )
    print(f"Trace result: {trace_result}")
    
    # Add a single LLM span with trace (simpler approach)
    print("--- Adding single LLM span trace ---")
    span_result = logger.add_single_llm_span_trace(
        input="Hello from AgentCraft test",
        output="Hello! This is a test response from the system.",
        model="gpt-3.5-turbo",
        metadata={"test": True, "component": "galileo_test"}
    )
    print(f"Single LLM span result: {span_result}")
    
    # Check if we have traces
    print(f"Has active trace: {logger.has_active_trace()}")
    print(f"Number of traces: {len(logger.traces) if hasattr(logger, 'traces') and logger.traces else 0}")
    
    # Flush to send to API
    print("--- Flushing ---")
    flush_result = logger.flush()  
    print(f"Flush result: {flush_result}")
    
    print("✅ Test completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
