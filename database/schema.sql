-- AgentCraft PostgreSQL Database Schema
-- Agent configuration and metrics for self-improvement loops

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Agent configurations table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    role VARCHAR(500) NOT NULL,
    backstory TEXT,
    goal TEXT,
    llm_config JSONB,
    tools JSONB DEFAULT '[]'::jsonb,
    keywords JSONB DEFAULT '[]'::jsonb,
    avatar VARCHAR(10),
    color VARCHAR(50),
    domain VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    specialization_score FLOAT DEFAULT 0.0,
    collaboration_rating FLOAT DEFAULT 0.0
);

-- Agent performance metrics table
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    session_id UUID,
    query_hash VARCHAR(64), -- Hash of the query for deduplication
    query_text TEXT,
    response_quality FLOAT,
    response_time_ms INTEGER,
    tokens_used INTEGER,
    cost_per_request FLOAT,
    user_feedback_rating INTEGER CHECK (user_feedback_rating >= 1 AND user_feedback_rating <= 5),
    llm_used VARCHAR(100),
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    context JSONB DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation sessions table
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    query TEXT NOT NULL,
    agents_selected JSONB,
    final_response TEXT,
    total_response_time_ms INTEGER,
    user_satisfaction INTEGER CHECK (user_satisfaction >= 1 AND user_satisfaction <= 5),
    escalated_to_human BOOLEAN DEFAULT false,
    escalation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Agent collaboration patterns table
CREATE TABLE agent_collaborations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    primary_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    secondary_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    collaboration_type VARCHAR(50), -- 'delegation', 'consultation', 'parallel', 'sequential'
    effectiveness_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System learning insights table
CREATE TABLE learning_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    insight_type VARCHAR(100), -- 'agent_optimization', 'workflow_improvement', 'user_pattern'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    confidence_score FLOAT,
    data_points INTEGER,
    recommended_actions JSONB,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'implemented', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    implemented_at TIMESTAMP WITH TIME ZONE
);

-- Agent skill evolution tracking
CREATE TABLE agent_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    skill_name VARCHAR(255),
    proficiency_score FLOAT,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    improvement_trend FLOAT DEFAULT 0.0, -- Positive = improving, Negative = declining
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, skill_name)
);

-- Query pattern analysis
CREATE TABLE query_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_hash VARCHAR(64) UNIQUE,
    pattern_description VARCHAR(500),
    frequency INTEGER DEFAULT 1,
    optimal_agents JSONB,
    avg_response_time_ms FLOAT,
    avg_satisfaction FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- A/B testing experiments
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    experiment_type VARCHAR(100), -- 'agent_selection', 'llm_choice', 'workflow'
    configuration_a JSONB,
    configuration_b JSONB,
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'paused', 'completed'
    results JSONB DEFAULT '{}'::jsonb,
    winner VARCHAR(1) CHECK (winner IN ('A', 'B')) -- NULL if no clear winner
);

-- Galileo integration logs
CREATE TABLE galileo_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trace_id UUID,
    session_id UUID REFERENCES conversation_sessions(id) ON DELETE SET NULL,
    event_type VARCHAR(100),
    payload JSONB,
    status VARCHAR(50) DEFAULT 'sent', -- 'sent', 'failed', 'pending'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    galileo_response JSONB
);

-- Indexes for performance
CREATE INDEX idx_agents_domain ON agents(domain);
CREATE INDEX idx_agents_active ON agents(is_active);
CREATE INDEX idx_agent_metrics_agent_id ON agent_metrics(agent_id);
CREATE INDEX idx_agent_metrics_recorded_at ON agent_metrics(recorded_at);
CREATE INDEX idx_agent_metrics_query_hash ON agent_metrics(query_hash);
CREATE INDEX idx_conversation_sessions_created_at ON conversation_sessions(created_at);
CREATE INDEX idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX idx_agent_collaborations_session_id ON agent_collaborations(session_id);
CREATE INDEX idx_query_patterns_pattern_hash ON query_patterns(pattern_hash);
CREATE INDEX idx_query_patterns_frequency ON query_patterns(frequency DESC);
CREATE INDEX idx_agent_skills_agent_id ON agent_skills(agent_id);
CREATE INDEX idx_agent_skills_proficiency ON agent_skills(proficiency_score DESC);

