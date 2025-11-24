# AgentCraft Testing Documentation

Complete guide to testing AgentCraft's multi-agent AI system.

## Table of Contents

1. [Overview](#overview)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Test Categories](#test-categories)
5. [Writing Tests](#writing-tests)
6. [Test Coverage](#test-coverage)
7. [CI/CD Integration](#cicd-integration)
8. [Best Practices](#best-practices)

---

## Overview

AgentCraft includes a comprehensive test suite covering API endpoints, agent functionality, knowledge retrieval, WebSocket communication, and integration scenarios.

### Test Directory Structure

```
tests/
├── test_api_endpoints.py           # API endpoint tests
├── test_technical_agent.py         # Agent functionality tests
├── test_adaptive_system.py         # Multi-LLM system tests
├── test_realtime_tracking.py       # WebSocket tracking tests
├── test_webhook_scenarios.py       # Webhook scenario tests
├── test_crew_db_integration.py     # Database integration tests
├── test_galileo_integration.py     # Galileo observability tests
├── test_basic_adaptive.py          # Basic adaptive tests
└── conftest.py                     # Shared fixtures
```

### Testing Stack

```python
{
    "test_framework": "pytest",
    "async_support": "pytest-asyncio",
    "http_client": "httpx",
    "mocking": "unittest.mock",
    "coverage": "pytest-cov"
}
```

---

## Test Structure

### Test File Organization

Each test file follows a consistent structure:

```python
#!/usr/bin/env python3
"""
Test module description
Tests specific functionality or component
"""

import sys
import os
import pytest
from typing import Dict, Any

# Add project root to path
sys.path.append('.')

# Import modules to test
from src.core.agent_router import agent_router
from backend.main import app

# Test fixtures
@pytest.fixture
def sample_query():
    """Sample query for testing"""
    return "How do I fix webhook signature validation errors?"

# Test classes
class TestAgentRouting:
    """Test agent routing functionality"""

    def test_webhook_query_routing(self, sample_query):
        """Test webhook query routes to correct agent"""
        result = agent_router.route_query(sample_query)

        assert result['success'] is True
        assert 'Technical' in result['routing_info']['selected_agent']
        assert result['routing_info']['confidence'] > 0.7

    def test_competitive_query_routing(self):
        """Test competitive query routing"""
        query = "How does this compare to Salesforce AgentForce?"
        result = agent_router.route_query(query)

        assert result['success'] is True
        assert result['agent_response']['competitive_advantage'] is not None
```

### Test Naming Conventions

```python
# Good test names (descriptive and specific)
def test_webhook_signature_verification_with_valid_secret():
    pass

def test_api_returns_404_for_nonexistent_agent():
    pass

def test_conversation_memory_retains_last_10_messages():
    pass

# Bad test names (vague)
def test_webhook():
    pass

def test_api():
    pass
```

---

## Running Tests

### Run All Tests

```bash
# Run complete test suite
python -m pytest tests/ -v

# With output
python -m pytest tests/ -v -s

# Stop on first failure
python -m pytest tests/ -x
```

### Run Specific Tests

```bash
# Run single test file
python -m pytest tests/test_technical_agent.py -v

# Run specific test
python -m pytest tests/test_api_endpoints.py::test_query_endpoint -v

# Run tests matching pattern
python -m pytest tests/ -k "webhook" -v
```

### Run with Coverage

```bash
# Generate coverage report
python -m pytest tests/ --cov=src --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw tests/ -- -v
```

---

## Test Categories

### 1. API Endpoint Tests

**File:** `tests/test_api_endpoints.py`

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/")

    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "ok"

def test_query_endpoint():
    """Test query processing endpoint"""
    payload = {
        "query": "How do I fix webhook errors?",
        "context": {"user_id": "test_user"}
    }

    response = client.post("/api/query", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "response" in data
    assert "routing_info" in data

def test_agent_list_endpoint():
    """Test agent listing endpoint"""
    response = client.get("/api/agents/list")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "agents" in data
    assert data["total_agents"] > 0

def test_knowledge_search_endpoint():
    """Test knowledge search endpoint"""
    response = client.get("/api/knowledge/search?q=webhook&limit=5")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "results" in data
    assert isinstance(data["results"], list)
```

### 2. Agent Functionality Tests

**File:** `tests/test_technical_agent.py`

```python
from src.core.agent_router import agent_router
from src.agents.technical_support_agent import get_technical_demo_scenarios

def test_webhook_expertise():
    """Test webhook troubleshooting capabilities"""
    query = "Our webhook integration stopped working. Getting 403 errors."

    result = agent_router.route_query(query)

    assert result['success'] is True
    assert 'Technical' in result['routing_info']['selected_agent']
    assert result['routing_info']['confidence'] > 0.7

    # Check for technical details
    response = result['agent_response']
    assert 'technical_response' in response

    if 'issue_analysis' in response['technical_response']:
        analysis = response['technical_response']['issue_analysis']
        assert 'diagnosis' in analysis
        assert 'solution' in analysis

def test_competitive_intelligence():
    """Test competitive analysis capabilities"""
    query = "How does your webhook handling compare to Salesforce AgentForce?"

    result = agent_router.route_query(query)

    assert result['success'] is True
    response = result['agent_response']['technical_response']

    assert 'competitor_limitations' in response
    assert 'cost_comparison' in response
    assert len(response['competitor_limitations']) > 0

def test_demo_scenarios():
    """Test all demo scenarios"""
    scenarios = get_technical_demo_scenarios()

    for scenario_name, scenario_query in scenarios.items():
        result = agent_router.route_query(scenario_query)

        assert result['success'] is True, f"Scenario {scenario_name} failed"
        assert result['routing_info']['confidence'] > 0.5
```

### 3. WebSocket Tests

**File:** `tests/test_realtime_tracking.py`

```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.main import app

@pytest.mark.asyncio
async def test_websocket_connection():
    """Test WebSocket connection establishment"""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/agent-tracking/test-client") as websocket:
            # Should receive active sessions on connect
            data = websocket.receive_json()

            assert data["type"] == "active_sessions"
            assert "data" in data

@pytest.mark.asyncio
async def test_agent_status_updates():
    """Test agent status update messages"""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/agent-tracking/test-client") as websocket:
            # Skip initial active_sessions message
            websocket.receive_json()

            # Request session state
            websocket.send_json({
                "type": "get_session_state",
                "session_id": "test_session"
            })

            # Should receive response
            response = websocket.receive_json()
            assert response["type"] in ["session_state", "session_not_found"]

@pytest.mark.asyncio
async def test_ping_pong_heartbeat():
    """Test WebSocket heartbeat mechanism"""
    with TestClient(app) as client:
        with client.websocket_connect("/ws/agent-tracking/test-client") as websocket:
            # Wait for ping
            for _ in range(5):
                data = websocket.receive_json()
                if data["type"] == "ping":
                    # Send pong
                    websocket.send_json({"type": "pong"})
                    break
```

### 4. Integration Tests

**File:** `tests/test_crew_db_integration.py`

```python
import pytest
from database.models import Agent, Conversation
from backend.main import conversation_memory

@pytest.mark.asyncio
async def test_database_connection():
    """Test database connection"""
    # Test that database is accessible
    agent_count = await Agent.count()
    assert agent_count >= 0

@pytest.mark.asyncio
async def test_conversation_storage():
    """Test conversation storage"""
    session_id = "test_session_123"

    # Add messages
    conversation_memory.add_message(
        session_id=session_id,
        role="user",
        message="Test message"
    )

    # Retrieve messages
    messages = conversation_memory.conversations.get(session_id, [])

    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Test message"

@pytest.mark.asyncio
async def test_agent_crud_operations():
    """Test agent CRUD operations"""
    # Create agent
    agent_data = {
        "name": "Test Agent",
        "role": "Testing specialist",
        "domain": "testing",
        "is_active": True
    }

    agent = await Agent.create(**agent_data)
    assert agent.id is not None

    # Read agent
    retrieved = await Agent.get(id=agent.id)
    assert retrieved.name == "Test Agent"

    # Update agent
    await Agent.update(id=agent.id, role="Updated role")
    updated = await Agent.get(id=agent.id)
    assert updated.role == "Updated role"

    # Delete agent
    await Agent.delete(id=agent.id)
    deleted = await Agent.get_or_none(id=agent.id)
    assert deleted is None
```

### 5. Service Tests

```python
import pytest
from src.services.qdrant_service import qdrant_service, KnowledgeArticle
from src.services.firecrawl_service import firecrawl_service

def test_qdrant_indexing():
    """Test Qdrant knowledge base indexing"""
    articles = [
        KnowledgeArticle(
            id="test_001",
            title="Test Article",
            content="Test content for search",
            category="Testing",
            tags=["test", "example"],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    ]

    # Index articles
    success = qdrant_service.index_knowledge_base(articles)
    assert success is True

    # Search
    results = qdrant_service.search("test content", limit=5)
    assert len(results) > 0
    assert results[0]["title"] == "Test Article"

@pytest.mark.asyncio
async def test_firecrawl_scraping():
    """Test Firecrawl web scraping"""
    url = "https://zapier.com/help/webhooks"

    result = await firecrawl_service.scrape_url(url)

    assert result["success"] is True
    assert "title" in result
    assert "content" in result
    assert len(result["content"]) > 0
```

---

## Writing Tests

### Test Template

```python
import pytest
from typing import Dict, Any

class TestFeatureName:
    """Test suite for specific feature"""

    @pytest.fixture
    def setup_data(self):
        """Setup test data"""
        return {
            "key": "value"
        }

    def test_basic_functionality(self, setup_data):
        """Test basic functionality works"""
        # Arrange
        input_data = setup_data

        # Act
        result = function_under_test(input_data)

        # Assert
        assert result is not None
        assert result["status"] == "success"

    def test_edge_case(self):
        """Test edge case handling"""
        # Arrange
        edge_case_input = None

        # Act & Assert
        with pytest.raises(ValueError):
            function_under_test(edge_case_input)

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality"""
        # Arrange
        query = "test query"

        # Act
        result = await async_function(query)

        # Assert
        assert result is not None
```

### Mocking External Services

```python
from unittest.mock import Mock, patch, AsyncMock

def test_with_mocked_api():
    """Test with mocked external API"""
    with patch('src.services.external_api.call') as mock_call:
        # Setup mock
        mock_call.return_value = {"status": "success", "data": "test"}

        # Test code that uses external API
        result = function_that_calls_api()

        # Verify
        assert result["data"] == "test"
        mock_call.assert_called_once()

@pytest.mark.asyncio
async def test_with_async_mock():
    """Test async function with mock"""
    with patch('src.services.firecrawl_service.scrape_url', new_callable=AsyncMock) as mock_scrape:
        # Setup async mock
        mock_scrape.return_value = {
            "success": True,
            "content": "mocked content"
        }

        # Test
        result = await function_using_scraper()

        assert result is not None
        mock_scrape.assert_awaited_once()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("query,expected_agent", [
    ("How do I fix webhooks?", "Technical Integration Specialist"),
    ("What's the pricing?", "Billing & Revenue Expert"),
    ("Security concerns", "Security Specialist"),
])
def test_agent_routing(query, expected_agent):
    """Test agent routing for various queries"""
    result = agent_router.route_query(query)

    assert result['success'] is True
    assert expected_agent in result['routing_info']['selected_agent']
```

---

## Test Coverage

### Running Coverage Analysis

```bash
# Generate coverage report
pytest tests/ --cov=src --cov=backend --cov-report=html --cov-report=term

# Output:
# ---------- coverage: platform linux, python 3.11.0 -----------
# Name                              Stmts   Miss  Cover
# -----------------------------------------------------
# backend/main.py                     245     15    94%
# src/core/agent_router.py            156      8    95%
# src/services/qdrant_service.py      198     22    89%
# src/services/firecrawl_service.py   167     28    83%
# -----------------------------------------------------
# TOTAL                              1247    128    90%
```

### Coverage Targets

```python
# pytest.ini or setup.cfg
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Coverage settings
[coverage:run]
source = src,backend
omit =
    */tests/*
    */venv/*
    */__pycache__/*

[coverage:report]
# Fail if coverage below 80%
fail_under = 80
precision = 2
show_missing = True
```

### Identifying Untested Code

```bash
# Show lines not covered
pytest tests/ --cov=src --cov-report=term-missing

# Output shows line numbers:
# Name                    Stmts   Miss  Cover   Missing
# -----------------------------------------------------
# src/core/agent.py         156      8    95%   45-52, 89
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio

    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov=backend --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        fail_ci_if_error: true
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        args: ['tests/', '-v']
        language: system
        pass_filenames: false
        always_run: true
```

---

## Best Practices

### 1. Test Independence

```python
# Good: Each test is independent
def test_feature_a():
    setup()
    result = test_a()
    cleanup()
    assert result

def test_feature_b():
    setup()
    result = test_b()
    cleanup()
    assert result

# Bad: Tests depend on each other
def test_step_1():
    global state
    state = initialize()

def test_step_2():  # Depends on test_step_1
    result = process(state)
```

### 2. Clear Assertions

```python
# Good: Specific assertions with messages
assert result['status'] == 'success', f"Expected success, got {result['status']}"
assert len(items) == 5, f"Expected 5 items, got {len(items)}"

# Bad: Vague assertions
assert result
assert items
```

### 3. Test Data Management

```python
# Use fixtures for reusable test data
@pytest.fixture
def sample_conversation():
    """Sample conversation for testing"""
    return {
        "session_id": "test_123",
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    }

def test_with_fixture(sample_conversation):
    result = process_conversation(sample_conversation)
    assert result is not None
```

### 4. Async Testing

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality properly"""
    result = await async_operation()
    assert result is not None

# Not this:
def test_async_wrong():
    result = async_operation()  # Returns coroutine, not result
    assert result  # Always True!
```

### 5. Error Testing

```python
# Test expected errors
def test_invalid_input_raises_error():
    with pytest.raises(ValueError) as exc_info:
        process_data(invalid_input)

    assert "Invalid input" in str(exc_info.value)
```

---

## Related Documentation

- [API.md](API.md) - API endpoints to test
- [SERVICES.md](SERVICES.md) - Service implementations
- [DEPLOYMENT.md](DEPLOYMENT.md) - Testing in production
- [CONTRIBUTING.md](CONTRIBUTING.md) - Testing requirements for contributions
