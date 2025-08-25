"""
CrewAI Database Integration
Memory-cached agent loader with PostgreSQL persistence
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import threading
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from database.models import agent_manager, db_manager
from src.agents.crewai_log_streamer import crewai_log_streamer

# CrewAI imports with fallback
try:
    from crewai import Agent, Task, Crew
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    Agent = Task = Crew = BaseTool = None

logger = logging.getLogger(__name__)

class DatabaseCrewAgent:
    """CrewAI Agent wrapper with database persistence"""
    
    def __init__(self, db_agent_data: Dict):
        self.db_data = db_agent_data
        self.id = db_agent_data['id']
        self.name = db_agent_data['name']
        self.role = db_agent_data['role']
        self.backstory = db_agent_data.get('backstory', '')
        self.goal = db_agent_data.get('goal', '')
        
        # Parse JSON fields that might be strings
        self.keywords = self._parse_json_field(db_agent_data.get('keywords'), [])
        self.llm_config = self._parse_json_field(db_agent_data.get('llm_config'), {})
        self.tools = self._parse_json_field(db_agent_data.get('tools'), [])
        
        self.domain = db_agent_data.get('domain', 'general')
        self.avatar = db_agent_data.get('avatar', '🤖')
        self.color = db_agent_data.get('color', 'blue')
        
        # Performance metrics
        self.specialization_score = db_agent_data.get('specialization_score', 0.0)
        self.collaboration_rating = db_agent_data.get('collaboration_rating', 0.0)
        
        # CrewAI agent instance (lazy loaded)
        self._crew_agent = None
        self.last_updated = db_agent_data.get('updated_at', time.time())
    
    def _parse_json_field(self, field_value, default_value):
        """Parse JSON field that might be a string or already parsed"""
        if field_value is None:
            return default_value
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON field: {field_value}")
                return default_value
        
        # Already parsed or correct type
        return field_value
    
    def _enhance_backstory_for_delegation(self) -> str:
        """Enhance backstory with comprehensive response guidelines"""
        base_backstory = self.backstory or f"You are a {self.role} with expertise in {self.domain}."
        
        enhanced_instructions = f"""

## CRITICAL RESPONSE GUIDELINES:
You MUST provide specific, actionable solutions directly addressing the user's exact query.

### Your Analysis Process:
1. **Identify Exact Problem**: What specific issue is the user facing?
2. **Provide Direct Solution**: Give concrete steps to fix THIS specific issue
3. **Be Actionable**: Include specific commands, configurations, or code when relevant
4. **Address Root Cause**: Explain what likely caused this specific problem
5. **Verification Steps**: How to test that the fix works

### Response Format Template:
```
## Problem Analysis
[What exactly is wrong based on the user's query]

## Solution Steps  
1. [First specific action to take]
2. [Second specific action]
3. [Additional steps as needed]

## Why This Happened
[Root cause explanation]

## Testing the Fix
[How to verify it's resolved]
```

### Domain Expertise - {self.domain.title()}:
{self._get_domain_specific_guidance()}

### Delegation Protocol:
Only delegate if you need expertise outside your domain. Format:
- task: "specific technical task"
- context: "relevant details"  
- coworker: "exact specialist role name"

Use simple strings only, NOT objects. Delegate examples:
- Technical issues → "Technical Integration Specialist" 
- Security concerns → "Security Specialist"
- Database problems → "Database Expert"
- Infrastructure → "DevOps Engineer"
- Billing/payments → "Billing & Revenue Expert"

