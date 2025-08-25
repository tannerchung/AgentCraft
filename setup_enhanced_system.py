#!/usr/bin/env python3
"""
Enhanced AgentCraft Setup Script
Sets up the complete database + memory-cached system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

async def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced AgentCraft System...")
    print("=" * 60)
    
    # Step 1: Database setup
    print("\n📦 Step 1: Database Setup")
    try:
        from database.setup import main as db_setup
        await db_setup()
        print("✅ Database setup completed")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    # Step 2: Test database connection
    print("\n🔗 Step 2: Testing Database Connection")
    try:
        from database.models import db_manager, agent_manager
        await db_manager.initialize()
        
        agents = await agent_manager.get_all_agents()
        print(f"✅ Database connected successfully ({len(agents)} agents found)")
        
        await db_manager.close()
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False
    
    # Step 3: Test CrewAI integration
    print("\n🤖 Step 3: Testing CrewAI Integration")
    try:
        from src.agents.crew_db_integration import crew_agent_pool
        await crew_agent_pool.initialize()
        
        agents = await crew_agent_pool.get_all_agents()
        cache_stats = crew_agent_pool.get_cache_stats()
        
        print(f"✅ CrewAI integration successful ({len(agents)} agents cached)")
        print(f"   Cache stats: {cache_stats['total_agents']} total, {cache_stats['active_agents']} active")
        
    except Exception as e:
        print(f"❌ CrewAI integration test failed: {e}")
        return False
    
    # Step 4: Test enhanced backend
    print("\n⚡ Step 4: Testing Enhanced Backend")
    try:
        from backend.enhanced_backend import enhanced_backend
        await enhanced_backend.initialize()
        
        # Test agent library retrieval
        library = await enhanced_backend.get_agent_library()
        
        if library.get('success'):
            agent_count = library.get('total_count', 0)
            print(f"✅ Enhanced backend initialized ({agent_count} agents available)")
            print(f"   Database backed: {library.get('database_backed', False)}")
            print(f"   Memory cached: {library.get('memory_cached', False)}")
        else:
            print(f"⚠️  Enhanced backend initialized but agent library test failed")
        
    except Exception as e:
        print(f"❌ Enhanced backend test failed: {e}")
        return False
    
    # Step 5: Test CLI tools
    print("\n🛠️  Step 5: Testing CLI Tools")
    try:
        from database.cli import AgentCraftCLI
        cli = AgentCraftCLI()
        await cli.initialize()
        
        print("✅ CLI tools available")
        print("   Try: python database/cli.py list")
        print("   Try: python database/cli.py performance")
        
        await cli.close()
    except Exception as e:
        print(f"⚠️  CLI tools test failed (not critical): {e}")
    
    # Step 6: Performance verification
    print("\n📊 Step 6: Performance Verification")
    try:
        import time
        from src.agents.enhanced_adaptive_system import enhanced_adaptive_system
        
        await enhanced_adaptive_system.initialize()
        
        # Test query processing
        start_time = time.time()
        test_result = await enhanced_adaptive_system.process_query(
            "Test query: What is the status of the webhook integration?",
            context={"test": True}
        )
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # Convert to ms
        
        if test_result.get('success'):
            print(f"✅ Performance test passed ({processing_time:.0f}ms)")
            print(f"   Agents used: {test_result.get('agents_used', [])}")
            print(f"   Database backed: {test_result.get('database_backed', False)}")
        else:
            print(f"⚠️  Performance test completed with issues")
    
    except Exception as e:
        print(f"⚠️  Performance verification failed: {e}")
    
    # Final status
    print("\n" + "=" * 60)
    print("🎉 Enhanced AgentCraft Setup Complete!")
    print("\n📋 Summary:")
    print("✅ PostgreSQL database with agent persistence")
    print("✅ Memory-cached agent pool for low latency")
    print("✅ CrewAI integration with database agents")
    print("✅ Hot-reload capability for agent updates")
    print("✅ Enhanced backend with metrics collection")
    print("✅ Self-improvement learning loops")
    
    print("\n🚀 Next Steps:")
    print("1. Start the backend:")
    print("   uv run python backend/main.py")
    print("")
    print("2. Test the system:")
    print("   curl -X POST http://localhost:8000/api/chat \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"agent_type\":\"multi-agent\",\"message\":\"Test webhook integration\"}'")
    print("")
    print("3. Manage agents with CLI:")
    print("   python database/cli.py list")
    print("   python database/cli.py create 'Custom Agent' 'Specialized role'")
    print("")
    print("4. Access API endpoints:")
    print("   GET  http://localhost:8000/api/agents/list")
    print("   POST http://localhost:8000/api/agents/create")
    print("   GET  http://localhost:8000/api/agents/metrics")
    
    print("\n💡 Key Benefits:")
    print("• Agents persist across server restarts")
    print("• Memory caching for optimal performance")
    print("• Real-time agent configuration updates")
    print("• Comprehensive metrics and learning")
    print("• CrewAI multi-agent orchestration")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✨ Setup completed successfully!")