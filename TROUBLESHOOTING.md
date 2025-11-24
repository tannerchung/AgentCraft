# AgentCraft Troubleshooting Guide

Common issues and their solutions for AgentCraft deployment and operation.

## Table of Contents

1. [Database Connection Issues](#database-connection-issues)
2. [API Key Problems](#api-key-problems)
3. [WebSocket Failures](#websocket-failures)
4. [Performance Issues](#performance-issues)
5. [Knowledge Retrieval Problems](#knowledge-retrieval-problems)
6. [Docker Issues](#docker-issues)
7. [Frontend Issues](#frontend-issues)
8. [Agent Routing Problems](#agent-routing-problems)

---

## Database Connection Issues

### Problem: "Connection to database failed"

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Solutions:**

1. **Check DATABASE_URL format:**
```bash
# Correct format
DATABASE_URL=postgresql://username:password@host:5432/database

# Common mistakes
DATABASE_URL=postgres://...  # Wrong: should be postgresql://
DATABASE_URL=postgresql://host/database  # Missing username/password
```

2. **Verify database is running:**
```bash
# Local PostgreSQL
pg_isready -h localhost -p 5432

# Docker container
docker ps | grep postgres
docker logs agentcraft_postgres
```

3. **Test connection manually:**
```bash
psql $DATABASE_URL

# Or
psql -h localhost -U agentcraft -d agentcraft
```

4. **Check firewall rules:**
```bash
# Allow PostgreSQL port
sudo ufw allow 5432/tcp

# For cloud databases, check security groups
```

### Problem: "Too many connections"

**Symptoms:**
```
FATAL: sorry, too many clients already
```

**Solutions:**

1. **Increase connection pool limit:**
```python
# backend/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,          # Default connections
    max_overflow=10,      # Extra connections when needed
    pool_timeout=30,      # Wait time for connection
    pool_recycle=3600     # Recycle connections hourly
)
```

2. **Close idle connections:**
```python
# Add to database models
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

3. **Monitor active connections:**
```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'agentcraft';
```

### Problem: "Database schema not initialized"

**Symptoms:**
```
sqlalchemy.exc.ProgrammingError: relation "agents" does not exist
```

**Solutions:**

1. **Run schema initialization:**
```bash
# Using SQL file
psql $DATABASE_URL -f database/schema.sql

# Using Python script
python database/setup.py
```

2. **Run migrations:**
```bash
# If using Alembic
alembic upgrade head
```

3. **Verify tables exist:**
```sql
\dt  -- List all tables
SELECT * FROM agents LIMIT 1;  -- Test query
```

---

## API Key Problems

### Problem: "OpenAI/Anthropic API key invalid"

**Symptoms:**
```
AuthenticationError: Incorrect API key provided
```

**Solutions:**

1. **Verify API key format:**
```bash
# OpenAI keys start with sk-proj- or sk-
OPENAI_API_KEY=sk-proj-abc123...

# Anthropic keys start with sk-ant-
ANTHROPIC_API_KEY=sk-ant-api03-xyz789...
```

2. **Check for whitespace:**
```bash
# Remove any accidental spaces
OPENAI_API_KEY=$(echo $OPENAI_API_KEY | tr -d '[:space:]')
```

3. **Test API key directly:**
```python
# test_openai.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("API key valid!")
except Exception as e:
    print(f"API key error: {e}")
```

4. **Check API key permissions:**
- Verify key has not expired
- Check usage limits
- Ensure billing is active

### Problem: "Qdrant connection failed"

**Symptoms:**
```
ConnectionError: Failed to connect to Qdrant
```

**Solutions:**

1. **Verify Qdrant URL and API key:**
```bash
# Correct format
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_api_key

# Test with curl
curl -H "api-key: $QDRANT_API_KEY" "$QDRANT_URL/collections"
```

2. **Check Qdrant cluster status:**
- Log into Qdrant Cloud dashboard
- Verify cluster is running
- Check IP whitelist settings

3. **Use in-memory mode for testing:**
```python
# For development/testing without Qdrant Cloud
from src.services.qdrant_service import QdrantService

qdrant = QdrantService(use_memory=True)
```

### Problem: "Firecrawl API rate limit exceeded"

**Symptoms:**
```
RateLimitError: Rate limit exceeded
```

**Solutions:**

1. **Implement rate limiting:**
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=10):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                await asyncio.sleep(left_to_wait)
            ret = await func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator
```

2. **Use caching:**
```python
# Cache scraped content
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_content(url: str):
    return firecrawl_service.scrape_url(url)
```

---

## WebSocket Failures

### Problem: "WebSocket connection refused"

**Symptoms:**
```
WebSocket connection to 'ws://localhost:8000/ws/agent-tracking' failed
```

**Solutions:**

1. **Verify WebSocket endpoint:**
```javascript
// Correct endpoint
const ws = new WebSocket('ws://localhost:8000/ws/agent-tracking/client-123');

// Common mistakes
// ws://localhost:8000/api/ws/...  // Wrong: no /api/ prefix
// wss://localhost:8000/...  // Wrong protocol for local dev
```

2. **Check CORS settings:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **Verify backend is running:**
```bash
# Check if backend is listening on port 8000
netstat -an | grep 8000

# Or
curl http://localhost:8000/
```

4. **Test WebSocket manually:**
```javascript
// In browser console
const ws = new WebSocket('ws://localhost:8000/ws/agent-tracking/test');
ws.onopen = () => console.log('Connected!');
ws.onerror = (e) => console.error('Error:', e);
ws.onmessage = (e) => console.log('Message:', e.data);
```

### Problem: "WebSocket disconnects frequently"

**Symptoms:**
```
WebSocket connection closed unexpectedly
Reconnection attempts failing
```

**Solutions:**

1. **Implement proper heartbeat:**
```javascript
class WebSocketManager {
    connect() {
        this.ws = new WebSocket(this.url);
        this.startHeartbeat();
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Every 30 seconds
    }

    disconnect() {
        clearInterval(this.heartbeatInterval);
        this.ws.close();
    }
}
```

2. **Increase timeout:**
```python
# backend/websocket_api.py
try:
    data = await asyncio.wait_for(
        websocket.receive_text(),
        timeout=60.0  # Increase from 30 to 60 seconds
    )
except asyncio.TimeoutError:
    # Send ping
    pass
```

3. **Check network stability:**
```bash
# Monitor network connection
ping -c 10 localhost

# Check for packet loss
```

### Problem: "WebSocket messages not received"

**Symptoms:**
- Messages sent but not received by server
- Server messages not reaching client

**Solutions:**

1. **Verify message format:**
```javascript
// Correct: JSON stringified
ws.send(JSON.stringify({ type: 'get_session_state', session_id: '123' }));

// Wrong: Plain object
ws.send({ type: 'get_session_state' });  // Won't work
```

2. **Check message handlers:**
```javascript
ws.onmessage = (event) => {
    try {
        const message = JSON.parse(event.data);
        console.log('Received:', message);
        handleMessage(message);
    } catch (error) {
        console.error('Parse error:', error);
    }
};
```

3. **Add debugging:**
```python
# Server-side logging
@router.websocket("/agent-tracking/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    logger.info(f"WebSocket connection from {client_id}")

    async def handle_message(data):
        logger.info(f"Received from {client_id}: {data}")
        # Process message
```

---

## Performance Issues

### Problem: "Slow API responses"

**Symptoms:**
- Queries taking > 5 seconds
- Timeouts on requests

**Solutions:**

1. **Enable caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_agent_search(query: str):
    return qdrant_service.search(query)
```

2. **Optimize database queries:**
```python
# Bad: N+1 query problem
for agent in agents:
    metrics = get_agent_metrics(agent.id)  # Separate query each time

# Good: Batch query
agent_ids = [a.id for a in agents]
metrics = get_bulk_agent_metrics(agent_ids)  # Single query
```

3. **Use async operations:**
```python
# Parallel execution
results = await asyncio.gather(
    qdrant_service.search(query),
    firecrawl_service.scrape_url(url),
    get_conversation_context(session_id)
)
```

4. **Monitor with profiling:**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = process_query(query)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Problem: "High memory usage"

**Symptoms:**
```
Process using excessive memory (>2GB)
Out of memory errors
```

**Solutions:**

1. **Limit conversation history:**
```python
# In ConversationMemory
MAX_MESSAGES_PER_SESSION = 10

if len(self.conversations[session_id]) > MAX_MESSAGES_PER_SESSION:
    self.conversations[session_id] = self.conversations[session_id][-MAX_MESSAGES_PER_SESSION:]
```

2. **Clear old sessions:**
```python
def cleanup_old_conversations(self, max_age_hours=24):
    """Remove conversations older than max_age_hours"""
    cutoff = datetime.now() - timedelta(hours=max_age_hours)

    for session_id in list(self.conversations.keys()):
        summary = self.get_conversation_summary(session_id)
        if summary['last_activity']:
            last_activity = datetime.fromisoformat(summary['last_activity'])
            if last_activity < cutoff:
                del self.conversations[session_id]
```

3. **Use generators for large datasets:**
```python
# Bad: Loads all into memory
all_agents = Agent.objects.all()

# Good: Iterator
for agent in Agent.objects.iterator():
    process_agent(agent)
```

### Problem: "Database connection pool exhausted"

**Symptoms:**
```
TimeoutError: QueuePool limit exceeded
```

**Solutions:**

1. **Increase pool size:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,      # Increase from default 5
    max_overflow=40    # Increase from default 10
)
```

2. **Ensure connections are closed:**
```python
# Use context managers
async with get_db() as db:
    result = await db.execute(query)
    # Connection automatically closed
```

---

## Knowledge Retrieval Problems

### Problem: "No results from knowledge search"

**Symptoms:**
- Search returns empty results
- Relevant content exists but not found

**Solutions:**

1. **Verify collection exists:**
```python
# Check Qdrant collections
collections = qdrant_service.client.get_collections()
print([c.name for c in collections.collections])
```

2. **Re-index knowledge base:**
```python
# Re-create and index
qdrant_service._initialize_collection()
articles = qdrant_service.generate_mock_knowledge_base()
qdrant_service.index_knowledge_base(articles)
```

3. **Check similarity threshold:**
```python
# Lower threshold for broader matches
results = qdrant_service.search(
    query=query,
    limit=10  # Increase from 5
)

# Check scores
for result in results:
    print(f"Score: {result['similarity_score']:.2f} - {result['title']}")
```

### Problem: "Firecrawl timeout errors"

**Symptoms:**
```
TimeoutError: Scraping timed out
```

**Solutions:**

1. **Increase timeout:**
```python
# In firecrawl_service
result = await asyncio.wait_for(
    self.app.scrape_url(url),
    timeout=60.0  # Increase from default
)
```

2. **Use mock mode for testing:**
```python
# Firecrawl automatically uses mock mode without API key
# Just don't set FIRECRAWL_API_KEY in development
```

3. **Implement retries:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def scrape_with_retry(url):
    return await firecrawl_service.scrape_url(url)
```

---

## Docker Issues

### Problem: "Container fails to start"

**Symptoms:**
```
Error response from daemon: container exited with code 1
```

**Solutions:**

1. **Check container logs:**
```bash
docker logs agentcraft_backend
docker logs agentcraft_frontend
```

2. **Verify environment variables:**
```bash
# Check env vars are set
docker exec agentcraft_backend env | grep DATABASE_URL
```

3. **Test dependencies:**
```bash
# Enter container
docker exec -it agentcraft_backend /bin/bash

# Test database connection
psql $DATABASE_URL

# Test Python imports
python -c "import fastapi; print('OK')"
```

4. **Rebuild without cache:**
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Problem: "Port already in use"

**Symptoms:**
```
Error starting container: port is already allocated
```

**Solutions:**

1. **Find process using port:**
```bash
# Find process on port 8000
lsof -i :8000

# Or
netstat -tulpn | grep 8000
```

2. **Kill process:**
```bash
# Kill process by PID
kill -9 <PID>

# Or stop Docker container
docker stop $(docker ps -q --filter "publish=8000")
```

3. **Change port:**
```yaml
# docker-compose.yml
services:
  backend:
    ports:
      - "8001:8000"  # Use 8001 instead
```

---

## Frontend Issues

### Problem: "npm install fails"

**Symptoms:**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE could not resolve
```

**Solutions:**

1. **Use legacy peer deps:**
```bash
npm install --legacy-peer-deps
```

2. **Clear cache:**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

3. **Use specific Node version:**
```bash
# Install nvm
nvm install 18
nvm use 18
npm install
```

### Problem: "Cannot connect to API"

**Symptoms:**
```
NetworkError: Failed to fetch
CORS error
```

**Solutions:**

1. **Verify API URL:**
```javascript
// In .env or code
REACT_APP_API_URL=http://localhost:8000

// Not http://localhost:8000/api  (no /api suffix)
```

2. **Check CORS configuration:**
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **Test API directly:**
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/agents/list
```

---

## Agent Routing Problems

### Problem: "Wrong agent selected for query"

**Symptoms:**
- Technical queries routed to non-technical agents
- Low confidence scores

**Solutions:**

1. **Check agent keywords:**
```python
# Verify agent has relevant keywords
agent = agent_router.agents['technical_integration']
print(agent.keywords)  # Should include 'webhook', 'api', etc.
```

2. **Adjust confidence threshold:**
```python
# Lower threshold for more permissive routing
DEFAULT_CONFIDENCE_THRESHOLD = 0.3  # Instead of 0.5
```

3. **Add more specific keywords:**
```python
agent.keywords.extend([
    'integration',
    'api',
    'rest',
    'webhook',
    'authentication'
])
```

### Problem: "Agents not collaborating"

**Symptoms:**
- Single agent handling complex queries
- No handoffs observed

**Solutions:**

1. **Enable collaboration:**
```python
# Check collaboration is enabled
collaboration_enabled = True
```

2. **Lower complexity threshold:**
```python
# Trigger collaboration for moderately complex queries
COMPLEXITY_THRESHOLD = 0.6  # Instead of 0.8
```

---

## Getting Help

### Diagnostic Information to Collect

When reporting issues, include:

```bash
# 1. System information
python --version
node --version
docker --version

# 2. Environment check
env | grep -E '(DATABASE|API_KEY|QDRANT|FIRECRAWL)'

# 3. Service status
docker ps
curl http://localhost:8000/health

# 4. Recent logs
docker logs agentcraft_backend --tail=50
tail -50 logs/agentcraft.log

# 5. Error message (full traceback)
```

### Support Resources

- **GitHub Issues**: https://github.com/your-repo/agentcraft/issues
- **Documentation**: [README.md](README.md)
- **API Reference**: [API.md](API.md)

---

## Related Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment
- [TESTING.md](TESTING.md) - Testing strategies
- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Database configuration
- [WEBSOCKET.md](WEBSOCKET.md) - WebSocket protocol
