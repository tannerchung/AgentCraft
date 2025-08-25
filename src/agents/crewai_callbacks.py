"""
CrewAI Callbacks for Real-time Tracking
Hooks into CrewAI execution to provide real-time status updates
"""

import logging
import time
import re
from typing import Dict, Any, Optional
from uuid import uuid4

from src.agents.realtime_agent_tracker import realtime_tracker, AgentStatus

logger = logging.getLogger(__name__)

class CrewAIExecutionCallback:
    """Callback class to track CrewAI execution in real-time"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.agent_tasks = {}
        self.execution_start = time.time()
    
    def on_crew_start(self, crew, inputs: Dict[str, Any]):
        """Called when crew starts execution"""
        agent_names = [agent.role for agent in crew.agents]
        realtime_tracker.start_session(self.session_id, inputs.get('query', 'Unknown query'), agent_names)
        
        realtime_tracker.add_crew_output(
            self.session_id,
            "crew_start",
            f"Starting crew with {len(agent_names)} agents: {', '.join(agent_names)}"
        )
        
        realtime_tracker.update_crew_phase(self.session_id, "crew_initialization")
    
    def on_agent_start(self, agent, task):
        """Called when an agent starts working on a task"""
        agent_name = getattr(agent, 'role', str(agent))
        task_description = getattr(task, 'description', str(task))
        
        realtime_tracker.update_agent_status(
            self.session_id,
            agent_name,
            AgentStatus.ANALYZING,
            task=task_description[:100],
            progress=10.0,
            details="Starting task analysis"
        )
        
        realtime_tracker.add_crew_output(
            self.session_id,
            "agent_start",
            f"Agent '{agent_name}' starting task: {task_description[:100]}...",
            agent_name=agent_name
        )
        
        self.agent_tasks[agent_name] = {
            'task': task_description,
            'start_time': time.time()
        }
    
    def on_agent_thinking(self, agent, message: str):
        """Called when agent is processing/thinking"""
        agent_name = getattr(agent, 'role', str(agent))
        
        realtime_tracker.update_agent_status(
            self.session_id,
            agent_name,
            AgentStatus.PROCESSING,
            progress=50.0,
            details=message[:200] if message else "Processing..."
        )
        
        # Extract useful information from agent thinking
        if message and len(message) > 20:
            realtime_tracker.add_crew_output(
                self.session_id,
                "agent_thinking",
                self._clean_agent_output(message),
                agent_name=agent_name
            )
    
    def on_agent_tool_use(self, agent, tool_name: str, tool_input: Any):
        """Called when agent uses a tool"""
        agent_name = getattr(agent, 'role', str(agent))
        
        realtime_tracker.update_agent_status(
            self.session_id,
            agent_name,
            AgentStatus.PROCESSING,
            progress=70.0,
            details=f"Using tool: {tool_name}"
        )
        
        realtime_tracker.add_crew_output(
            self.session_id,
            "tool_use",
            f"Using tool '{tool_name}' with input: {str(tool_input)[:100]}...",
            agent_name=agent_name
        )
    
    def on_agent_complete(self, agent, result):
        """Called when agent completes its task"""
        agent_name = getattr(agent, 'role', str(agent))
        
        realtime_tracker.update_agent_status(
            self.session_id,
            agent_name,
            AgentStatus.FINISHED,
            progress=100.0,
            details="Task completed successfully"
        )
        
        # Extract result content
        result_content = str(result)[:500] if result else "Task completed"
        
        realtime_tracker.add_crew_output(
            self.session_id,
            "agent_complete",
            f"Agent '{agent_name}' completed task. Result: {self._clean_agent_output(result_content)}",
            agent_name=agent_name
        )
        
        # Calculate task duration
        if agent_name in self.agent_tasks:
            duration = time.time() - self.agent_tasks[agent_name]['start_time']
            realtime_tracker.add_crew_output(
                self.session_id,
                "timing",
                f"Agent '{agent_name}' task completed in {duration:.2f}s",
                agent_name=agent_name
            )
    
    def on_collaboration(self, primary_agent, secondary_agent, context: str):
        """Called when agents collaborate"""
        primary_name = getattr(primary_agent, 'role', str(primary_agent))
        secondary_name = getattr(secondary_agent, 'role', str(secondary_agent))
        
        # Update both agents to collaborating status
        for agent_name in [primary_name, secondary_name]:
            realtime_tracker.update_agent_status(
                self.session_id,
                agent_name,
                AgentStatus.COLLABORATING,
                progress=60.0,
                details=f"Collaborating with {secondary_name if agent_name == primary_name else primary_name}"
            )
        
        realtime_tracker.add_crew_output(
            self.session_id,
            "collaboration",
            f"Collaboration between '{primary_name}' and '{secondary_name}': {context[:200]}",
            agent_name=primary_name
        )
    
    def on_crew_complete(self, crew, result):
        """Called when entire crew completes execution"""
        duration = time.time() - self.execution_start
        
        realtime_tracker.update_crew_phase(self.session_id, "synthesis")
        
        # Final result
        result_content = str(result) if result else "Crew execution completed"
        
        realtime_tracker.add_crew_output(
            self.session_id,
            "final_result",
            f"Crew execution completed in {duration:.2f}s. Final result: {self._clean_agent_output(result_content[:1000])}"
        )
        
        realtime_tracker.complete_session(self.session_id, result_content)
    
    def on_error(self, error, agent=None):
        """Called when an error occurs"""
        agent_name = getattr(agent, 'role', str(agent)) if agent else None
        error_message = str(error)
        
        realtime_tracker.add_crew_output(
            self.session_id,
            "error",
            f"Error occurred: {error_message}",
            agent_name=agent_name
        )
        
        realtime_tracker.error_session(self.session_id, error_message, agent_name)
    
    def _clean_agent_output(self, text: str) -> str:
        """Clean up agent output for display"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common system prefixes
        text = re.sub(r'^(Agent|Assistant|AI):\s*', '', text, flags=re.IGNORECASE)
        
        # Remove markdown artifacts that might not render well
        text = re.sub(r'```\w*\n', '\n```\n', text)
        
        # Truncate if too long
        if len(text) > 500:
            text = text[:497] + "..."
        
        return text

