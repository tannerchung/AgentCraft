
#!/usr/bin/env python3
"""
Quick setup script for Replit PostgreSQL database
"""

import os
import sys
import asyncio

def check_replit_database():
    """Check if Replit database is configured"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found!")
        print("\n📝 To set up PostgreSQL in Replit:")
        print("   1. Open the 'Database' tab in the left sidebar")
        print("   2. Click 'Create Database'")
        print("   3. Wait for the database to be created")
        print("   4. Run this script again")
        return False
    
    print(f"✅ Found DATABASE_URL: {database_url[:50]}...")
    return True

async def setup_database():
    """Run the database setup"""
    try:
        from database.setup import main as db_setup
        success = await db_setup()
        return success
    except ImportError:
        print("❌ Database setup module not found")
        print("Installing required dependencies...")
        
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "asyncpg", "psycopg2-binary"])
        
        from database.setup import main as db_setup
        success = await db_setup()
        return success

def main():
    """Main setup function"""
    print("🚀 AgentCraft Replit Database Setup")
    print("=" * 40)
    
    # Step 1: Check if database exists
    if not check_replit_database():
        return False
    
    # Step 2: Run database setup
    print("\n🔧 Setting up database schema and default agents...")
    success = asyncio.run(setup_database())
    
    if success:
        print("\n🎉 Database setup completed successfully!")
        print("🚀 You can now start AgentCraft with: python main.py")
    else:
        print("\n❌ Database setup failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
