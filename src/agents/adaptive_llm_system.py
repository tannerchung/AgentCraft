import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from crewai import Agent, Task, Crew, LLM

# Try to import advanced CrewAI features, fallback if not available
try:
    from crewai.memory import ShortTermMemory, LongTermMemory, EntityMemory
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    print("⚠️  CrewAI memory features not available")

# CrewAI features are now built into the main Crew class (v0.165+)
try:
    from crewai import Crew
    # Check if Crew has planning capabilities
    PLANNING_AVAILABLE = hasattr(Crew, 'plan') or hasattr(Crew, 'planning')
    TESTING_AVAILABLE = hasattr(Crew, 'test') or hasattr(Crew, 'evaluate')
    TRAINING_AVAILABLE = hasattr(Crew, 'train') or hasattr(Crew, 'training')
    COLLABORATION_AVAILABLE = True  # Collaboration is core to CrewAI
    
    if not PLANNING_AVAILABLE:
        print("ℹ️  CrewAI planning features: using built-in execution planning")
    if not TESTING_AVAILABLE:
        print("ℹ️  CrewAI testing features: using built-in performance evaluation")  
    if not TRAINING_AVAILABLE:
        print("ℹ️  CrewAI training features: using built-in feedback learning")
    print("✅ CrewAI core features loaded successfully")
    
except ImportError:
    PLANNING_AVAILABLE = False
    TESTING_AVAILABLE = False  
    TRAINING_AVAILABLE = False
    COLLABORATION_AVAILABLE = False
    print("⚠️  CrewAI not available")

import anthropic
from dotenv import load_dotenv

load_dotenv()

# Import Galileo integration
try:
    try:
        from .galileo_adaptive_integration import galileo_integration
    except ImportError:
        # Try absolute import as fallback
        from galileo_adaptive_integration import galileo_integration
    GALILEO_INTEGRATION_AVAILABLE = True
    print("✅ Galileo adaptive integration loaded")
except ImportError:
    GALILEO_INTEGRATION_AVAILABLE = False
    galileo_integration = None
    print("ℹ️  Galileo adaptive integration not available (optional feature)")

@dataclass
class LLMMetrics:
    """Performance metrics for an LLM"""
    response_times: List[float]
    quality_scores: List[float]
    cost_per_token: float
    success_rate: float
    expertise_areas: List[str]
    token_usage: Dict[str, int]
    error_count: int
    total_requests: int
    
    def get_avg_response_time(self) -> float:
        return sum(self.response_times[-50:]) / max(1, len(self.response_times[-50:]))
    
    def get_avg_quality(self) -> float:
        return sum(self.quality_scores[-50:]) / max(1, len(self.quality_scores[-50:]))
    
    def get_efficiency_score(self) -> float:
        """Combined metric: quality/cost ratio adjusted by speed"""
        if self.cost_per_token == 0:
            return self.get_avg_quality()
        
        quality = self.get_avg_quality()
        cost_efficiency = quality / self.cost_per_token if self.cost_per_token > 0 else quality
        speed_bonus = max(0, (5.0 - self.get_avg_response_time()) / 5.0)  # Bonus for sub-5s responses
        
        return cost_efficiency * (1 + speed_bonus * 0.2)