ALWAYS provide your expert analysis first, then delegate only if additional expertise is truly needed."""

        return base_backstory + enhanced_instructions
    
    def _get_domain_specific_guidance(self) -> str:
        """Get domain-specific response guidance"""
        domain_guidance = {
            'technical': '''
- Check configuration files (.env, config.json, etc.)
- Verify API endpoints and authentication credentials
- Test connectivity with curl commands or similar tools
- Review error logs for specific error messages
- Provide working code examples or configuration snippets
- Check SSL certificates, webhook URLs, timeout settings''',
            
            'security': '''
- Assess authentication mechanisms (API keys, OAuth, JWT)
- Check authorization and access controls
- Review encryption and secure protocols (HTTPS, TLS)
- Identify specific vulnerabilities and their severity
- Provide exact security configuration examples
- Suggest compliance measures (GDPR, SOC2, etc.)''',
            
            'business': '''
- Calculate financial impact and resolution costs
- Consider compliance and legal requirements
- Provide timeline estimates for solutions
- Suggest process improvements to prevent recurrence
- Include business justification for technical changes
- Account for user experience and customer impact''',
            
            'orchestration': '''
- Coordinate between different technical domains
- Prioritize actions by business impact and urgency
- Ensure all aspects of the problem are addressed
- Synthesize multi-domain solutions into coherent plan
- Manage dependencies between different solution steps''',
            
            'analysis': '''
- Gather specific data points and metrics
- Compare alternatives with clear trade-offs
- Provide evidence-based recommendations
- Include competitive benchmarking when relevant
- Present findings with supporting examples and data
- Focus on actionable insights rather than theory'''
        }
        
        return domain_guidance.get(self.domain, 'Provide specific, actionable guidance relevant to your expertise area.')
    
    @property
    def crew_agent(self) -> Optional[Agent]:
        """Get or create the CrewAI Agent instance"""
        if not CREWAI_AVAILABLE:
            logger.warning("CrewAI not available, cannot create agent")
            return None
        
        if self._crew_agent is None:
            try:
                # Determine LLM from config
                llm_model = self.llm_config.get('model', 'gpt-3.5-turbo')
                
                # Create CrewAI agent with enhanced prompting for delegation
                enhanced_backstory = self._enhance_backstory_for_delegation()
                
                self._crew_agent = Agent(
                    role=self.role,
                    goal=self.goal,
                    backstory=enhanced_backstory,
                    verbose=True,
                    allow_delegation=True,  # Re-enable delegation with better prompts
                    tools=self._load_tools(),
                    llm=self._get_llm_instance(llm_model)
                )
                
                # Add metadata for tracking
                self._crew_agent._db_id = self.id
                self._crew_agent._db_name = self.name
                self._crew_agent._domain = self.domain
                
                logger.info(f"Created CrewAI agent: {self.name}")
                
            except Exception as e:
                logger.error(f"Failed to create CrewAI agent for {self.name}: {e}")
                return None
        
        return self._crew_agent
    
    def _load_tools(self) -> List:
        """Load tools for this agent"""
        # TODO: Implement tool loading from database
        # For now, return empty list
        return []
    
    def _get_llm_instance(self, model_name: str):
        """Get LLM instance based on model name"""
        # This would integrate with your LLM selection system
        # For now, return None to use default
        return None
    
    def invalidate_cache(self):
        """Invalidate the cached CrewAI agent to force reload"""
        self._crew_agent = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'id': str(self.id),
            'name': self.name,
            'role': self.role,
            'backstory': self.backstory,
            'goal': self.goal,
            'keywords': self.keywords,
            'llm_config': self.llm_config,
            'tools': self.tools,
            'domain': self.domain,
            'avatar': self.avatar,
            'color': self.color,
            'specialization_score': self.specialization_score,
            'collaboration_rating': self.collaboration_rating
        }

class CrewAIAgentPool:
    """Memory-cached agent pool with database persistence"""
    
    def __init__(self, cache_ttl: int = 300):  # 5 minute cache TTL
        self.cache_ttl = cache_ttl
        self.agents_cache: Dict[str, DatabaseCrewAgent] = {}
        self.agents_by_id: Dict[UUID, DatabaseCrewAgent] = {}
        self.last_refresh = 0
        self.refresh_lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.initialized = False
    
    async def initialize(self):
        """Initialize the agent pool"""
        if not self.initialized:
            await db_manager.initialize()
            await self.refresh_agents()
            self.initialized = True
            logger.info("CrewAI Agent Pool initialized")
    
    async def refresh_agents(self, force: bool = False):
        """Refresh agents from database"""
        current_time = time.time()
        
        with self.refresh_lock:
            if not force and current_time - self.last_refresh < self.cache_ttl:
                return  # Cache still valid
            
            try:
                # Load all agents from database
                db_agents = await agent_manager.get_all_agents()
                
                # Clear old cache
                old_cache = self.agents_cache.copy()
                self.agents_cache.clear()
                self.agents_by_id.clear()
                
                # Create new agent instances
                for agent_data in db_agents:
                    if not agent_data.get('is_active', True):
                        continue  # Skip inactive agents
                    
                    db_agent = DatabaseCrewAgent(agent_data)
                    
                    # Check if we can reuse existing CrewAI instance
                    old_agent = old_cache.get(db_agent.name)
                    if (old_agent and 
                        old_agent.last_updated == db_agent.last_updated and
                        old_agent._crew_agent is not None):
                        # Reuse existing CrewAI agent instance
                        db_agent._crew_agent = old_agent._crew_agent
                    
                    self.agents_cache[db_agent.name] = db_agent
                    self.agents_by_id[db_agent.id] = db_agent
                
                self.last_refresh = current_time
                logger.info(f"Refreshed {len(self.agents_cache)} agents from database")
                
            except Exception as e:
                logger.error(f"Failed to refresh agents from database: {e}")
                raise
    
    async def get_agent(self, name: str) -> Optional[DatabaseCrewAgent]:
        """Get agent by name with automatic cache refresh"""
        await self._ensure_fresh_cache()
        return self.agents_cache.get(name)
    
    async def get_agent_by_id(self, agent_id: UUID) -> Optional[DatabaseCrewAgent]:
        """Get agent by ID with automatic cache refresh"""
        await self._ensure_fresh_cache()
        return self.agents_by_id.get(agent_id)
    
    async def get_all_agents(self) -> Dict[str, DatabaseCrewAgent]:
        """Get all cached agents"""
        await self._ensure_fresh_cache()
        return self.agents_cache.copy()
    
    async def get_agents_by_domain(self, domain: str) -> List[DatabaseCrewAgent]:
        """Get agents by domain"""
        await self._ensure_fresh_cache()
        return [agent for agent in self.agents_cache.values() 
                if agent.domain == domain]
    
    async def get_agents_by_keywords(self, keywords: List[str]) -> List[DatabaseCrewAgent]:
        """Get agents that match any of the given keywords"""
        await self._ensure_fresh_cache()
        
        matching_agents = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for agent in self.agents_cache.values():
            agent_keywords = [kw.lower() for kw in agent.keywords]
            if any(kw in agent_keywords for kw in keywords_lower):
                matching_agents.append(agent)
        
        # Sort by specialization score descending
        matching_agents.sort(key=lambda a: a.specialization_score, reverse=True)
        return matching_agents
    
    async def create_crew(self, agent_names: List[str], tasks: List[Dict]) -> Optional['Crew']:
        """Create a CrewAI Crew from database agents"""
        if not CREWAI_AVAILABLE:
            logger.error("CrewAI not available")
            return None
        
        await self._ensure_fresh_cache()
        
        # Get agents
        agents = []
        for name in agent_names:
            db_agent = self.agents_cache.get(name)
            if db_agent and db_agent.crew_agent:
                agents.append(db_agent.crew_agent)
            else:
                logger.warning(f"Agent not found or failed to create: {name}")
        
        if not agents:
            logger.error("No valid agents found for crew creation")
            return None
        
        # Create tasks
        crew_tasks = []
        for i, task_data in enumerate(tasks):
            task = Task(
                description=task_data.get('description', f'Task {i+1}'),
                agent=agents[i % len(agents)],  # Round-robin assignment
                expected_output=task_data.get('expected_output', 'Task completion')
            )
            crew_tasks.append(task)
        
        # Create crew
        try:
            # Try to set up hierarchical process with manager LLM
            crew_config = {
                "agents": agents,
                "tasks": crew_tasks,
                "verbose": True,
                "memory": True
            }
            
            try:
                # For hierarchical process, we need a manager LLM
                from langchain_openai import ChatOpenAI
                manager_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
                
                crew_config.update({
                    "process": "hierarchical",
                    "manager_llm": manager_llm
                })
                logger.info("Using hierarchical process with manager LLM")
                
            except ImportError as e:
                logger.warning(f"Could not import langchain_openai: {e}, using sequential process")
                crew_config.update({
                    "process": "sequential",
                    "max_iter": 2  # Allow iterations for collaboration
                })
            
            crew = Crew(**crew_config)
            
            logger.info(f"Created crew with {len(agents)} agents and {len(crew_tasks)} tasks")
            return crew
            
        except Exception as e:
            logger.error(f"Failed to create crew: {e}")
            return None
    
    async def invalidate_agent(self, name: str):
        """Invalidate specific agent cache"""
        agent = self.agents_cache.get(name)
        if agent:
            agent.invalidate_cache()
            logger.info(f"Invalidated cache for agent: {name}")
    
    async def hot_reload_agent(self, agent_id: UUID):
        """Hot reload a specific agent from database"""
        try:
            # Get updated agent data from database
            updated_data = await agent_manager.get_agent_by_id(agent_id)
            if not updated_data:
                logger.warning(f"Agent {agent_id} not found in database")
                return
            
            # Create new agent instance
            new_agent = DatabaseCrewAgent(updated_data)
            
            # Update caches
            with self.refresh_lock:
                # Remove old instance
                old_agent = self.agents_by_id.get(agent_id)
                if old_agent:
                    self.agents_cache.pop(old_agent.name, None)
                
                # Add new instance
                self.agents_cache[new_agent.name] = new_agent
                self.agents_by_id[new_agent.id] = new_agent
            
            logger.info(f"Hot reloaded agent: {new_agent.name}")
            
        except Exception as e:
            logger.error(f"Failed to hot reload agent {agent_id}: {e}")
    
    async def _ensure_fresh_cache(self):
        """Ensure cache is fresh, refresh if needed"""
        current_time = time.time()
        if current_time - self.last_refresh > self.cache_ttl:
            await self.refresh_agents()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_agents': len(self.agents_cache),
            'active_agents': sum(1 for a in self.agents_cache.values() 
                               if a._crew_agent is not None),
            'last_refresh': self.last_refresh,
            'cache_age_seconds': time.time() - self.last_refresh,
            'cache_ttl': self.cache_ttl
        }

class DatabaseCrewAIOrchestrator:
    """Main orchestrator that combines database agents with CrewAI"""
    
    def __init__(self):
        self.agent_pool = CrewAIAgentPool()
        self.initialized = False
    
    async def initialize(self):
        """Initialize the orchestrator"""
        await self.agent_pool.initialize()
        self.initialized = True
        logger.info("Database CrewAI Orchestrator initialized")
    
    async def process_query(self, query: str, context: Dict = None) -> Dict:
        """Process query using database agents and CrewAI"""
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized")
        
        try:
            start_time = time.time()
            
            # Extract keywords for agent selection
            keywords = self._extract_keywords(query)
            
            # Select appropriate agents
            selected_agents = await self._select_agents(keywords, query)
            
            if not selected_agents:
                return {
                    'success': False,
                    'error': 'No suitable agents found',
                    'response': 'I could not find appropriate agents to handle your request.'
                }
            
            # Create tasks for the agents
            tasks = self._create_tasks(query, selected_agents, context)
            
            # Create and execute crew
            crew = await self.agent_pool.create_crew(
                [agent.name for agent in selected_agents],
                tasks
            )
            
            if not crew:
                return {
                    'success': False,
                    'error': 'Failed to create crew',
                    'response': 'I encountered an issue setting up the agent team.'
                }
            
            # Set session ID for log streaming
            session_id = f"crew_{int(time.time())}"
            crewai_log_streamer.set_session_id(session_id)
            
            # Log crew execution start
            crewai_log_streamer.log_crewai_event(
                "crew_execution_start", 
                f"Starting crew execution with {len(crew.agents)} agents",
                {
                    "agent_count": len(crew.agents),
                    "task_count": len(crew.tasks),
                    "query": query[:100]
                }
            )
            
            # Execute the crew (run in thread to avoid blocking)
            result = await asyncio.get_event_loop().run_in_executor(
                None, crew.kickoff
            )
            
            # Log crew execution completion
            crewai_log_streamer.log_crewai_event(
                "crew_execution_complete",
                f"Crew execution completed successfully",
                {
                    "result_length": len(str(result)),
                    "processing_time": time.time() - start_time
                }
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            return {
                'success': True,
                'response': str(result),
                'agents_used': [agent.name for agent in selected_agents],
                'processing_time': f"{processing_time:.2f}s",
                'database_backed': True,
                'crew_execution': True
            }
            
        except Exception as e:
            logger.error(f"Error in CrewAI orchestration: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': f'I encountered an error: {str(e)}'
            }
    
    async def _select_agents(self, keywords: List[str], query: str) -> List[DatabaseCrewAgent]:
        """Select optimal agents for the query"""
        # Get agents by keywords
        keyword_agents = await self.agent_pool.get_agents_by_keywords(keywords)
        
        # Always include orchestrator if available
        orchestrator = await self.agent_pool.get_agent("Orchestration Agent")
        selected = []
        
        if orchestrator:
            selected.append(orchestrator)
        
        # Add specialized agents (up to 2 more)
        for agent in keyword_agents[:2]:
            if agent not in selected:
                selected.append(agent)
        
        # Fallback to technical agent if no matches
        if len(selected) <= 1:
            technical = await self.agent_pool.get_agent("Technical Integration Specialist")
            if technical and technical not in selected:
                selected.append(technical)
        
        return selected
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        query_lower = query.lower()
        
        # Common domain keywords
        domain_keywords = {
            'technical': ['api', 'webhook', 'integration', 'ssl', 'certificate', 'error', 'bug'],
            'billing': ['payment', 'billing', 'subscription', 'invoice', 'refund', 'charge'],
            'security': ['security', 'vulnerability', 'breach', 'hack', 'compliance', 'audit'],
            'database': ['database', 'sql', 'query', 'migration', 'performance', 'timeout'],
            'competitive': ['competitor', 'competitive', 'market', 'analysis', 'compare'],
            'support': ['help', 'support', 'issue', 'problem', 'trouble', 'assist']
        }
        
        extracted = []
        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                extracted.extend(keywords)
        
        # Add words from query
        words = [w.strip('.,!?()[]"\'') for w in query_lower.split() if len(w) > 3]
        extracted.extend(words)
        
        return list(set(extracted))  # Remove duplicates
    
    def _create_tasks(self, query: str, agents: List[DatabaseCrewAgent], 
                     context: Dict = None) -> List[Dict]:
        """Create specific, actionable tasks for the selected agents"""
        tasks = []
        
        if len(agents) == 1:
            # Single agent task with specific instructions
            tasks.append({
                'description': f'''Analyze this user query and provide a specific, actionable solution:

USER QUERY: "{query}"

Requirements:
1. Identify the exact problem described in the query
2. Provide step-by-step solution instructions  
3. Include specific commands, configurations, or code examples
4. Explain the root cause
5. Provide verification steps

Format your response with clear sections:
- Problem Analysis
- Solution Steps (numbered list)
- Why This Happened
- Testing the Fix''',
                'expected_output': 'A structured response with specific problem analysis, step-by-step solution, root cause explanation, and verification steps'
            })
        else:
            # Multi-agent tasks with role-specific instructions
            for i, agent in enumerate(agents):
                if i == 0:  # First agent (usually orchestrator)
                    tasks.append({
                        'description': f'''As the orchestrating agent, analyze this query and provide an initial comprehensive response:

USER QUERY: "{query}"

Your responsibilities:
1. Identify all aspects of the problem
2. Provide initial solution steps
3. Determine if specialist input is needed
4. Coordinate the overall response

If you need specialist expertise, clearly delegate specific tasks to appropriate team members.''',
                        'expected_output': 'Comprehensive initial analysis with clear solution steps, and delegation requests if specialist expertise is needed'
                    })
                else:  # Specialist agents
                    tasks.append({
                        'description': f'''Provide expert {agent.domain} analysis and solutions for:

USER QUERY: "{query}"

Your {agent.domain} expertise should focus on:
1. {agent.domain}-specific aspects of this problem
2. Detailed technical solutions within your domain
3. Specific tools, commands, or configurations to use
4. Best practices for prevention
5. Testing and validation approaches

Provide actionable, implementable solutions.''',
                        'expected_output': f'Expert {agent.domain} analysis with specific, actionable solutions, technical details, and implementation guidance'
                    })
        
        return tasks
    
    async def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        agents = await self.agent_pool.get_all_agents()
        cache_stats = self.agent_pool.get_cache_stats()
        
        return {
            'total_agents': len(agents),
            'agents_by_domain': self._group_agents_by_domain(agents),
            'cache_stats': cache_stats,
            'crewai_available': CREWAI_AVAILABLE
        }
    
    def _group_agents_by_domain(self, agents: Dict[str, DatabaseCrewAgent]) -> Dict:
        """Group agents by domain"""
        domains = {}
        for agent in agents.values():
            domain = agent.domain
            if domain not in domains:
                domains[domain] = []
            domains[domain].append({
                'name': agent.name,
                'specialization_score': agent.specialization_score,
                'collaboration_rating': agent.collaboration_rating
            })
        return domains

# Global instances
crew_agent_pool = CrewAIAgentPool()
database_crew_orchestrator = DatabaseCrewAIOrchestrator()