#!/usr/bin/env python3
"""
Working Galileo test with proper trace initialization
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
    
    # Start trace with required input parameter
    print("--- Starting trace ---")
    trace_input = "Testing Galileo logging integration"
    trace_id = logger.start_trace(input=trace_input, name="working_test_trace")
    print(f"Trace started: {trace_id}")
    
    # Add LLM span
    print("--- Adding LLM span ---")
    span_result = logger.add_llm_span(
        input="What is the meaning of life?",
        output="The meaning of life is a philosophical question that has been debated for centuries.",
        model="working-test-model"
    )
    print(f"LLM span result: {span_result}")
    
    # Check traces
    if hasattr(logger, 'traces') and logger.traces:
        print(f"✓ Traces found: {len(logger.traces)}")
        print(f"Trace details: {logger.traces[0]}")
    else:
        print("❌ No traces found")
    
    # Flush
    print("--- Flushing ---")
    flush_result = logger.flush()
    print(f"Flush result: {flush_result}")
    
    if flush_result and len(flush_result) > 0:
        print("🎉 SUCCESS! Data was sent to Galileo!")
        print(f"Sent {len(flush_result)} items")
    else:
        print("❌ No data was sent")
    
    print(f"\nIf successful, check: https://app.galileo.ai/projects/AgentCraft")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()