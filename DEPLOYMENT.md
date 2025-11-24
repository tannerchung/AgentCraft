# AgentCraft Production Deployment Guide

Complete guide for deploying AgentCraft to production environments.

## Table of Contents

1. [Overview](#overview)
2. [Docker Setup](#docker-setup)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Cloud Deployments](#cloud-deployments)
6. [Scaling Strategies](#scaling-strategies)
7. [Monitoring](#monitoring)
8. [Security](#security)

---

## Overview

AgentCraft is designed for production deployment with Docker, cloud-native architectures, and horizontal scaling capabilities.

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Optional)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Frontend (React)│    │  Frontend (React)│
│  Port: 3000      │    │  Port: 3000      │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Backend (FastAPI)    │
         │  Port: 8000           │
         │  - WebSocket          │
         │  - REST API           │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  PostgreSQL      │    │  External Services│
│  Port: 5432      │    │  - Qdrant Cloud   │
└──────────────────┘    │  - Firecrawl      │
                        │  - OpenAI/Claude  │
                        └──────────────────┘
```

### Prerequisites

- Docker & Docker Compose
- PostgreSQL database (local or cloud)
- API keys for required services
- Domain name (for production)
- SSL certificates (for HTTPS)

---

## Docker Setup

### Docker Compose Configuration

AgentCraft includes a `docker-compose.yml` for local development and testing.

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: agentcraft_postgres
    environment:
      POSTGRES_DB: agentcraft
      POSTGRES_USER: agentcraft
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
    networks:
      - agentcraft_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U agentcraft -d agentcraft"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    container_name: agentcraft_backend
    environment:
      - DATABASE_URL=postgresql://agentcraft:${POSTGRES_PASSWORD}@postgres:5432/agentcraft
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - QDRANT_URL=${QDRANT_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - agentcraft_network
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: agentcraft_frontend
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - agentcraft_network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local

networks:
  agentcraft_network:
    driver: bridge
```

### Backend Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl --fail http://localhost:8000/ || exit 1

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build application
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration

```nginx
# nginx.conf
server {
    listen 3000;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket proxy
    location /ws/ {
        proxy_pass http://backend:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Running with Docker Compose

```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Environment Configuration

### Production .env File

```bash
# .env.production

# Application
APP_NAME=AgentCraft
APP_VERSION=2.0.0
ENVIRONMENT=production
DEBUG=False

# API Keys (Required)
OPENAI_API_KEY=sk-proj-your_openai_api_key
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key

# External Knowledge Services
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/agentcraft

# Optional Services
GALILEO_API_KEY=your_galileo_api_key
GALILEO_PROJECT=AgentCraft-Production
GALILEO_LOG_STREAM=production

# Security
SECRET_KEY=your_secret_key_min_32_chars
ALLOWED_HOSTS=agentcraft.com,*.agentcraft.com
CORS_ORIGINS=https://agentcraft.com,https://app.agentcraft.com

# Performance
WORKERS=4
MAX_CONNECTIONS=100
TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Environment Validation

```python
# backend/config.py
import os
from typing import Optional
import logging

class Config:
    """Production configuration"""

    # Required environment variables
    REQUIRED_VARS = [
        'DATABASE_URL',
        'SECRET_KEY'
    ]

    # Optional but recommended
    RECOMMENDED_VARS = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'QDRANT_URL',
        'QDRANT_API_KEY'
    ]

    @classmethod
    def validate(cls):
        """Validate environment configuration"""
        missing = []
        for var in cls.REQUIRED_VARS:
            if not os.getenv(var):
                missing.append(var)

        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        # Warn about missing recommended vars
        for var in cls.RECOMMENDED_VARS:
            if not os.getenv(var):
                logging.warning(f"Recommended environment variable not set: {var}")

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> str:
        """Get environment variable"""
        return os.getenv(key, default)

# Validate on import
Config.validate()
```

---

## Database Setup

### PostgreSQL Cloud Options

#### 1. Neon (Recommended)

```bash
# Neon PostgreSQL
DATABASE_URL=postgresql://user:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/agentcraft?sslmode=require
```

**Advantages:**
- Serverless PostgreSQL
- Auto-scaling
- Branching for testing
- Free tier available

**Setup:**
1. Sign up at https://neon.tech
2. Create project
3. Copy connection string
4. Run schema initialization

#### 2. Amazon RDS

```bash
# Amazon RDS
DATABASE_URL=postgresql://user:password@agentcraft.123456789012.us-east-1.rds.amazonaws.com:5432/agentcraft
```

#### 3. Google Cloud SQL

```bash
# Cloud SQL
DATABASE_URL=postgresql://user:password@/agentcraft?host=/cloudsql/project:region:instance
```

### Database Initialization

```bash
# Initialize database schema
psql $DATABASE_URL -f database/schema.sql

# Or using Python
python database/setup.py
```

### Database Migrations

```python
# database/migrations/001_initial_schema.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('session_id', sa.String(255), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now())
    )

def downgrade():
    op.drop_table('conversations')
```

```bash
# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Cloud Deployments

### AWS Deployment

#### Using AWS ECS (Fargate)

```yaml
# docker-compose.ecs.yml
version: '3.8'

services:
  backend:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/agentcraft-backend:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    logging:
      driver: awslogs
      options:
        awslogs-group: /ecs/agentcraft
        awslogs-region: us-east-1
        awslogs-stream-prefix: backend
```

**Deployment Steps:**

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker build -t agentcraft-backend .
docker tag agentcraft-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentcraft-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/agentcraft-backend:latest

# 2. Update ECS service
aws ecs update-service --cluster agentcraft --service agentcraft-backend --force-new-deployment
```

### Vercel (Frontend Only)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Set environment variables
vercel env add REACT_APP_API_URL production
```

**vercel.json:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app",
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Render

```yaml
# render.yaml
services:
  - type: web
    name: agentcraft-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: agentcraft-db
          property: connectionString

  - type: web
    name: agentcraft-frontend
    env: static
    buildCommand: npm install && npm run build
    staticPublishPath: ./build

databases:
  - name: agentcraft-db
    plan: free
```

---

## Scaling Strategies

### Horizontal Scaling

#### Load Balancer Configuration (Nginx)

```nginx
# nginx-lb.conf
upstream backend_servers {
    least_conn;
    server backend1:8000 weight=1;
    server backend2:8000 weight=1;
    server backend3:8000 weight=1;
}

server {
    listen 80;
    server_name api.agentcraft.com;

    location / {
        proxy_pass http://backend_servers;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml agentcraft

# Scale service
docker service scale agentcraft_backend=3
```

#### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentcraft-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentcraft-backend
  template:
    metadata:
      labels:
        app: agentcraft-backend
    spec:
      containers:
      - name: backend
        image: agentcraft/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: agentcraft-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: agentcraft-backend
spec:
  selector:
    app: agentcraft-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Vertical Scaling

```yaml
# docker-compose with resource limits
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Auto-Scaling (AWS)

```json
{
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 75.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }
}
```

---

## Monitoring

### Health Checks

```python
# backend/main.py
@app.get("/health")
async def health_check():
    """Comprehensive health check"""

    checks = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # Database check
    try:
        # Test database connection
        await db.execute("SELECT 1")
        checks["checks"]["database"] = "healthy"
    except Exception as e:
        checks["status"] = "unhealthy"
        checks["checks"]["database"] = f"unhealthy: {str(e)}"

    # Qdrant check
    try:
        metrics = qdrant_service.get_metrics()
        checks["checks"]["qdrant"] = metrics["status"]
    except Exception as e:
        checks["checks"]["qdrant"] = f"error: {str(e)}"

    # External services
    checks["checks"]["firecrawl"] = "available" if firecrawl_service.app else "unavailable"

    return checks
```

### Prometheus Metrics

```python
# Install: pip install prometheus-fastapi-instrumentator

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)
```

### Logging

```python
# backend/logging_config.py
import logging
import json

class JSONFormatter(logging.Formatter):
    """JSON log formatter for production"""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Set JSON formatter
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

### Application Performance Monitoring (APM)

```python
# Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv("ENVIRONMENT", "production")
)
```

---

## Security

### SSL/TLS Configuration

```nginx
# nginx-ssl.conf
server {
    listen 443 ssl http2;
    server_name agentcraft.com;

    ssl_certificate /etc/ssl/certs/agentcraft.crt;
    ssl_certificate_key /etc/ssl/private/agentcraft.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
```

### Security Headers

```python
# backend/middleware.py
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### API Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/query")
@limiter.limit("10/minute")
async def query_endpoint(request: Request):
    # Endpoint logic
    pass
```

### Secrets Management

```bash
# Using AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id agentcraft/production --query SecretString --output text

# Using environment variables with Docker secrets
echo "my_secret_value" | docker secret create db_password -
```

---

## Related Documentation

- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Database configuration
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Deployment issues
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [TESTING.md](TESTING.md) - Testing before deployment
