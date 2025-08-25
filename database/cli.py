#!/usr/bin/env python3
"""
AgentCraft Database CLI
Command-line tool for managing agents and viewing metrics
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from uuid import UUID

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import db_manager, agent_manager, metrics_manager, learning_manager

class AgentCraftCLI:
    """Command-line interface for AgentCraft database management"""
    
    async def initialize(self):
        """Initialize database connection"""
        await db_manager.initialize()
    
    async def close(self):
        """Close database connections"""
        await db_manager.close()
    
    async def list_agents(self):
        """List all agents"""
        agents = await agent_manager.get_all_agents()
        
        print(f"\n📋 AgentCraft Agents ({len(agents)} total)")
        print("=" * 80)
        
        for agent in agents:
            status = "✅ Active" if agent.get('is_active', True) else "❌ Inactive"
            print(f"🤖 {agent['name']} - {agent['domain'].title()} [{status}]")
            print(f"   Role: {agent['role']}")
            print(f"   Keywords: {', '.join(agent.get('keywords', []))}")
            print(f"   Specialization: {agent.get('specialization_score', 0.0):.2f}")
            print(f"   Collaboration: {agent.get('collaboration_rating', 0.0):.2f}")
            print(f"   ID: {agent['id']}")
            print()
    
    async def agent_performance(self, agent_name: str = None, days: int = 30):
        """Show agent performance metrics"""
        if agent_name:
            # Find agent by name
            agents = await agent_manager.get_all_agents()
            agent = next((a for a in agents if a['name'].lower() == agent_name.lower()), None)
            
            if not agent:
                print(f"❌ Agent '{agent_name}' not found")
                return
            
            performance = await metrics_manager.get_agent_performance_summary(agent['id'], days)
            
            print(f"\n📊 Performance Report: {agent['name']} (Last {days} days)")
            print("=" * 60)
            
            if performance.get('total_interactions', 0) == 0:
                print("No interactions recorded in the specified period.")
                return
            
            print(f"Total Interactions: {performance.get('total_interactions', 0)}")
            print(f"Average Quality: {performance.get('avg_quality', 0):.2f}/5")
            print(f"Average Response Time: {performance.get('avg_response_time', 0):.0f}ms")
            print(f"User Rating: {performance.get('avg_user_rating', 0):.1f}/5")
            print(f"Success Rate: {performance.get('success_rate', 0):.1%}")
            print(f"Average Cost: ${performance.get('avg_cost', 0):.4f}")
            
        else:
            # Show overall system performance
            agents = await agent_manager.get_all_agents()
            print(f"\n📊 System Performance Summary (Last {days} days)")
            print("=" * 80)
            
            total_agents = len(agents)
            active_agents = sum(1 for a in agents if a.get('is_active', True))
            
            print(f"Total Agents: {total_agents}")
            print(f"Active Agents: {active_agents}")
            print("\nTop Performing Agents:")
            print("-" * 40)
            
            # Show top 5 agents by interaction count
            performances = []
            for agent in agents[:5]:  # Limit to first 5 for demo
                perf = await metrics_manager.get_agent_performance_summary(agent['id'], days)
                if perf.get('total_interactions', 0) > 0:
                    performances.append((agent['name'], perf))
            
            performances.sort(key=lambda x: x[1].get('total_interactions', 0), reverse=True)
            
            for name, perf in performances:
                print(f"🤖 {name}: {perf.get('total_interactions', 0)} interactions, "
                      f"{perf.get('avg_quality', 0):.1f}/5 quality")
    
    async def create_agent(self, name: str, role: str, domain: str = "general",
                          keywords: str = "", avatar: str = "🤖", color: str = "blue"):
        """Create a new agent"""
        keyword_list = [k.strip() for k in keywords.split(',')] if keywords else []
        
        agent_data = {
            'name': name,
            'role': role,
            'domain': domain,
            'keywords': keyword_list,
            'avatar': avatar,
            'color': color,
            'backstory': f'You are a specialized agent focusing on {domain}-related tasks.',
            'goal': f'Provide excellent support for {domain} inquiries',
            'llm_config': {"model": "claude-3-5-sonnet", "temperature": 0.2}
        }
        
        try:
            agent_id = await agent_manager.create_agent(agent_data)
            print(f"✅ Created agent '{name}' with ID: {agent_id}")
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
    
    async def learning_insights(self, limit: int = 10):
        """Show learning insights"""
        insights = await learning_manager.get_pending_insights()
        
        print(f"\n🧠 Learning Insights ({len(insights)} pending)")
        print("=" * 80)
        
        if not insights:
            print("No pending insights. System is learning from interactions...")
            return
        
        for insight in insights[:limit]:
            print(f"💡 {insight['title']}")
            print(f"   Type: {insight['insight_type']}")
            print(f"   Confidence: {insight['confidence_score']:.1%}")
            print(f"   Data Points: {insight['data_points']}")
            print(f"   Description: {insight['description']}")
            print(f"   Created: {insight['created_at'].strftime('%Y-%m-%d %H:%M')}")
            print()
    
    async def query_patterns(self, limit: int = 10):
        """Show query patterns analysis"""
        patterns = await metrics_manager.analyze_query_patterns(limit)
        
        print(f"\n🔍 Query Patterns Analysis (Top {limit})")
        print("=" * 80)
        
        if not patterns:
            print("No query patterns recorded yet.")
            return
        
        for pattern in patterns:
            print(f"📊 {pattern['pattern_description'] or 'Unknown Pattern'}")
            print(f"   Frequency: {pattern['frequency']} occurrences")
            print(f"   Avg Response Time: {pattern.get('avg_response_time_ms', 0):.0f}ms")
            print(f"   Avg Satisfaction: {pattern.get('avg_satisfaction', 0):.1f}/5")
            if pattern.get('optimal_agents'):
                agents = ', '.join(pattern['optimal_agents'])
                print(f"   Best Agents: {agents}")
            print(f"   Last Seen: {pattern['last_seen'].strftime('%Y-%m-%d %H:%M')}")
            print()

async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='AgentCraft Database CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List agents command
    list_parser = subparsers.add_parser('list', help='List all agents')
    
    # Performance command
    perf_parser = subparsers.add_parser('performance', help='Show performance metrics')
    perf_parser.add_argument('--agent', help='Specific agent name')
    perf_parser.add_argument('--days', type=int, default=30, help='Days to analyze (default: 30)')
    
    # Create agent command
    create_parser = subparsers.add_parser('create', help='Create new agent')
    create_parser.add_argument('name', help='Agent name')
    create_parser.add_argument('role', help='Agent role description')
    create_parser.add_argument('--domain', default='general', help='Agent domain')
    create_parser.add_argument('--keywords', default='', help='Comma-separated keywords')
    create_parser.add_argument('--avatar', default='🤖', help='Agent avatar emoji')
    create_parser.add_argument('--color', default='blue', help='Agent color')
    
    # Learning insights command
    insights_parser = subparsers.add_parser('insights', help='Show learning insights')
    insights_parser.add_argument('--limit', type=int, default=10, help='Number of insights to show')
    
    # Query patterns command
    patterns_parser = subparsers.add_parser('patterns', help='Show query patterns')
    patterns_parser.add_argument('--limit', type=int, default=10, help='Number of patterns to show')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AgentCraftCLI()
    
    try:
        await cli.initialize()
        
        if args.command == 'list':
            await cli.list_agents()
        elif args.command == 'performance':
            await cli.agent_performance(args.agent, args.days)
        elif args.command == 'create':
            await cli.create_agent(args.name, args.role, args.domain, 
                                 args.keywords, args.avatar, args.color)
        elif args.command == 'insights':
            await cli.learning_insights(args.limit)
        elif args.command == 'patterns':
            await cli.query_patterns(args.limit)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await cli.close()

if __name__ == "__main__":
    asyncio.run(main())