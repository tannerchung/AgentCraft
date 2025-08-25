#!/usr/bin/env python3
"""
Test Galileo with correct API parameters
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
    
    # Test 1: Simple single LLM span trace (complete conversation)
    print("--- Test 1: Single LLM span trace ---")
    trace_result = logger.add_single_llm_span_trace(
        input="What is the competitive advantage of AgentCraft?",
        output="AgentCraft provides real-time multi-agent collaboration with visual tracking and adaptive LLM selection for optimal performance.",
        model="gpt-3.5-turbo",
        metadata={"test": "true", "component": "galileo_test"}
    )
    print(f"Single trace result: {trace_result}")
    
    # Test 2: Manual trace with spans
    print("--- Test 2: Manual trace construction ---")
    trace_start = logger.start_trace(
        input="How does the real-time tracking work?",
        name="realtime_tracking_query",
        metadata={"query_type": "technical"}
    )
    print(f"Start trace result: {trace_start}")
    
    # Add LLM span to active trace
    if logger.has_active_trace():
        llm_span = logger.add_llm_span(
            input="Analyze real-time tracking architecture",
            output="The system uses WebSocket connections with AgentActivity data structures to broadcast agent status updates.",
            model="gpt-4"
        )
        print(f"LLM span result: {llm_span}")
    
    # Check status
    print(f"Has active trace: {logger.has_active_trace()}")
    print(f"Number of traces: {len(logger.traces) if hasattr(logger, 'traces') and logger.traces else 0}")
    
    # Flush to send to Galileo
    print("--- Flushing to Galileo ---")
    flush_result = logger.flush()
    print(f"Flush result: {flush_result}")
    
    # Check after flush
    print(f"Traces after flush: {len(logger.traces) if hasattr(logger, 'traces') and logger.traces else 0}")
    
    print("✅ Galileo test completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