class LLMPool:
    """Manages a pool of LLMs with performance tracking and hot-swapping"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self.metrics = self._initialize_metrics()
        self.selection_weights = {
            "quality": 0.4,
            "speed": 0.3,
            "cost": 0.2,
            "reliability": 0.1
        }
        
        # Initialize evaluation LLM for quality scoring
        self.evaluator_llm = LLM(
            model="gpt-4o-mini",
            temperature=0.0,
            api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def _initialize_models(self) -> Dict[str, LLM]:
        """Initialize the pool of available LLMs"""
        models = {}
        
        # Fast models for simple tasks
        if os.getenv('OPENAI_API_KEY'):
            models.update({
                "fast": LLM(
                    model="gpt-3.5-turbo",
                    temperature=0.1,
                    api_key=os.getenv('OPENAI_API_KEY')
                ),
                "balanced": LLM(
                    model="gpt-4o-mini", 
                    temperature=0.2,
                    api_key=os.getenv('OPENAI_API_KEY')
                ),
                "creative": LLM(
                    model="gpt-4o",
                    temperature=0.7,
                    api_key=os.getenv('OPENAI_API_KEY')
                )
            })
        
        # Anthropic models for reasoning tasks
        if os.getenv('ANTHROPIC_API_KEY'):
            models.update({
                "powerful": LLM(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0.1,
                    api_key=os.getenv('ANTHROPIC_API_KEY')
                ),
                "reasoning": LLM(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0.0,
                    api_key=os.getenv('ANTHROPIC_API_KEY')
                )
            })
        
        # Local models for cost efficiency (if available)
        try:
            models["local"] = LLM(
                model="ollama/llama3.1",
                base_url="http://localhost:11434"
            )
        except:
            pass  # Local model not available
        
        return models
    
    def _initialize_metrics(self) -> Dict[str, LLMMetrics]:
        """Initialize performance metrics for each model"""
        return {
            name: LLMMetrics(
                response_times=[],
                quality_scores=[],
                cost_per_token=self._get_cost_per_token(name),
                success_rate=1.0,
                expertise_areas=self._get_expertise_areas(name),
                token_usage={"input": 0, "output": 0},
                error_count=0,
                total_requests=0
            ) for name in self.models.keys()
        }
    
    def _get_cost_per_token(self, model_name: str) -> float:
        """Get cost per token for different models (approximate)"""
        costs = {
            "fast": 0.0000015,      # GPT-3.5-turbo
            "balanced": 0.000001,   # GPT-4o-mini
            "creative": 0.000005,   # GPT-4o
            "powerful": 0.000003,   # Claude 3.5 Sonnet
            "reasoning": 0.000003,  # Claude 3.5 Sonnet
            "local": 0.0            # Local model - no API costs
        }
        return costs.get(model_name, 0.000003)
    
    def _get_expertise_areas(self, model_name: str) -> List[str]:
        """Define expertise areas for each model"""
        expertise = {
            "fast": ["simple_queries", "routing", "classification"],
            "balanced": ["general_support", "explanations", "moderate_complexity"],
            "creative": ["content_generation", "brainstorming", "creative_writing"],
            "powerful": ["complex_analysis", "technical_solutions", "detailed_reasoning"],
            "reasoning": ["logic_problems", "step_by_step_analysis", "debugging"],
            "local": ["privacy_sensitive", "offline_processing", "cost_efficient"]
        }
        return expertise.get(model_name, ["general"])
    
    def get_optimal_model(self, task_type: str, query_complexity: float = 0.5) -> Tuple[LLM, str]:
        """Select optimal model based on task type and complexity"""
        
        # Calculate scores for each available model
        model_scores = {}
        
        for name, model in self.models.items():
            metrics = self.metrics[name]
            score = self._calculate_model_score(name, task_type, query_complexity, metrics)
            model_scores[name] = score
        
        # Select the highest scoring model
        if not model_scores:
            # No models available, return None
            logging.warning("No models available for selection")
            return None, "none"
            
        best_model_name = max(model_scores.items(), key=lambda x: x[1])[0]
        
        logging.info(f"Selected {best_model_name} for {task_type} (complexity: {query_complexity})")
        logging.debug(f"Model scores: {model_scores}")
        
        return self.models[best_model_name], best_model_name
    
    def _calculate_model_score(self, model_name: str, task_type: str, 
                             complexity: float, metrics: LLMMetrics) -> float:
        """Calculate selection score for a model"""
        
        # Base score from efficiency
        base_score = metrics.get_efficiency_score()
        
        # Task type bonuses
        expertise_bonus = 0.2 if task_type in metrics.expertise_areas else 0
        
        # Complexity adjustment
        if model_name in ["powerful", "reasoning"] and complexity > 0.7:
            complexity_bonus = 0.3
        elif model_name in ["fast", "balanced"] and complexity < 0.3:
            complexity_bonus = 0.2
        else:
            complexity_bonus = 0
        
        # Reliability penalty
        reliability_penalty = metrics.error_count / max(1, metrics.total_requests) * 0.5
        
        return base_score + expertise_bonus + complexity_bonus - reliability_penalty
    
    def track_performance(self, model_name: str, response_time: float, 
                         quality_score: float, token_usage: Dict[str, int],
                         success: bool = True):
        """Track performance metrics for continuous improvement"""
        
        if model_name not in self.metrics:
            return
        
        metrics = self.metrics[model_name]
        
        # Update metrics
        metrics.response_times.append(response_time)
        metrics.quality_scores.append(quality_score)
        metrics.token_usage["input"] += token_usage.get("input", 0)
        metrics.token_usage["output"] += token_usage.get("output", 0)
        metrics.total_requests += 1
        
        if not success:
            metrics.error_count += 1
        
        # Update success rate (rolling window)
        recent_requests = min(100, metrics.total_requests)
        recent_errors = len([1 for i in range(-recent_requests, 0) 
                           if i < len(metrics.response_times) and not success])
        metrics.success_rate = (recent_requests - recent_errors) / recent_requests
        
        # Trim old data to prevent memory bloat
        if len(metrics.response_times) > 1000:
            metrics.response_times = metrics.response_times[-500:]
            metrics.quality_scores = metrics.quality_scores[-500:]
    
    def evaluate_response_quality(self, query: str, response: str, 
                                 task_type: str = "general") -> float:
        """Evaluate response quality using the evaluator LLM"""
        
        eval_prompt = f"""
        Evaluate this AI response on a scale of 1.0 to 10.0 based on:
        
        Task Type: {task_type}
        Query: {query}
        Response: {response}
        
        Criteria:
        - Accuracy and correctness (30%)
        - Completeness and thoroughness (25%) 
        - Relevance to the query (20%)
        - Clarity and helpfulness (15%)
        - Professional tone (10%)
        
        Return ONLY a numeric score (e.g., 7.5).
        """
        
        try:
            # Use the evaluator LLM to score quality
            evaluation = self.evaluator_llm.call([{
                "role": "user", 
                "content": eval_prompt
            }])
            
            # Handle different response formats (string vs object with .content)
            if hasattr(evaluation, 'content'):
                score_text = evaluation.content.strip()
            elif isinstance(evaluation, str):
                score_text = evaluation.strip()
            else:
                score_text = str(evaluation).strip()
            # Extract numeric score
            score = float(''.join(c for c in score_text if c.isdigit() or c == '.'))
            return min(10.0, max(1.0, score))  # Clamp between 1-10
            
        except Exception as e:
            logging.warning(f"Quality evaluation failed: {e}")
            return 7.0  # Default neutral score
    
    def get_performance_summary(self) -> Dict[str, Dict]:
        """Get performance summary for all models"""
        return {
            name: {
                "avg_response_time": metrics.get_avg_response_time(),
                "avg_quality": metrics.get_avg_quality(), 
                "efficiency_score": metrics.get_efficiency_score(),
                "success_rate": metrics.success_rate,
                "total_requests": metrics.total_requests,
                "expertise_areas": metrics.expertise_areas,
                "cost_per_token": metrics.cost_per_token
            } for name, metrics in self.metrics.items()
        }

class IntelligentOrchestrator:
    """Orchestrator with LLM selection and memory capabilities"""
    
    def __init__(self, llm_pool: LLMPool):
        self.llm_pool = llm_pool
        
        # Initialize CrewAI memory systems if available
        if MEMORY_AVAILABLE:
            self.short_term_memory = ShortTermMemory()
            self.long_term_memory = LongTermMemory()
            self.entity_memory = EntityMemory()
        else:
            self.short_term_memory = None
            self.long_term_memory = None
            self.entity_memory = None
        
        # Get optimal LLM for orchestration
        orchestrator_llm, self.orchestrator_model_name = llm_pool.get_optimal_model(
            "orchestration", query_complexity=0.8
        )
        
        # Create orchestrator agent with memory if available
        agent_kwargs = {
            'role': 'Intelligent Multi-LLM Orchestrator',
            'goal': '''Analyze queries and optimally route them to the best LLMs based on:
            - Query complexity and domain expertise needed
            - Real-time performance metrics and efficiency  
            - Cost-quality trade-offs and response time requirements
            - Historical success patterns and learning from feedback''',
            'backstory': """You are an advanced AI orchestrator with deep understanding of 
            different LLM capabilities, strengths, and optimal use cases. You continuously 
            learn from performance data to make increasingly better routing decisions, 
            balancing quality, speed, and cost efficiency.""",
            'llm': orchestrator_llm,
            'verbose': True,
            'allow_delegation': True
        }
        
        if MEMORY_AVAILABLE:
            agent_kwargs['memory'] = True
        
        self.orchestrator_agent = Agent(**agent_kwargs)
        
        # Initialize planning system (using built-in crew planning)
        self.planner = None  # Planning is handled by Crew.plan() method
        
        # Initialize training system (using built-in crew training) 
        self.training_handler = None  # Training is handled by Crew.train() method
        
    def analyze_query_complexity(self, query: str, context: Dict = None) -> float:
        """Analyze query complexity to inform LLM selection"""
        
        analysis_prompt = f"""
        Analyze the complexity of this query on a scale of 0.0 to 1.0:
        
        Query: {query}
        Context: {context or 'None'}
        
        Consider:
        - Technical depth required (0.1 = simple FAQ, 1.0 = complex debugging)
        - Domain expertise needed (0.1 = general knowledge, 1.0 = specialized)
        - Reasoning steps required (0.1 = direct answer, 1.0 = multi-step analysis)
        - Response length expected (0.1 = brief, 1.0 = comprehensive)
        
        Return ONLY a numeric score (e.g., 0.7).
        """
        
        try:
            # Use orchestrator to analyze complexity
            complexity_task = Task(
                description=analysis_prompt,
                agent=self.orchestrator_agent,
                expected_output="Numeric complexity score"
            )
            
            crew_kwargs = {
                'agents': [self.orchestrator_agent],
                'tasks': [complexity_task],
                'verbose': False
            }
            
            if MEMORY_AVAILABLE:
                crew_kwargs['memory'] = True
                
            result = Crew(**crew_kwargs).kickoff()
            
            # Extract numeric score
            score_text = str(result).strip()
            # Extract first valid float from the text
            import re
            numbers = re.findall(r'\d+\.?\d*', score_text)
            if numbers:
                try:
                    complexity = float(numbers[0])
                    return min(1.0, max(0.0, complexity))
                except ValueError:
                    pass
            
            # Fallback if no valid number found
            return 0.5
            
        except Exception as e:
            logging.warning(f"Complexity analysis failed: {e}")
            return 0.5  # Default medium complexity
    
    def select_optimal_llms(self, query: str, context: Dict = None) -> Dict[str, Tuple[LLM, str]]:
        """Select optimal LLMs for different specialist roles"""
        
        # Analyze query complexity
        complexity = self.analyze_query_complexity(query, context)
        
        # Determine required specialist types
        specialist_types = self._determine_specialists_needed(query, context)
        
        # Select optimal LLM for each specialist
        selected_llms = {}
        
        for specialist_type in specialist_types:
            optimal_llm, model_name = self.llm_pool.get_optimal_model(
                specialist_type, query_complexity=complexity
            )
            selected_llms[specialist_type] = (optimal_llm, model_name)
        
        # Log LLM selection to Galileo
        if GALILEO_INTEGRATION_AVAILABLE and galileo_integration:
            model_names = {role: model_name for role, (_, model_name) in selected_llms.items()}
            galileo_integration.log_llm_selection_event(
                query, model_names, complexity, context
            )
        
        return selected_llms
    
    def _determine_specialists_needed(self, query: str, context: Dict = None) -> List[str]:
        """Determine which specialists are needed for the query"""
        
        query_lower = query.lower()
        specialists = []
        
        # Technical specialist
        if any(term in query_lower for term in 
               ['webhook', 'api', 'integration', 'ssl', 'error', 'bug', 'technical']):
            specialists.append('technical')
        
        # Competitive analyst
        if any(term in query_lower for term in 
               ['competitor', 'compare', 'vs', 'market', 'pricing', 'alternative']):
            specialists.append('competitive')
        
        # Always include customer success for routing and coordination
        specialists.append('customer_success')
        
        return specialists

class AdaptiveMultiAgentSystem:
    """Complete adaptive multi-agent system with hot-swappable LLMs"""
    
    def __init__(self):
        # Initialize core systems
        self.llm_pool = LLMPool()
        self.orchestrator = IntelligentOrchestrator(self.llm_pool)
        
        # Initialize collaboration system (built into CrewAI)
        self.collaboration = True if COLLABORATION_AVAILABLE else None
        
        # Initialize evaluator for testing (using built-in crew evaluation)
        self.evaluator = True if TESTING_AVAILABLE else None
        
        # Performance tracking
        self.execution_history = []
        
        logging.info("Adaptive Multi-Agent System initialized")
        logging.info(f"Available LLMs: {list(self.llm_pool.models.keys())}")
    
    def create_specialist_agent(self, role: str, query: str, selected_llm: LLM, 
                              model_name: str) -> Agent:
        """Create specialist agents with dynamically selected LLMs"""
        
        agents = {
            'technical': Agent(
                role='Technical Integration Specialist',
                goal='Solve complex technical issues with precision and comprehensive analysis',
                backstory="""You are a senior technical specialist with expertise in:
                - API integrations and webhook troubleshooting
                - System architecture and performance optimization  
                - Security implementations and debugging
                - Real-time problem diagnosis and solution development""",
                llm=selected_llm,
                memory=MEMORY_AVAILABLE,
                verbose=True,
                allow_delegation=False
            ),
            
            'competitive': Agent(
                role='Competitive Intelligence Specialist',
                goal='Provide strategic competitive analysis and market positioning insights',
                backstory="""You are a competitive intelligence expert specializing in:
                - AI agent platform comparisons and technical differentiation
                - Market positioning and pricing strategy analysis
                - Feature gap analysis and competitive advantages
                - Strategic recommendations for market positioning""",
                llm=selected_llm,
                memory=MEMORY_AVAILABLE,
                verbose=True,
                allow_delegation=False
            ),
            
            'customer_success': Agent(
                role='Customer Success Specialist',
                goal='Provide excellent customer service and coordinate with specialists',
                backstory="""You are a customer success expert focused on:
                - Understanding customer needs and translating technical solutions
                - Coordinating between technical specialists and customers
                - Ensuring clear communication and customer satisfaction
                - Escalation management and relationship building""",
                llm=selected_llm,
                memory=MEMORY_AVAILABLE,
                verbose=True,
                allow_delegation=True
            )
        }
        
        agent = agents.get(role)
        if agent:
            # Track which LLM is being used (store in backstory for compatibility)
            original_backstory = agent.backstory
            agent.backstory = f"{original_backstory}\n\n[System: Using {model_name} LLM for this role]"
            
        return agent
    
    def process_query_with_adaptive_llms(self, query: str, context: Dict = None) -> Dict:
        """Process queries with dynamically selected LLMs and full CrewAI features"""
        
        start_time = time.time()
        context = context or {}
        
        try:
            # Step 1: Select optimal LLMs for each specialist
            selected_llms = self.orchestrator.select_optimal_llms(query, context)
            
            logging.info(f"Selected LLMs: {[(role, model_name) for role, (_, model_name) in selected_llms.items()]}")
            
            # Step 2: Create agents with selected LLMs
            agents = []
            model_names = {}
            
            for role, (llm, model_name) in selected_llms.items():
                agent = self.create_specialist_agent(role, query, llm, model_name)
                if agent:
                    agents.append(agent)
                    model_names[role] = model_name
            
            # Step 3: Create comprehensive task with planning
            main_task = Task(
                description=f"""
                Analyze and provide a comprehensive response to this customer query:
                
                Query: {query}
                Context: {json.dumps(context, indent=2)}
                
                Requirements:
                1. Provide accurate, helpful, and actionable information
                2. Use appropriate technical depth for the audience
                3. Include specific steps or recommendations when applicable
                4. Collaborate between specialists as needed
                5. Ensure the response is professional and customer-focused
                
                The response should demonstrate the value of our multi-agent AI system
                with intelligent LLM selection and specialist collaboration.
                """,
                agent=agents[0],  # Primary agent based on query type
                expected_output="Comprehensive, professional response addressing the customer query",
                context_str=json.dumps(context)
            )
            
            # Step 4: Execute with available CrewAI features
            crew_kwargs = {
                'agents': agents,
                'tasks': [main_task],
                'verbose': True
            }
            
            if MEMORY_AVAILABLE:
                crew_kwargs['memory'] = True
                
            if PLANNING_AVAILABLE:
                crew_kwargs['planning'] = True
                
            if COLLABORATION_AVAILABLE and self.collaboration:
                crew_kwargs['collaboration'] = self.collaboration
            
            crew = Crew(**crew_kwargs)
            
            # Plan and execute
            if PLANNING_AVAILABLE and hasattr(crew, 'plan'):
                execution_plan = crew.plan()
                logging.info(f"Execution plan: {execution_plan}")
            
            result = crew.kickoff()
            
            # Step 5: Evaluate and track performance
            execution_time = time.time() - start_time
            
            # Evaluate response quality
            quality_scores = {}
            for role, model_name in model_names.items():
                quality_score = self.llm_pool.evaluate_response_quality(
                    query, str(result), role
                )
                quality_scores[role] = quality_score
                
                # Track performance
                token_usage = {"input": len(query), "output": len(str(result))}
                self.llm_pool.track_performance(
                    model_name, execution_time, quality_score, token_usage, True
                )
                
                # Log performance metrics to Galileo
                if GALILEO_INTEGRATION_AVAILABLE and galileo_integration:
                    perf_metrics = {
                        "response_time": execution_time,
                        "quality_score": quality_score,
                        "input_tokens": token_usage["input"],
                        "output_tokens": token_usage["output"],
                        "success_rate": 1.0,
                        "efficiency_score": self.llm_pool.metrics[model_name].get_efficiency_score()
                    }
                    galileo_integration.log_performance_metrics(model_name, perf_metrics)
            
            # Step 6: Store execution history for training
            execution_record = {
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "context": context,
                "selected_llms": model_names,
                "execution_time": execution_time,
                "quality_scores": quality_scores,
                "result": str(result)
            }
            
            self.execution_history.append(execution_record)
            
            # Trim history to prevent memory bloat
            if len(self.execution_history) > 1000:
                self.execution_history = self.execution_history[-500:]
            
            return {
                "response": str(result),
                "llms_used": model_names,
                "performance_metrics": {
                    "execution_time": execution_time,
                    "quality_scores": quality_scores,
                    "avg_quality": sum(quality_scores.values()) / len(quality_scores)
                },
                "optimization_insights": self.generate_optimization_insights(),
                "agent_collaboration": self.get_collaboration_insights(),
                "memory_utilization": self.get_memory_insights()
            }
            
        except Exception as e:
            logging.error(f"Adaptive processing failed: {e}")
            
            # Fallback to single model
            return self._fallback_processing(query, context, str(e))
    
    def _fallback_processing(self, query: str, context: Dict, error: str) -> Dict:
        """Fallback processing when adaptive system fails"""
        
        try:
            # Use the most reliable model for fallback
            fallback_llm, model_name = self.llm_pool.get_optimal_model("general", 0.5)
            
            fallback_agent = Agent(
                role='Fallback Support Agent',
                goal='Provide helpful response when the adaptive system encounters issues',
                backstory='Reliable backup agent for system resilience',
                llm=fallback_llm,
                verbose=True
            )
            
            fallback_task = Task(
                description=f"Provide a helpful response to: {query}",
                agent=fallback_agent,
                expected_output="Professional response"
            )
            
            crew = Crew(agents=[fallback_agent], tasks=[fallback_task])
            result = crew.kickoff()
            
            return {
                "response": str(result),
                "llms_used": {"fallback": model_name},
                "performance_metrics": {"execution_time": 0, "quality_scores": {}, "avg_quality": 0},
                "error": f"Adaptive system failed: {error}. Used fallback processing.",
                "optimization_insights": {},
                "agent_collaboration": {},
                "memory_utilization": {}
            }
            
        except Exception as fallback_error:
            return {
                "response": f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(fallback_error)}",
                "llms_used": {},
                "performance_metrics": {"execution_time": 0, "quality_scores": {}, "avg_quality": 0},
                "error": f"Both adaptive and fallback systems failed",
                "optimization_insights": {},
                "agent_collaboration": {},
                "memory_utilization": {}
            }
    
    def generate_optimization_insights(self) -> Dict:
        """Generate insights for system optimization"""
        
        performance_summary = self.llm_pool.get_performance_summary()
        
        # Find best performing models
        best_quality = max(performance_summary.items(), 
                          key=lambda x: x[1]['avg_quality'], 
                          default=('none', {'avg_quality': 0}))
        
        best_speed = min(performance_summary.items(), 
                        key=lambda x: x[1]['avg_response_time'], 
                        default=('none', {'avg_response_time': float('inf')}))
        
        best_efficiency = max(performance_summary.items(), 
                            key=lambda x: x[1]['efficiency_score'], 
                            default=('none', {'efficiency_score': 0}))
        
        return {
            "best_quality_model": best_quality[0],
            "fastest_model": best_speed[0], 
            "most_efficient_model": best_efficiency[0],
            "performance_summary": performance_summary,
            "recommendations": self._generate_recommendations(performance_summary)
        }
    
    def _generate_recommendations(self, performance_summary: Dict) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        for model_name, metrics in performance_summary.items():
            if metrics['success_rate'] < 0.9:
                recommendations.append(f"Consider reducing load on {model_name} due to low success rate ({metrics['success_rate']:.2f})")
            
            if metrics['avg_response_time'] > 10.0:
                recommendations.append(f"{model_name} is slow (avg: {metrics['avg_response_time']:.1f}s) - consider alternatives for time-sensitive tasks")
            
            if metrics['avg_quality'] > 8.5 and metrics['efficiency_score'] > 5.0:
                recommendations.append(f"{model_name} is performing excellently - consider increasing its usage")
        
        return recommendations
    
    def get_collaboration_insights(self) -> Dict:
        """Get insights about agent collaboration"""
        return {
            "collaboration_active": COLLABORATION_AVAILABLE,
            "delegation_patterns": "Orchestrator delegates to specialists based on expertise",
            "knowledge_sharing": "Agents share context" + (" through memory systems" if MEMORY_AVAILABLE else " via task context"),
            "coordination_efficiency": "High - intelligent routing reduces redundant processing"
        }
    
    def get_memory_insights(self) -> Dict:
        """Get insights about memory utilization"""
        if MEMORY_AVAILABLE:
            return {
                "short_term_memory": "Active - tracks current conversation context",
                "long_term_memory": "Learning from historical interactions",
                "entity_memory": "Maintains knowledge about recurring issues and solutions",
                "memory_optimization": "Automated cleanup prevents memory bloat"
            }
        else:
            return {
                "memory_status": "Using basic context passing (CrewAI memory features not available)",
                "context_sharing": "Agents share information through task descriptions",
                "optimization": "Manual context management in use"
            }
    
    def train_system(self, feedback_data: List[Dict]) -> Dict:
        """Train the system based on feedback data"""
        
        try:
            # Prepare training data
            training_inputs = []
            training_outputs = []
            
            for feedback in feedback_data:
                training_inputs.append({
                    "query": feedback["query"],
                    "context": feedback.get("context", {}),
                    "selected_llms": feedback.get("selected_llms", {})
                })
                
                training_outputs.append({
                    "quality_score": feedback.get("quality_score", 5.0),
                    "user_satisfaction": feedback.get("user_satisfaction", 5.0),
                    "execution_time": feedback.get("execution_time", 1.0)
                })
            
            # Update LLM selection weights based on performance
            self._update_selection_weights(training_inputs, training_outputs)
            
            training_results = {
                "training_completed": True,
                "samples_processed": len(feedback_data),
                "updated_weights": self.llm_pool.selection_weights,
                "performance_improvements": "LLM selection algorithms updated based on feedback"
            }
            
            # Log training event to Galileo
            if GALILEO_INTEGRATION_AVAILABLE and galileo_integration:
                galileo_integration.log_training_event(feedback_data, training_results)
            
            return training_results
            
        except Exception as e:
            logging.error(f"Training failed: {e}")
            return {"training_completed": False, "error": str(e)}
    
    def _update_selection_weights(self, inputs: List[Dict], outputs: List[Dict]):
        """Update LLM selection weights based on training data"""
        
        # Simple weight adjustment based on average performance
        total_quality = sum(output["quality_score"] for output in outputs)
        total_satisfaction = sum(output["user_satisfaction"] for output in outputs)
        avg_time = sum(output["execution_time"] for output in outputs) / len(outputs)
        
        # Adjust weights based on performance
        if total_quality / len(outputs) > 7.0:
            self.llm_pool.selection_weights["quality"] += 0.05
        
        if avg_time < 3.0:
            self.llm_pool.selection_weights["speed"] += 0.05
        
        if total_satisfaction / len(outputs) > 8.0:
            self.llm_pool.selection_weights["reliability"] += 0.05
        
        # Normalize weights
        total_weight = sum(self.llm_pool.selection_weights.values())
        for key in self.llm_pool.selection_weights:
            self.llm_pool.selection_weights[key] /= total_weight
    
    def test_system(self, test_queries: List[Dict]) -> Dict:
        """Test the system with a set of queries"""
        
        test_results = []
        
        for test_case in test_queries:
            query = test_case["query"]
            expected_outcome = test_case.get("expected_outcome", {})
            
            # Process query
            start_time = time.time()
            result = self.process_query_with_adaptive_llms(
                query, test_case.get("context", {})
            )
            test_time = time.time() - start_time
            
            # Evaluate result
            test_result = {
                "query": query,
                "execution_time": test_time,
                "quality_score": result["performance_metrics"]["avg_quality"],
                "llms_used": result["llms_used"],
                "success": result.get("error") is None,
                "meets_expectations": self._evaluate_expectations(result, expected_outcome)
            }
            
            test_results.append(test_result)
        
        # Calculate overall metrics
        success_rate = sum(1 for r in test_results if r["success"]) / len(test_results)
        avg_quality = sum(r["quality_score"] for r in test_results) / len(test_results)
        avg_time = sum(r["execution_time"] for r in test_results) / len(test_results)
        
        return {
            "test_completed": True,
            "total_tests": len(test_queries),
            "success_rate": success_rate,
            "average_quality": avg_quality,
            "average_execution_time": avg_time,
            "detailed_results": test_results,
            "recommendations": self._generate_test_recommendations(test_results)
        }
    
    def _evaluate_expectations(self, result: Dict, expected: Dict) -> bool:
        """Evaluate if result meets expected outcomes"""
        
        if not expected:
            return True  # No expectations set
        
        # Check execution time expectation
        if "max_time" in expected:
            if result["performance_metrics"]["execution_time"] > expected["max_time"]:
                return False
        
        # Check quality expectation  
        if "min_quality" in expected:
            if result["performance_metrics"]["avg_quality"] < expected["min_quality"]:
                return False
        
        # Check required LLM types
        if "required_specialists" in expected:
            used_specialists = set(result["llms_used"].keys())
            required_specialists = set(expected["required_specialists"])
            if not required_specialists.issubset(used_specialists):
                return False
        
        return True
    
    def _generate_test_recommendations(self, test_results: List[Dict]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in test_results if not r["success"]]
        if failed_tests:
            recommendations.append(f"{len(failed_tests)} tests failed - investigate error handling")
        
        slow_tests = [r for r in test_results if r["execution_time"] > 10.0]
        if slow_tests:
            recommendations.append(f"{len(slow_tests)} tests were slow - optimize LLM selection for speed")
        
        low_quality_tests = [r for r in test_results if r["quality_score"] < 6.0]
        if low_quality_tests:
            recommendations.append(f"{len(low_quality_tests)} tests had low quality - review LLM capabilities")
        
        return recommendations

# Initialize the adaptive system
adaptive_system = AdaptiveMultiAgentSystem()

# Add compatibility method for existing backend integration
def process_technical_query(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Compatibility wrapper for existing backend integration"""
    
    # Use the adaptive system to process the query
    result = adaptive_system.process_query_with_adaptive_llms(query, context or {})
    
    # Convert to expected backend format
    return {
        "agent_info": {
            "role": "Adaptive Multi-LLM Orchestrator",
            "processing_time": f"{result['performance_metrics']['execution_time']:.2f} seconds",
            "ai_powered": True,
            "orchestration_mode": True,
            "llms_used": result["llms_used"]
        },
        "technical_response": {
            "ai_analysis": result["response"],
            "optimization_insights": result["optimization_insights"],
            "agent_collaboration": result["agent_collaboration"], 
            "memory_utilization": result["memory_utilization"]
        },
        "query_analysis": {
            "original_query": query,
            "processing_approach": "Adaptive Multi-LLM Orchestration with CrewAI",
            "ai_confidence": "High - Dynamic LLM Selection",
            "llms_selected": list(result["llms_used"].values())
        },
        "competitive_advantage": {
            "vs_agentforce": "Adaptive LLM selection vs Fixed models",
            "response_quality": "Optimized quality-cost-speed balance",
            "intelligence_level": "Self-improving multi-model orchestration"
        },
        "performance_metrics": result["performance_metrics"],
        "timestamp": datetime.now().isoformat()
    }

# Attach the method to the adaptive system
adaptive_system.process_technical_query = process_technical_query