-- Update timestamp triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_skills_updated_at BEFORE UPDATE ON agent_skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default agent configurations
INSERT INTO agents (name, role, backstory, goal, llm_config, keywords, avatar, color, domain) VALUES
('Orchestration Agent', 'Query analysis and agent coordination', 
 'You are the central coordinator responsible for understanding user queries and selecting the most appropriate specialist agents to handle each request.', 
 'Efficiently route queries to the right agents and synthesize their responses',
 '{"model": "claude-3-5-sonnet", "temperature": 0.1}'::jsonb,
 '["routing", "synthesis", "coordination"]'::jsonb,
 '🧠', 'purple', 'orchestration'),

('Technical Integration Specialist', 'API, webhook, and integration issues',
 'You are an expert in technical integrations, API troubleshooting, webhook management, and solving complex connectivity issues.',
 'Resolve technical integration problems quickly and effectively',
 '{"model": "claude-3-5-sonnet", "temperature": 0.2}'::jsonb,
 '["webhook", "api", "ssl", "integration", "authentication", "timeout", "certificate"]'::jsonb,
 '🔧', 'blue', 'technical'),

('DevOps Engineer', 'Deployment, infrastructure, and monitoring',
 'You specialize in DevOps practices, infrastructure management, deployment pipelines, and system monitoring.',
 'Optimize deployment processes and infrastructure reliability',
 '{"model": "claude-3-5-sonnet", "temperature": 0.2}'::jsonb,
 '["deployment", "docker", "kubernetes", "ci/cd", "monitoring", "infrastructure", "pipeline"]'::jsonb,
 '⚙️', 'cyan', 'technical'),

('Security Specialist', 'Security audits and vulnerability assessment',
 'You are a cybersecurity expert focused on identifying vulnerabilities, implementing security best practices, and ensuring compliance.',
 'Maintain the highest security standards and protect against threats',
 '{"model": "claude-3-5-sonnet", "temperature": 0.1}'::jsonb,
 '["security", "vulnerability", "encryption", "compliance", "oauth", "gdpr", "audit"]'::jsonb,
 '🛡️', 'red', 'technical'),

('Database Expert', 'Database optimization and migrations',
 'You specialize in database design, optimization, migration strategies, and performance tuning.',
 'Ensure optimal database performance and data integrity',
 '{"model": "claude-3-5-sonnet", "temperature": 0.2}'::jsonb,
 '["database", "sql", "migration", "optimization", "query", "index", "schema"]'::jsonb,
 '🗄️', 'indigo', 'technical'),

('Billing & Revenue Expert', 'Payment processing and subscription management',
 'You are an expert in billing systems, payment processing, subscription management, and revenue optimization.',
 'Optimize billing processes and resolve payment-related issues',
 '{"model": "gpt-4", "temperature": 0.1}'::jsonb,
 '["billing", "payment", "subscription", "invoice", "revenue", "refund", "dunning"]'::jsonb,
 '💳', 'green', 'business'),

('Legal Compliance Agent', 'Contract analysis and compliance',
 'You specialize in legal compliance, contract analysis, regulatory requirements, and policy development.',
 'Ensure legal compliance and minimize regulatory risks',
 '{"model": "claude-3-5-sonnet", "temperature": 0.1}'::jsonb,
 '["legal", "contract", "compliance", "gdpr", "privacy", "terms", "policy"]'::jsonb,
 '⚖️', 'gray', 'business'),

('Competitive Intelligence Analyst', 'Market research and competitive positioning',
 'You analyze market trends, competitive landscapes, and provide strategic insights for business positioning.',
 'Provide actionable competitive intelligence and market insights',
 '{"model": "claude-3-5-sonnet", "temperature": 0.3}'::jsonb,
 '["competitive", "competitor", "market", "analysis", "positioning", "strategy", "intelligence"]'::jsonb,
 '🎯', 'orange', 'analysis');

-- Insert sample query patterns for learning
INSERT INTO query_patterns (pattern_hash, pattern_description, optimal_agents, avg_response_time_ms, avg_satisfaction) VALUES
('webhook_issues', 'Webhook integration and SSL certificate problems', 
 '["Technical Integration Specialist", "Security Specialist"]'::jsonb, 2500, 4.2),
('billing_problems', 'Payment and subscription billing issues',
 '["Billing & Revenue Expert"]'::jsonb, 1800, 4.5),
('security_audit', 'Security vulnerabilities and compliance checks',
 '["Security Specialist", "Legal Compliance Agent"]'::jsonb, 3200, 4.8),
('database_performance', 'Database optimization and query performance',
 '["Database Expert", "DevOps Engineer"]'::jsonb, 2800, 4.1);