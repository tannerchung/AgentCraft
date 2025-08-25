# AgentCraft Database Setup

This guide will help you set up PostgreSQL for persistent agent configurations and metrics collection.

## 🚀 Quick Start with Docker

### 1. Start PostgreSQL with Docker Compose

```bash
# Start PostgreSQL and pgAdmin
docker-compose up -d

# Check status
docker-compose ps
```

This will create:
- **PostgreSQL**: `localhost:5432` (username: `agentcraft`, password: `agentcraft`)
- **pgAdmin**: `localhost:5050` (email: `admin@agentcraft.com`, password: `agentcraft`)

### 2. Initialize Database Schema

```bash
# Install database dependencies
pip install -r requirements-db.txt

# Run database setup
python database/setup.py
```

### 3. Update Environment Variables

Add to your `.env` file:

```env
# Database Configuration
DATABASE_URL=postgresql://agentcraft:agentcraft@localhost:5432/agentcraft

# Optional: Enable enhanced logging
LOG_LEVEL=INFO
```

## 🛠️ Manual PostgreSQL Setup

If you prefer to install PostgreSQL manually:

### 1. Install PostgreSQL

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 2. Create Database and User

```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE agentcraft;
CREATE USER agentcraft WITH PASSWORD 'agentcraft';
GRANT ALL PRIVILEGES ON DATABASE agentcraft TO agentcraft;
ALTER USER agentcraft CREATEDB;
\q
```

### 3. Update DATABASE_URL

```env
DATABASE_URL=postgresql://agentcraft:agentcraft@localhost:5432/agentcraft
```

### 4. Run Setup Script

```bash
python database/setup.py
```

## 📊 Database Schema Overview

The database includes these key tables:

### Core Tables
- **`agents`**: Agent configurations, LLM settings, and performance scores
- **`agent_metrics`**: Individual response metrics and quality scores
- **`conversation_sessions`**: Complete conversation tracking
- **`agent_collaborations`**: Multi-agent interaction patterns

### Learning Tables
- **`learning_insights`**: AI-generated improvement recommendations
- **`agent_skills`**: Individual skill proficiency tracking
- **`query_patterns`**: Common query pattern optimization
- **`experiments`**: A/B testing configurations and results

### Integration Tables
- **`galileo_logs`**: Observability platform integration logs

## 🔧 Database Management

### Using the CLI Tool

```bash
# List all agents
python database/cli.py list

# Show performance metrics
python database/cli.py performance
python database/cli.py performance --agent "Technical Integration Specialist"

# Create a new agent
python database/cli.py create "Security Auditor" \
  "Advanced security analysis and compliance checking" \
  --domain security \
  --keywords "security,audit,compliance,vulnerability" \
  --avatar "🔒" \
  --color "red"

# View learning insights
python database/cli.py insights

# Analyze query patterns
python database/cli.py patterns
```

### Direct Database Access

**Using pgAdmin (Web Interface):**
1. Open `http://localhost:5050`
2. Login with `admin@agentcraft.com` / `agentcraft`
3. Add server: `postgres:5432`, username: `agentcraft`, password: `agentcraft`

**Using Command Line:**
```bash
# Connect to database
psql postgresql://agentcraft:agentcraft@localhost:5432/agentcraft

# Example queries
SELECT name, domain, specialization_score FROM agents WHERE is_active = true;
SELECT COUNT(*) FROM agent_metrics WHERE recorded_at > NOW() - INTERVAL '7 days';
```

## 🎯 Key Benefits

### 1. **Persistent Agent Configurations**
- Agents survive server restarts
- Dynamic agent creation and modification
- Version-controlled agent evolution

### 2. **Advanced Metrics Collection**
- Response quality tracking
- Performance optimization data
- User satisfaction correlation

### 3. **Self-Improvement Loops**
- Automated learning insights generation
- Query pattern optimization
- Agent skill evolution tracking

### 4. **A/B Testing Framework**
- Experiment different agent configurations
- Compare LLM performance
- Data-driven optimization decisions

## 🔍 Monitoring and Observability

### Performance Queries

```sql
-- Top performing agents (last 30 days)
SELECT 
    a.name,
    COUNT(am.*) as interactions,
    AVG(am.response_quality) as avg_quality,
    AVG(am.response_time_ms) as avg_response_time
FROM agents a
JOIN agent_metrics am ON a.id = am.agent_id
WHERE am.recorded_at > NOW() - INTERVAL '30 days'
GROUP BY a.id, a.name
ORDER BY avg_quality DESC, interactions DESC;

-- Query pattern analysis
SELECT 
    pattern_description,
    frequency,
    avg_satisfaction,
    optimal_agents
FROM query_patterns
ORDER BY frequency DESC
LIMIT 10;
```

### Learning Insights

```sql
-- Pending improvement recommendations
SELECT 
    insight_type,
    title,
    confidence_score,
    recommended_actions
FROM learning_insights
WHERE status = 'pending'
ORDER BY confidence_score DESC;
```

## 🚨 Troubleshooting

### Common Issues

**Connection Failed:**
```bash
# Check if PostgreSQL is running
docker-compose ps
# or
sudo systemctl status postgresql

# Check connection
psql postgresql://agentcraft:agentcraft@localhost:5432/agentcraft -c "SELECT 1;"
```

**Schema Issues:**
```bash
# Reset database (⚠️ destroys all data)
docker-compose down -v
docker-compose up -d
python database/setup.py
```

**Permission Errors:**
```bash
# Grant permissions
sudo -u postgres psql -c "ALTER USER agentcraft CREATEDB;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE agentcraft TO agentcraft;"
```

## 🔄 Migration and Backup

### Backup Database

```bash
# Create backup
docker exec agentcraft_postgres pg_dump -U agentcraft agentcraft > backup.sql

# Restore backup
docker exec -i agentcraft_postgres psql -U agentcraft agentcraft < backup.sql
```

### Update Schema

When updating the schema, run:

```bash
# Apply new migrations
python database/setup.py

# Or manually apply specific changes
psql postgresql://agentcraft:agentcraft@localhost:5432/agentcraft -f new_migration.sql
```

## 🎉 Next Steps

Once your database is set up:

1. **Start the backend**: `uv run python backend/main.py`
2. **Create custom agents**: Use the CLI or API endpoints
3. **Monitor performance**: Check the pgAdmin dashboard
4. **Review learning insights**: `python database/cli.py insights`

Your agents will now persist across server restarts and continuously improve through metrics collection and self-learning loops!