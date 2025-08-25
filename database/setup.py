#!/usr/bin/env python3
"""
Database setup and initialization script for AgentCraft
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from database/
sys.path.append(str(Path(__file__).parent.parent))

from database.models import db_manager

async def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    # Parse database URL
    db_url = os.getenv('DATABASE_URL', 'postgresql://agentcraft:agentcraft@localhost:5432/agentcraft')
    parts = db_url.split('/')
    db_name = parts[-1]
    admin_url = '/'.join(parts[:-1]) + '/postgres'  # Connect to postgres db first
    
    try:
        # Connect to postgres database to create agentcraft database
        conn = await asyncpg.connect(admin_url)
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not exists:
            # Create database
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✓ Created database: {db_name}")
        else:
            print(f"✓ Database already exists: {db_name}")
        
        await conn.close()
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

async def run_schema_migration():
    """Run the schema migration"""
    try:
        # Initialize database connection
        await db_manager.initialize()
        
        # Read schema file
        schema_path = Path(__file__).parent / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        async with db_manager.pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        print("✓ Schema migration completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error running schema migration: {e}")
        return False
    finally:
        await db_manager.close()

async def verify_setup():
    """Verify the database setup"""
    try:
        await db_manager.initialize()
        
        async with db_manager.pool.acquire() as conn:
            # Check agents table
            agent_count = await conn.fetchval("SELECT COUNT(*) FROM agents")
            print(f"✓ Agents table initialized with {agent_count} default agents")
            
            # Check other tables exist
            tables = await conn.fetch("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            table_names = [row['table_name'] for row in tables]
            expected_tables = [
                'agents', 'agent_metrics', 'conversation_sessions', 
                'agent_collaborations', 'learning_insights', 'agent_skills',
                'query_patterns', 'experiments', 'galileo_logs'
            ]
            
            missing_tables = set(expected_tables) - set(table_names)
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
            else:
                print(f"✓ All {len(expected_tables)} required tables created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False
    finally:
        await db_manager.close()

async def main():
    """Main setup function"""
    print("🚀 Setting up AgentCraft database...")
    
    # Step 1: Create database if needed
    if not await create_database_if_not_exists():
        sys.exit(1)
    
    # Step 2: Run schema migration
    if not await run_schema_migration():
        sys.exit(1)
    
    # Step 3: Verify setup
    if not await verify_setup():
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Start your backend server: uv run python backend/main.py")
    print("2. The agents will now persist across server restarts")
    print("3. Metrics will be collected for self-improvement loops")

if __name__ == "__main__":
    asyncio.run(main())