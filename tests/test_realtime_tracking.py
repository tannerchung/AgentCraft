#!/usr/bin/env python3
"""
Unit tests for the real-time agent tracking system
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agents.realtime_agent_tracker import (
    RealtimeAgentTracker, AgentStatus, AgentActivity, CrewExecutionState
)

class TestAgentStatus:
    """Test AgentStatus enum"""
    
    def test_agent_status_values(self):
        """Test that all expected agent status values exist"""
        expected_statuses = [
            'IDLE', 'ANALYZING', 'PROCESSING', 'COLLABORATING', 
            'COMPLETING', 'FINISHED', 'ERROR'
        ]
        
        for status in expected_statuses:
            assert hasattr(AgentStatus, status)
            assert isinstance(getattr(AgentStatus, status), AgentStatus)

class TestAgentActivity:
    """Test AgentActivity data class"""
    
    def test_agent_activity_creation(self):
        """Test AgentActivity creation with valid parameters"""
        activity = AgentActivity(
            agent_id="test_123",
            agent_name="TestAgent",
            status=AgentStatus.PROCESSING,
            current_task="Test task",
            progress=75.0,
            details="Processing test data"
        )
        
        assert activity.agent_id == "test_123"
        assert activity.agent_name == "TestAgent"
        assert activity.status == AgentStatus.PROCESSING
        assert activity.current_task == "Test task"
        assert activity.progress == 75.0
        assert activity.details == "Processing test data"
        assert activity.started_at is not None
        assert activity.updated_at is not None

class TestCrewExecutionState:
    """Test CrewExecutionState data class"""
    
    def test_crew_execution_state_creation(self):
        """Test CrewExecutionState creation"""
        agent1 = AgentActivity("1", "Agent1", AgentStatus.PROCESSING, "Task1", 50.0)
        agent2 = AgentActivity("2", "Agent2", AgentStatus.FINISHED, "Task2", 100.0)
        
        execution_state = CrewExecutionState(
            session_id="session_123",
            query="Test query",
            total_agents=2,
            active_agents=[agent1, agent2]
        )
        
        assert execution_state.session_id == "session_123"
        assert execution_state.query == "Test query"
        assert execution_state.total_agents == 2
        assert len(execution_state.active_agents) == 2
        assert execution_state.current_phase == "initialization"
        assert execution_state.overall_progress == 75.0  # Average of 50% and 100%

class TestRealtimeAgentTracker:
    """Test RealtimeAgentTracker functionality"""
    
    @pytest.fixture
    def tracker(self):
        """Create a fresh tracker instance for each test"""
        return RealtimeAgentTracker()
    
    def test_tracker_initialization(self, tracker):
        """Test tracker initializes with empty state"""
        assert len(tracker.active_sessions) == 0
        assert len(tracker.websocket_connections) == 0
        assert len(tracker.execution_logs) == 0
    
    def test_start_session(self, tracker):
        """Test starting a new tracking session"""
        session_id = "test_session_123"
        query = "Test competitive analysis query"
        agent_names = ["CompetitiveAnalyst", "MarketResearcher"]
        
        tracker.start_session(session_id, query, agent_names)
        
        assert session_id in tracker.active_sessions
        session = tracker.active_sessions[session_id]
        
        assert session.session_id == session_id
        assert session.query == query
        assert session.total_agents == len(agent_names)
        assert len(session.active_agents) == len(agent_names)
        
        # Check that agents were created with correct initial state
        for i, agent_name in enumerate(agent_names):
            agent = session.active_agents[i]
            assert agent.agent_name == agent_name
            assert agent.status == AgentStatus.IDLE
            assert agent.progress == 0.0
    
    def test_update_agent_status(self, tracker):
        """Test updating agent status"""
        session_id = "test_session_123"
        agent_name = "TestAgent"
        
        # Start session first
        tracker.start_session(session_id, "Test query", [agent_name])
        
        # Update agent status
        tracker.update_agent_status(
            session_id=session_id,
            agent_name=agent_name,
            status=AgentStatus.PROCESSING,
            task="Analyzing data",
            progress=60.0,
            details="Processing user request"
        )
        
        session = tracker.active_sessions[session_id]
        agent = next(a for a in session.active_agents if a.agent_name == agent_name)
        
        assert agent.status == AgentStatus.PROCESSING
        assert agent.current_task == "Analyzing data"
        assert agent.progress == 60.0
        assert agent.details == "Processing user request"
    
    def test_add_crew_output(self, tracker):
        """Test adding crew output logs"""
        session_id = "test_session_123"
        
        # Start session
        tracker.start_session(session_id, "Test query", ["TestAgent"])
        
        # Add crew output
        tracker.add_crew_output(
            session_id=session_id,
            output_type="analysis",
            content="Test analysis complete",
            agent_name="TestAgent"
        )
        
        session = tracker.active_sessions[session_id]
        assert len(session.crew_output) == 1
        
        output = session.crew_output[0]
        assert output["type"] == "analysis"
        assert output["content"] == "Test analysis complete"
        assert output["agent"] == "TestAgent"
        assert "timestamp" in output
    
    def test_complete_session(self, tracker):
        """Test completing a session"""
        session_id = "test_session_123"
        final_result = "Analysis complete: Competitive positioning established"
        
        # Start session
        tracker.start_session(session_id, "Test query", ["TestAgent"])
        
        # Complete session
        tracker.complete_session(session_id, final_result)
        
        session = tracker.active_sessions[session_id]
        assert session.current_phase == "completed"
        assert session.crew_output[-1]["content"] == final_result
    
    def test_error_session(self, tracker):
        """Test handling session errors"""
        session_id = "test_session_123"
        error_message = "Connection timeout"
        failed_agent = "TestAgent"
        
        # Start session
        tracker.start_session(session_id, "Test query", [failed_agent])
        
        # Trigger error
        tracker.error_session(session_id, error_message, failed_agent)
        
        session = tracker.active_sessions[session_id]
        assert session.current_phase == "error"
        
        # Check that the failed agent status is updated
        failed_agent_obj = next(a for a in session.active_agents if a.agent_name == failed_agent)
        assert failed_agent_obj.status == AgentStatus.ERROR
        assert error_message in failed_agent_obj.details
    
    def test_get_active_sessions_summary(self, tracker):
        """Test getting active sessions summary"""
        # Start multiple sessions
        tracker.start_session("session1", "Query 1", ["Agent1"])
        tracker.start_session("session2", "Query 2", ["Agent2", "Agent3"])
        
        summary = tracker.get_active_sessions_summary()
        
        assert summary["total_sessions"] == 2
        assert len(summary["sessions"]) == 2
        session_ids = [s["session_id"] for s in summary["sessions"]]
        assert "session1" in session_ids
        assert "session2" in session_ids
    
    def test_websocket_management(self, tracker):
        """Test WebSocket connection management"""
        # Mock WebSocket
        mock_websocket1 = Mock()
        mock_websocket2 = Mock()
        
        # Add connections
        tracker.add_websocket_connection(mock_websocket1)
        tracker.add_websocket_connection(mock_websocket2)
        
        assert len(tracker.websocket_connections) == 2
        assert mock_websocket1 in tracker.websocket_connections
        assert mock_websocket2 in tracker.websocket_connections
        
        # Remove connection
        tracker.remove_websocket_connection(mock_websocket1)
        
        assert len(tracker.websocket_connections) == 1
        assert mock_websocket1 not in tracker.websocket_connections
        assert mock_websocket2 in tracker.websocket_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_update(self, tracker):
        """Test broadcasting updates to WebSocket connections"""
        # Mock WebSocket connections
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        
        tracker.add_websocket_connection(mock_ws1)
        tracker.add_websocket_connection(mock_ws2)
        
        # Start a session first so broadcast has data
        tracker.start_session("test_123", "Test query", ["TestAgent"])
        
        # Broadcast update
        await tracker._broadcast_update("test_123", "agent_status_update")
        
        # Verify both WebSockets received the update
        mock_ws1.send_text.assert_called_once()
        mock_ws2.send_text.assert_called_once()
        
        # Check the sent data
        sent_data1 = json.loads(mock_ws1.send_text.call_args[0][0])
        assert sent_data1["type"] == "agent_status_update"
        assert sent_data1["session_id"] == "test_123"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])