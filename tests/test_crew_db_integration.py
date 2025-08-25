#!/usr/bin/env python3
"""
Unit tests for CrewAI database integration
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agents.crew_db_integration import DatabaseCrewAgent, CrewAIAgentPool

class TestDatabaseCrewAgent:
    """Test DatabaseCrewAgent functionality"""
    
    @pytest.fixture
    def sample_agent_data(self):
        """Sample agent data for testing"""
        return {
            'id': 'test-agent-123',
            'name': 'Test Competitive Analyst',
            'role': 'Competitive Intelligence Specialist',
            'backstory': 'Expert in market analysis and competitive positioning',
            'goal': 'Analyze competitive landscape and provide strategic insights',
            'keywords': ['competitive', 'analysis', 'market', 'strategy'],
            'llm_config': {'model': 'gpt-3.5-turbo', 'temperature': 0.7},
            'tools': [],
            'domain': 'analysis',
            'avatar': '📊',
            'color': 'blue',
            'specialization_score': 0.85,
            'collaboration_rating': 0.75,
            'updated_at': datetime.now().timestamp()
        }
    
    def test_agent_initialization(self, sample_agent_data):
        """Test DatabaseCrewAgent initialization"""
        agent = DatabaseCrewAgent(sample_agent_data)
        
        assert agent.id == 'test-agent-123'
        assert agent.name == 'Test Competitive Analyst'
        assert agent.role == 'Competitive Intelligence Specialist'
        assert agent.domain == 'analysis'
        assert agent.keywords == ['competitive', 'analysis', 'market', 'strategy']
        assert agent.llm_config == {'model': 'gpt-3.5-turbo', 'temperature': 0.7}
        assert agent.specialization_score == 0.85
        assert agent.collaboration_rating == 0.75
    
    def test_parse_json_field_with_string(self, sample_agent_data):
        """Test JSON field parsing when data is a string"""
        # Simulate string JSON data from database
        sample_agent_data['keywords'] = '["competitive", "analysis", "market"]'
        sample_agent_data['llm_config'] = '{"model": "gpt-4", "temperature": 0.5}'
        
        agent = DatabaseCrewAgent(sample_agent_data)
        
        assert agent.keywords == ["competitive", "analysis", "market"]
        assert agent.llm_config == {"model": "gpt-4", "temperature": 0.5}
    
    def test_parse_json_field_with_invalid_json(self, sample_agent_data):
        """Test JSON field parsing with invalid JSON falls back to default"""
        sample_agent_data['keywords'] = 'invalid json string'
        sample_agent_data['llm_config'] = 'also invalid'
        
        agent = DatabaseCrewAgent(sample_agent_data)
        
        assert agent.keywords == []  # Default value
        assert agent.llm_config == {}  # Default value
    
    def test_enhance_backstory_for_delegation(self, sample_agent_data):
        """Test backstory enhancement with delegation instructions"""
        agent = DatabaseCrewAgent(sample_agent_data)
        
        enhanced_backstory = agent._enhance_backstory_for_delegation()
        
        assert "IMPORTANT DELEGATION RULES" in enhanced_backstory
        assert "Delegate work to coworker" in enhanced_backstory
        assert "simple strings only" in enhanced_backstory
        assert "WRONG:" in enhanced_backstory
        assert "RIGHT:" in enhanced_backstory
        # Should include original backstory
        assert sample_agent_data['backstory'] in enhanced_backstory
    
    @patch('src.agents.crew_db_integration.CREWAI_AVAILABLE', True)
    def test_crew_agent_creation_success(self, sample_agent_data):
        """Test successful CrewAI agent creation"""
        with patch('src.agents.crew_db_integration.Agent') as mock_agent:
            mock_crew_agent = Mock()
            mock_agent.return_value = mock_crew_agent
            
            agent = DatabaseCrewAgent(sample_agent_data)
            crew_agent = agent.crew_agent
            
            assert crew_agent is mock_crew_agent
            mock_agent.assert_called_once()
            
            # Verify Agent was called with correct parameters
            call_args = mock_agent.call_args
            assert call_args[1]['role'] == sample_agent_data['role']
            assert call_args[1]['goal'] == sample_agent_data['goal']
            assert call_args[1]['verbose'] is True
            assert call_args[1]['allow_delegation'] is True
    
    @patch('src.agents.crew_db_integration.CREWAI_AVAILABLE', False)
    def test_crew_agent_creation_unavailable(self, sample_agent_data):
        """Test CrewAI agent creation when CrewAI is unavailable"""
        agent = DatabaseCrewAgent(sample_agent_data)
        crew_agent = agent.crew_agent
        
        assert crew_agent is None
    
    def test_to_dict_conversion(self, sample_agent_data):
        """Test conversion to dictionary format"""
        agent = DatabaseCrewAgent(sample_agent_data)
        agent_dict = agent.to_dict()
        
        expected_keys = [
            'id', 'name', 'role', 'backstory', 'goal', 'keywords',
            'llm_config', 'tools', 'domain', 'avatar', 'color',
            'specialization_score', 'collaboration_rating'
        ]
        
        for key in expected_keys:
            assert key in agent_dict
        
        assert agent_dict['id'] == str(sample_agent_data['id'])
        assert agent_dict['name'] == sample_agent_data['name']
        assert agent_dict['specialization_score'] == sample_agent_data['specialization_score']

class TestCrewAIAgentPool:
    """Test CrewAIAgentPool functionality"""
    
    @pytest.fixture
    def sample_db_agents(self):
        """Sample database agents data"""
        return [
            {
                'id': 'agent-1',
                'name': 'Competitive Analyst',
                'role': 'Market Research Specialist',
                'domain': 'analysis',
                'keywords': ['competitive', 'market', 'analysis'],
                'is_active': True,
                'specialization_score': 0.9,
                'collaboration_rating': 0.8,
                'updated_at': datetime.now().timestamp()
            },
            {
                'id': 'agent-2',
                'name': 'Technical Specialist',
                'role': 'Technical Integration Expert',
                'domain': 'technical',
                'keywords': ['api', 'webhook', 'integration'],
                'is_active': True,
                'specialization_score': 0.85,
                'collaboration_rating': 0.75,
                'updated_at': datetime.now().timestamp()
            },
            {
                'id': 'agent-3',
                'name': 'Inactive Agent',
                'role': 'Unused Agent',
                'domain': 'general',
                'keywords': ['general'],
                'is_active': False,  # Should be filtered out
                'specialization_score': 0.5,
                'collaboration_rating': 0.5,
                'updated_at': datetime.now().timestamp()
            }
        ]
    
    @pytest.fixture
    def agent_pool(self):
        """Create fresh agent pool for each test"""
        return CrewAIAgentPool(cache_ttl=60)  # Short TTL for testing
    
    @pytest.mark.asyncio
    async def test_pool_initialization(self, agent_pool):
        """Test agent pool initialization"""
        assert not agent_pool.initialized
        assert len(agent_pool.agents_cache) == 0
        assert len(agent_pool.agents_by_id) == 0
        assert agent_pool.cache_ttl == 60
    
    @pytest.mark.asyncio
    async def test_refresh_agents(self, agent_pool, sample_db_agents):
        """Test refreshing agents from database"""
        with patch('src.agents.crew_db_integration.db_manager.initialize') as mock_db_init, \
             patch('src.agents.crew_db_integration.agent_manager.get_all_agents') as mock_get_agents:
            
            mock_get_agents.return_value = sample_db_agents
            
            await agent_pool.refresh_agents()
            
            # Should only load active agents (2 out of 3)
            assert len(agent_pool.agents_cache) == 2
            assert len(agent_pool.agents_by_id) == 2
            
            assert 'Competitive Analyst' in agent_pool.agents_cache
            assert 'Technical Specialist' in agent_pool.agents_cache
            assert 'Inactive Agent' not in agent_pool.agents_cache
    
    @pytest.mark.asyncio
    async def test_get_agent_by_name(self, agent_pool, sample_db_agents):
        """Test getting agent by name"""
        with patch('src.agents.crew_db_integration.agent_manager.get_all_agents') as mock_get_agents:
            mock_get_agents.return_value = sample_db_agents
            
            await agent_pool.refresh_agents()
            
            # Test existing agent
            agent = await agent_pool.get_agent('Competitive Analyst')
            assert agent is not None
            assert agent.name == 'Competitive Analyst'
            assert agent.domain == 'analysis'
            
            # Test non-existent agent
            missing_agent = await agent_pool.get_agent('Non-existent Agent')
            assert missing_agent is None
    
    @pytest.mark.asyncio
    async def test_get_agents_by_keywords(self, agent_pool, sample_db_agents):
        """Test getting agents by keyword matching"""
        with patch('src.agents.crew_db_integration.agent_manager.get_all_agents') as mock_get_agents:
            mock_get_agents.return_value = sample_db_agents
            
            await agent_pool.refresh_agents()
            
            # Test keyword matching
            competitive_agents = await agent_pool.get_agents_by_keywords(['competitive', 'market'])
            assert len(competitive_agents) >= 1
            assert any(agent.name == 'Competitive Analyst' for agent in competitive_agents)
            
            technical_agents = await agent_pool.get_agents_by_keywords(['api', 'webhook'])
            assert len(technical_agents) >= 1
            assert any(agent.name == 'Technical Specialist' for agent in technical_agents)
            
            # Test no matches
            no_match_agents = await agent_pool.get_agents_by_keywords(['nonexistent', 'keyword'])
            assert len(no_match_agents) == 0
    
    @pytest.mark.asyncio
    async def test_create_crew_success(self, agent_pool, sample_db_agents):
        """Test successful crew creation"""
        with patch('src.agents.crew_db_integration.agent_manager.get_all_agents') as mock_get_agents, \
             patch('src.agents.crew_db_integration.Crew') as mock_crew_class, \
             patch('src.agents.crew_db_integration.Task') as mock_task_class, \
             patch('src.agents.crew_db_integration.Agent') as mock_agent_class, \
             patch('src.agents.crew_db_integration.CREWAI_AVAILABLE', True):
            
            mock_get_agents.return_value = sample_db_agents
            await agent_pool.refresh_agents()
            
            # Mock crew creation
            mock_crew = Mock()
            mock_crew_class.return_value = mock_crew
            
            # Mock task creation
            mock_task = Mock()
            mock_task_class.return_value = mock_task
            
            # Mock agent creation
            mock_agent = Mock()
            mock_agent_class.return_value = mock_agent
            
            agent_names = ['Competitive Analyst', 'Technical Specialist']
            tasks = [
                {'description': 'Analyze competition', 'expected_output': 'Analysis report'},
                {'description': 'Check technical feasibility', 'expected_output': 'Technical report'}
            ]
            
            crew = await agent_pool.create_crew(agent_names, tasks)
            
            assert crew is mock_crew
            mock_crew_class.assert_called_once()
            
            # Verify crew was created with correct parameters
            call_kwargs = mock_crew_class.call_args[1]
            assert 'agents' in call_kwargs
            assert 'tasks' in call_kwargs
            assert call_kwargs['verbose'] is True
            assert call_kwargs['memory'] is True
    
    @pytest.mark.asyncio
    async def test_create_crew_no_valid_agents(self, agent_pool, sample_db_agents):
        """Test crew creation with no valid agents"""
        with patch('src.agents.crew_db_integration.agent_manager.get_all_agents') as mock_get_agents:
            mock_get_agents.return_value = sample_db_agents
            await agent_pool.refresh_agents()
            
            # Try to create crew with non-existent agents
            agent_names = ['Non-existent Agent 1', 'Non-existent Agent 2']
            tasks = [{'description': 'Test task', 'expected_output': 'Test output'}]
            
            crew = await agent_pool.create_crew(agent_names, tasks)
            
            assert crew is None
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, agent_pool, sample_db_agents):
        """Test agent cache invalidation"""
        with patch('src.agents.crew_db_integration.agent_manager.get_all_agents') as mock_get_agents:
            mock_get_agents.return_value = sample_db_agents
            
            await agent_pool.refresh_agents()
            assert 'Competitive Analyst' in agent_pool.agents_cache
            
            # Invalidate specific agent
            await agent_pool.invalidate_agent('Competitive Analyst')
            # Agent should still be in cache, but its crew_agent should be invalidated
            assert 'Competitive Analyst' in agent_pool.agents_cache
    
    @pytest.mark.asyncio
    async def test_ensure_fresh_cache(self, agent_pool, sample_db_agents):
        """Test cache freshness management"""
        with patch('src.agents.crew_db_integration.agent_manager.get_all_agents') as mock_get_agents:
            mock_get_agents.return_value = sample_db_agents
            
            # Set very short cache TTL for testing
            agent_pool.cache_ttl = 0.1  # 100ms
            
            await agent_pool.refresh_agents()
            initial_refresh_time = agent_pool.last_refresh
            
            # Wait for cache to expire
            await asyncio.sleep(0.2)
            
            # This should trigger a refresh
            await agent_pool._ensure_fresh_cache()
            
            assert agent_pool.last_refresh > initial_refresh_time

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])