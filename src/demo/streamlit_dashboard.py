
"""
AgentCraft Demo Dashboard - Streamlit interface showcasing specialized agent capabilities.
Demonstrates architectural flexibility and rapid customization advantages.
"""

import streamlit as st
import json
import time
from typing import Dict, Any
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.agent_router import AgentRouter
from src.agents.technical_support_agent import TechnicalSupportAgent

# Page configuration
st.set_page_config(
    page_title="AgentCraft - Specialized AI Agent Architecture",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB 0%, #A23B72 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    
    .expertise-badge {
        background-color: #2E86AB;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.25rem;
        display: inline-block;
    }
    
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def initialize_agent_system():
    """Initialize the AgentCraft system with specialized agents."""
    if 'agent_router' not in st.session_state:
        router = AgentRouter()
        
        # Register Technical Support Agent
        tech_agent = TechnicalSupportAgent()
        router.register_agent(
            tech_agent, 
            ["webhook", "api", "integration", "ssl", "authentication", "timeout", "json", "http", "debug", "troubleshoot"]
        )
        
        st.session_state.agent_router = router
        st.session_state.query_history = []

def display_header():
    """Display main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>🛠️ AgentCraft</h1>
        <h3>Specialized AI Agent Architecture</h3>
        <p>Demonstrating domain expertise advantages over generic topic handling</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display sidebar with agent information and system status."""
    with st.sidebar:
        st.header("🤖 Agent System Status")
        
        agent_status = st.session_state.agent_router.get_agent_status()
        
        st.metric("Active Agents", agent_status["total_agents"])
        
        st.subheader("Available Specialists")
        for agent_name, capabilities in agent_status["agents"].items():
            with st.expander(f"📋 {agent_name}"):
                st.write(f"**Domain:** {capabilities['expertise_domain']}")
                st.write(f"**Description:** {capabilities['description']}")
                
                # Performance metrics
                metrics = capabilities['performance_metrics']
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Queries Handled", metrics['queries_handled'])
                with col2:
                    st.metric("Avg Confidence", f"{metrics['expertise_confidence']:.1%}")
                
                # Specialized knowledge areas
                st.write("**Expertise Areas:**")
                knowledge = capabilities['specialized_knowledge']
                for area, description in knowledge.items():
                    st.markdown(f"""
                    <div class="expertise-badge">{area.replace('_', ' ').title()}</div>
                    """, unsafe_allow_html=True)
                    st.caption(description)

def display_demo_scenarios():
    """Display pre-built demo scenarios."""
    st.subheader("🎯 Demo Scenarios")
    st.write("Try these scenarios to see specialized expertise in action:")
    
    scenarios = {
        "Webhook SSL Issue": "My webhook is failing with SSL certificate verification errors. How can I fix this?",
        "Authentication Problem": "I'm getting 401 errors when sending webhooks. The HMAC signature might be wrong.",
        "Timeout Configuration": "My webhook endpoint is timing out. What's the best way to configure timeouts and retries?",
        "Webhook Setup": "I need to implement a webhook receiver for user registration events. Can you help me set it up?",
        "Debugging Guide": "My webhook integration isn't working reliably. How should I debug this systematically?"
    }
    
    col1, col2, col3 = st.columns(3)
    
    for i, (scenario_name, query) in enumerate(scenarios.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(f"🔬 {scenario_name}", key=f"scenario_{i}"):
                st.session_state.demo_query = query
                st.rerun()

def process_query(query: str) -> Dict[str, Any]:
    """Process query through the agent router."""
    with st.spinner("🧠 Routing to specialized agent..."):
        # Simulate some processing time for demo effect
        time.sleep(1)
        
        # Extract technical context for better routing
        context = {
            "technical_indicators": [word for word in query.lower().split() 
                                   if word in ["webhook", "api", "ssl", "timeout", "json", "authentication"]]
        }
        
        response = st.session_state.agent_router.route_query(query, context)
        
        # Add to query history
        st.session_state.query_history.append({
            "query": query,
            "response": response,
            "timestamp": time.time()
        })
        
        return response

def display_response(response: Dict[str, Any]):
    """Display agent response with formatting."""
    # Confidence indicator
    confidence = response.get('confidence', 0.0)
    if confidence >= 0.7:
        confidence_class = "confidence-high"
        confidence_icon = "🟢"
    elif confidence >= 0.4:
        confidence_class = "confidence-medium"
        confidence_icon = "🟡"
    else:
        confidence_class = "confidence-low"
        confidence_icon = "🔴"
    
    # Agent info header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**Agent:** {response.get('agent_used', 'Unknown')}")
    with col2:
        st.markdown(f"""
        <span class="{confidence_class}">
            {confidence_icon} {confidence:.0%} Confidence
        </span>
        """, unsafe_allow_html=True)
    with col3:
        if 'routing_info' in response:
            with st.expander("🔍 Routing Details"):
                st.json(response['routing_info'])
    
    # Main response content
    st.markdown("### 💡 Specialized Response")
    st.markdown(response.get('response', 'No response available'))
    
    # Additional technical details
    if 'code_examples' in response and response['code_examples']:
        with st.expander("💻 Code Examples"):
            st.code(response['code_examples'], language='python')
    
    if 'diagnostic_steps' in response and response['diagnostic_steps']:
        with st.expander("🔧 Diagnostic Steps"):
            for step in response['diagnostic_steps']:
                st.write(f"• {step}")
    
    if 'expertise_applied' in response:
        st.write("**Expertise Areas Applied:**")
        for area in response['expertise_applied']:
            st.markdown(f"""
            <div class="expertise-badge">{area.replace('_', ' ').title()}</div>
            """, unsafe_allow_html=True)

def display_query_history():
    """Display query history."""
    if st.session_state.query_history:
        st.subheader("📈 Query History")
        
        for i, entry in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
            with st.expander(f"Query {len(st.session_state.query_history) - i}: {entry['query'][:50]}..."):
                st.write(f"**Query:** {entry['query']}")
                st.write(f"**Agent:** {entry['response'].get('agent_used', 'Unknown')}")
                st.write(f"**Confidence:** {entry['response'].get('confidence', 0.0):.0%}")
                st.write(f"**Time:** {time.ctime(entry['timestamp'])}")

def display_competitive_advantages():
    """Display competitive advantages section."""
    st.subheader("🎯 Architectural Advantages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### AgentCraft Approach
        **✅ Specialized Expertise**
        - Domain-specific knowledge depth
        - Code-level technical solutions
        - Specific diagnostic capabilities
        
        **✅ Architectural Flexibility**
        - Custom agent development
        - Rapid domain expansion
        - Tailored solution architectures
        
        **✅ Rapid Customization**
        - New agents in hours, not months
        - Custom tool integration
        - Flexible routing logic
        """)
    
    with col2:
        st.markdown("""
        ### Generic Topic Handling
        **⚠️ Broad but Shallow**
        - Generic responses across domains
        - Template-based solutions
        - Limited technical depth
        
        **⚠️ Platform Constraints**
        - Vendor roadmap dependency
        - Limited customization options
        - Fixed architectural patterns
        
        **⚠️ Slower Adaptation**
        - Platform update cycles
        - Feature request processes
        - Implementation delays
        """)

def main():
    """Main application function."""
    # Initialize system
    initialize_agent_system()
    
    # Display header
    display_header()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Query interface
        st.subheader("💬 Interact with Specialized Agents")
        
        # Check for demo query
        default_query = st.session_state.get('demo_query', '')
        if default_query:
            st.session_state.demo_query = ''  # Clear it
        
        query = st.text_area(
            "Enter your technical query:",
            value=default_query,
            height=100,
            placeholder="e.g., My webhook is returning 401 authentication errors..."
        )
        
        col_query1, col_query2 = st.columns([1, 4])
        with col_query1:
            if st.button("🚀 Submit Query", disabled=not query.strip()):
                response = process_query(query)
                display_response(response)
        
        with col_query2:
            if st.button("🧹 Clear History"):
                st.session_state.query_history = []
                st.rerun()
        
        # Demo scenarios
        display_demo_scenarios()
        
        # Query history
        display_query_history()
    
    with col2:
        # Competitive advantages
        display_competitive_advantages()
        
        # System information
        st.subheader("ℹ️ System Information")
        st.info("""
        **AgentCraft** demonstrates how specialized AI agents can deliver 
        superior customer outcomes through:
        
        • **Domain Expertise**: Deep technical knowledge
        • **Specific Solutions**: Code examples and diagnostics  
        • **Flexible Architecture**: Custom agent development
        • **Rapid Innovation**: Quick domain expansion
        
        This complements platform approaches by providing 
        specialized capabilities for complex technical domains.
        """)

if __name__ == "__main__":
    main()
