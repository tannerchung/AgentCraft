# Contributing to AgentCraft

Thank you for your interest in contributing to AgentCraft! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Code Style](#code-style)
5. [Git Workflow](#git-workflow)
6. [Pull Request Process](#pull-request-process)
7. [Testing Requirements](#testing-requirements)
8. [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal attacks or insults
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.11 or higher
- Node.js 18 or higher
- Git
- Docker (optional but recommended)
- PostgreSQL (local or cloud)

### Finding Work

1. **Check Issues**: Browse [open issues](https://github.com/your-repo/agentcraft/issues) for tasks labeled:
   - `good-first-issue` - Great for newcomers
   - `help-wanted` - Community contributions welcome
   - `bug` - Bug fixes needed
   - `enhancement` - Feature requests

2. **Propose New Features**: Open an issue to discuss your idea before implementing

3. **Ask Questions**: Don't hesitate to ask for clarification or help

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/agentcraft.git
cd agentcraft

# Add upstream remote
git remote add upstream https://github.com/original-repo/agentcraft.git
```

### 2. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools

# Frontend dependencies
cd src
npm install
cd ..
```

### 3. Set Up Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (optional for development)
nano .env
```

### 4. Initialize Database

```bash
# Using Docker
docker-compose up -d postgres

# Or local PostgreSQL
createdb agentcraft
psql agentcraft -f database/schema.sql
```

### 5. Run Development Servers

```bash
# Terminal 1: Backend
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd src
npm start

# Access at http://localhost:3000
```

---

## Code Style

### Python Code Style

We follow **PEP 8** with some modifications.

#### Formatting

```python
# Use Black for consistent formatting
pip install black
black backend/ src/ tests/

# Configuration in pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
```

#### Linting

```python
# Use Flake8 for linting
pip install flake8
flake8 backend/ src/ tests/

# Configuration in .flake8
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203,W503
```

#### Type Hints

Use type hints for function signatures:

```python
# Good
def process_query(query: str, session_id: str = None) -> Dict[str, Any]:
    """Process a user query"""
    return {"response": "..."}

# Bad
def process_query(query, session_id=None):
    return {"response": "..."}
```

#### Imports

```python
# Order: standard library, third-party, local
import os
import sys
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.core.agent_router import agent_router
from src.services.qdrant_service import qdrant_service
```

#### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int = 0) -> Dict[str, Any]:
    """
    Brief description of what the function does.

    Longer description with more details about the implementation,
    edge cases, or important considerations.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 0)

    Returns:
        Dictionary containing:
            - key1: Description
            - key2: Description

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer

    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['key1'])
        'value1'
    """
    if not param1:
        raise ValueError("param1 cannot be empty")

    return {"key1": "value1", "key2": param2}
```

### JavaScript/React Code Style

#### Formatting

```bash
# Use Prettier for formatting
npm install --save-dev prettier
npx prettier --write "src/**/*.{js,jsx,css}"

# Configuration in .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "printWidth": 100
}
```

#### ESLint

```bash
# Install ESLint
npm install --save-dev eslint
npx eslint src/

# Configuration in .eslintrc.json
{
  "extends": ["react-app", "react-app/jest"],
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "off"
  }
}
```

#### Component Structure

```javascript
// Good: Functional component with hooks
import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * AgentCard displays information about a single agent
 */
const AgentCard = ({ agent, onSelect }) => {
    const [isActive, setIsActive] = useState(false);

    useEffect(() => {
        // Setup code
        return () => {
            // Cleanup code
        };
    }, [agent]);

    return (
        <div className="agent-card">
            <h3>{agent.name}</h3>
            <p>{agent.role}</p>
        </div>
    );
};

AgentCard.propTypes = {
    agent: PropTypes.shape({
        name: PropTypes.string.isRequired,
        role: PropTypes.string.isRequired
    }).isRequired,
    onSelect: PropTypes.func
};

export default AgentCard;
```

---

## Git Workflow

### Branch Naming

```bash
# Feature branches
feature/add-new-agent-type
feature/improve-knowledge-retrieval

# Bug fixes
fix/websocket-connection-issue
fix/database-connection-pool

# Documentation
docs/update-api-documentation
docs/add-deployment-guide

# Tests
test/add-agent-routing-tests
test/improve-coverage
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```bash
# Format
<type>(<scope>): <subject>

<body>

<footer>

# Examples
feat(agents): add competitive intelligence agent

Add new agent specialized in competitive analysis and market research.
Includes integration with external data sources and citation generation.

Closes #123

---

fix(websocket): resolve connection timeout issue

Increase heartbeat interval from 30s to 60s to prevent premature
connection closures on slow networks.

Fixes #456

---

docs(api): update knowledge API documentation

Add examples for new search parameters and clarify citation format.

---

test(services): add Qdrant service integration tests

Implement comprehensive tests for vector search, indexing, and
error handling scenarios.
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge upstream changes into your main branch
git checkout main
git merge upstream/main

# Push updates to your fork
git push origin main

# Rebase your feature branch
git checkout feature/your-feature
git rebase main
```

---

## Pull Request Process

### Before Submitting

1. **Test your changes:**
```bash
# Run test suite
pytest tests/ -v

# Check code style
black --check backend/ src/
flake8 backend/ src/

# Frontend checks
npm test
npm run lint
```

2. **Update documentation:**
- Add/update docstrings
- Update relevant .md files
- Add code examples if needed

3. **Add tests:**
- Unit tests for new functions
- Integration tests for new features
- Update existing tests if behavior changed

### Creating a Pull Request

1. **Push your branch:**
```bash
git push origin feature/your-feature
```

2. **Open PR on GitHub:**
- Use a clear, descriptive title
- Fill out the PR template completely
- Link related issues with `Closes #123` or `Fixes #456`

3. **PR Template:**
```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made
- Added X functionality
- Fixed Y issue
- Updated Z documentation

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated

## Screenshots (if applicable)
Add screenshots for UI changes.

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. **Automated Checks:**
   - Tests must pass
   - Code coverage maintained
   - Linting checks pass

2. **Code Review:**
   - At least one approval required
   - Address review comments
   - Update as requested

3. **Merge:**
   - Squash and merge for clean history
   - Delete branch after merge

---

## Testing Requirements

### Minimum Requirements

All contributions must include:

1. **Unit Tests:**
```python
def test_new_feature():
    """Test that new feature works correctly"""
    result = new_feature_function(input_data)
    assert result is not None
    assert result['status'] == 'success'
```

2. **Coverage:**
```bash
# Maintain >80% coverage
pytest tests/ --cov=src --cov=backend --cov-report=term
```

3. **Integration Tests** (for major features):
```python
@pytest.mark.asyncio
async def test_feature_integration():
    """Test feature integration with other components"""
    # Setup
    # Execute
    # Assert
```

### Test Organization

```python
# Group related tests in classes
class TestAgentRouting:
    """Test agent routing functionality"""

    def test_technical_query_routing(self):
        """Test routing of technical queries"""
        pass

    def test_business_query_routing(self):
        """Test routing of business queries"""
        pass
```

### Running Tests Locally

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_new_feature.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

---

## Documentation

### Code Documentation

1. **Docstrings:** All public functions, classes, and modules
2. **Comments:** Complex logic and non-obvious code
3. **Type Hints:** Function parameters and return values

### User Documentation

Update relevant documentation files:

- **README.md**: For major features
- **API.md**: For API changes
- **SERVICES.md**: For new services
- **FRONTEND.md**: For UI changes
- **DEPLOYMENT.md**: For deployment changes

### Documentation Style

```markdown
# Clear Headings

## Subheadings

Use **bold** for emphasis and `code` for technical terms.

### Code Examples

Provide complete, working examples:

```python
# Good example with context
from src.core.agent_router import agent_router

result = agent_router.route_query("How do I fix webhooks?")
print(result['routing_info']['selected_agent'])
# Output: "Technical Integration Specialist"
```

### Lists

Use ordered lists for steps:
1. First step
2. Second step
3. Third step

Use unordered lists for options:
- Option A
- Option B
- Option C
```

---

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Example: `2.1.3`

### Creating a Release

1. **Update version:**
```python
# backend/main.py
__version__ = "2.1.3"
```

2. **Update CHANGELOG.md:**
```markdown
## [2.1.3] - 2024-01-20

### Added
- New competitive intelligence agent
- Qdrant cloud integration

### Fixed
- WebSocket connection stability
- Database connection pool management

### Changed
- Improved knowledge retrieval accuracy
```

3. **Tag release:**
```bash
git tag -a v2.1.3 -m "Release version 2.1.3"
git push origin v2.1.3
```

---

## Questions or Problems?

- **Questions**: Open a discussion on GitHub
- **Bugs**: Open an issue with reproduction steps
- **Security**: Email security@agentcraft.com (do not open public issue)

---

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to AgentCraft!

---

## Related Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [TESTING.md](TESTING.md) - Testing guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