class CrewAIOutputCapture:
    """Captures CrewAI console output for real-time display"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.original_stdout = None
        self.original_stderr = None
    
    def __enter__(self):
        """Start capturing output"""
        import sys
        from io import StringIO
        
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Create custom stdout that sends to both console and tracker
        class TrackedOutput:
            def __init__(self, session_id, original, output_type):
                self.session_id = session_id
                self.original = original
                self.output_type = output_type
                self.buffer = ""
            
            def write(self, text):
                # Write to original stdout/stderr
                if self.original:
                    self.original.write(text)
                
                # Buffer and send to tracker
                self.buffer += text
                
                # Send complete lines to tracker
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    if line.strip():  # Only send non-empty lines
                        realtime_tracker.add_crew_output(
                            self.session_id,
                            f"console_{self.output_type}",
                            line.strip()
                        )
            
            def flush(self):
                if self.original:
                    self.original.flush()
        
        sys.stdout = TrackedOutput(self.session_id, self.original_stdout, "stdout")
        sys.stderr = TrackedOutput(self.session_id, self.original_stderr, "stderr")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop capturing output"""
        import sys
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

def create_callback_system(session_id: str) -> CrewAIExecutionCallback:
    """Factory function to create callback system for a session"""
    return CrewAIExecutionCallback(session_id)

# Helper function to patch CrewAI for real-time tracking
def patch_crewai_for_tracking():
    """Monkey patch CrewAI classes to add tracking callbacks"""
    try:
        from crewai import Crew, Agent, Task
        
        # Store original methods
        original_crew_kickoff = Crew.kickoff
        original_agent_execute = getattr(Agent, 'execute', None)
        
        def tracked_kickoff(self, inputs=None):
            """Patched kickoff method with tracking"""
            session_id = getattr(self, '_tracking_session_id', str(uuid4()))
            callback = create_callback_system(session_id)
            
            try:
                callback.on_crew_start(self, inputs or {})
                
                # Use output capture
                with CrewAIOutputCapture(session_id):
                    result = original_crew_kickoff(self, inputs)
                
                callback.on_crew_complete(self, result)
                return result
                
            except Exception as e:
                callback.on_error(e)
                raise
        
        # Apply patches
        Crew.kickoff = tracked_kickoff
        
        logger.info("Successfully patched CrewAI for real-time tracking")
        return True
        
    except ImportError:
        logger.warning("CrewAI not available, cannot patch for tracking")
        return False
    except Exception as e:
        logger.error(f"Failed to patch CrewAI: {e}")
        return False

# Initialize patches when module is imported
CREWAI_PATCHED = patch_crewai_for_tracking()