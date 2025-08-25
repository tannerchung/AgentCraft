
#!/usr/bin/env python3
"""
Enhanced AgentCraft Database Setup for Replit PostgreSQL
"""

import os
import asyncio
import asyncpg
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        # Use Replit's DATABASE_URL environment variable
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set. Please create a PostgreSQL database in Replit.")
        
        self.pool = None
    
    async def initialize(self):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            print("✅ Connected to Replit PostgreSQL database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()

    async def create_tables(self):
        """Create all required tables"""
        schema_file = Path(__file__).parent / "schema.sql"
        
        if not schema_file.exists():
            print("❌ Schema file not found. Creating basic schema...")
            await self.create_basic_schema()
            return
        
        try:
            async with self.pool.acquire() as conn:
                schema_sql = schema_file.read_text()
                await conn.execute(schema_sql)
                print("✅ Database schema created successfully")
        except Exception as e:
            print(f"❌ Schema creation failed: {e}")
            await self.create_basic_schema()
    
    async def create_basic_schema(self):
        """Create basic schema if schema.sql doesn't exist"""
        basic_schema = """
        -- AgentCraft Core Tables
        CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            domain VARCHAR(100),
            specialization_score DECIMAL(3,2) DEFAULT 0.80,
            keywords TEXT[],
            avatar VARCHAR(10) DEFAULT '🤖',
            color VARCHAR(20) DEFAULT 'blue',
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS agent_metrics (
            id SERIAL PRIMARY KEY,
            agent_id INTEGER REFERENCES agents(id),
            response_quality DECIMAL(3,2),
            response_time_ms INTEGER,
            user_satisfaction INTEGER,
            query_complexity DECIMAL(3,2),
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS conversation_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) UNIQUE,
            agent_id INTEGER REFERENCES agents(id),
            user_query TEXT,
            agent_response TEXT,
            confidence_score DECIMAL(3,2),
            feedback_rating INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS agent_collaborations (
            id SERIAL PRIMARY KEY,
            primary_agent_id INTEGER REFERENCES agents(id),
            collaborating_agent_id INTEGER REFERENCES agents(id),
            collaboration_type VARCHAR(50),
            success_rate DECIMAL(3,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS learning_insights (
            id SERIAL PRIMARY KEY,
            insight_type VARCHAR(100),
            title VARCHAR(255),
            description TEXT,
            confidence_score DECIMAL(3,2),
            recommended_actions TEXT[],
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS agent_skills (
            id SERIAL PRIMARY KEY,
            agent_id INTEGER REFERENCES agents(id),
            skill_name VARCHAR(100),
            proficiency_score DECIMAL(3,2),
            improvement_rate DECIMAL(5,4),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS query_patterns (
            id SERIAL PRIMARY KEY,
            pattern_description TEXT,
            frequency INTEGER DEFAULT 1,
            avg_satisfaction DECIMAL(3,2),
            optimal_agents TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS experiments (
            id SERIAL PRIMARY KEY,
            experiment_name VARCHAR(255),
            description TEXT,
            variant_a_config JSONB,
            variant_b_config JSONB,
            status VARCHAR(50) DEFAULT 'active',
            significance_level DECIMAL(3,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS galileo_logs (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255),
            log_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(basic_schema)
                print("✅ Basic database schema created")
        except Exception as e:
            print(f"❌ Basic schema creation failed: {e}")
            raise

    async def seed_default_agents(self):
        """Insert default agents"""
        default_agents = [
            {
                'name': 'Technical Integration Specialist',
                'description': 'Expert in webhook implementations, API integrations, and technical troubleshooting',
                'domain': 'technical',
                'specialization_score': 0.95,
                'keywords': ['webhook', 'api', 'integration', 'technical', 'troubleshooting'],
                'avatar': '⚡',
                'color': 'blue'
            },
            {
                'name': 'Security & Compliance Expert',
                'description': 'Specializes in security protocols, authentication, and compliance requirements',
                'domain': 'security',
                'specialization_score': 0.92,
                'keywords': ['security', 'authentication', 'compliance', 'encryption', 'audit'],
                'avatar': '🔒',
                'color': 'red'
            },
            {
                'name': 'Performance Analytics Specialist',
                'description': 'Expert in monitoring, optimization, and performance analysis',
                'domain': 'analytics',
                'specialization_score': 0.88,
                'keywords': ['performance', 'monitoring', 'analytics', 'optimization', 'metrics'],
                'avatar': '📊',
                'color': 'green'
            },
            {
                'name': 'Customer Success Manager',
                'description': 'Handles escalations, customer relations, and business process optimization',
                'domain': 'customer_success',
                'specialization_score': 0.85,
                'keywords': ['customer', 'support', 'escalation', 'business', 'process'],
                'avatar': '🎯',
                'color': 'purple'
            }
        ]
        
        try:
            async with self.pool.acquire() as conn:
                for agent in default_agents:
                    await conn.execute("""
                        INSERT INTO agents (name, description, domain, specialization_score, keywords, avatar, color)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (name) DO NOTHING
                    """, agent['name'], agent['description'], agent['domain'], 
                    agent['specialization_score'], agent['keywords'], agent['avatar'], agent['color'])
                
                print("✅ Default agents seeded successfully")
        except Exception as e:
            print(f"❌ Agent seeding failed: {e}")

async def main():
    """Main setup function"""
    print("🚀 Setting up AgentCraft Database with Replit PostgreSQL...")
    print("=" * 60)
    
    # Check for DATABASE_URL
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL not found!")
        print("📝 To set up PostgreSQL in Replit:")
        print("   1. Click on 'Database' in the left sidebar")
        print("   2. Click 'Create Database'")
        print("   3. The DATABASE_URL will be automatically added to your environment")
        print("   4. Run this setup again")
        return False
    
    db_manager = DatabaseManager()
    
    try:
        # Initialize connection
        await db_manager.initialize()
        
        # Create tables
        await db_manager.create_tables()
        
        # Seed default data
        await db_manager.seed_default_agents()
        
        # Verify setup
        async with db_manager.pool.acquire() as conn:
            agent_count = await conn.fetchval("SELECT COUNT(*) FROM agents")
            table_count = await conn.fetchval("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            
            print(f"✅ Setup completed successfully!")
            print(f"   📊 {table_count} tables created")
            print(f"   🤖 {agent_count} agents initialized")
            print("🎉 AgentCraft database is ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    finally:
        await db_manager.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🚀 Next steps:")
        print("   1. Start your backend: python backend/main.py")
        print("   2. Your agents will now persist in the database!")
    else:
        print("\n❌ Setup incomplete. Please check the errors above.")
