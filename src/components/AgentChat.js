
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CheckCircle, Search, Filter, ChevronDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useAgentChat } from '../hooks/useAgentChat';

const AgentChat = () => {
  const [selectedAgent, setSelectedAgent] = useState('technical');
  const [message, setMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);
  const [websocket, setWebsocket] = useState(null);
  const [realTimeAgentStates, setRealTimeAgentStates] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const messagesEndRef = useRef(null);
  const clientId = useRef(`agent_chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  
  const { messages, sendMessage, isLoading, agentStatus } = useAgentChat(selectedAgent);

  const agents = [
    // Technical Domain
    {
      id: 'technical',
      name: 'Technical Integration Specialist',
      description: 'APIs, webhooks, SSL, authentication, and system integrations',
      avatar: '🔧',
      category: 'Technical',
      expertise: ['Webhook debugging', 'API authentication', 'SSL certificates', 'System architecture']
    },
    {
      id: 'devops',
      name: 'DevOps Engineer',
      description: 'Deployment, infrastructure, monitoring, and performance optimization',
      avatar: '⚙️',
      category: 'Technical',
      expertise: ['CI/CD', 'Docker', 'Kubernetes', 'Monitoring', 'Performance tuning']
    },
    {
      id: 'security',
      name: 'Security Specialist',
      description: 'Security audits, compliance, vulnerability assessment, and encryption',
      avatar: '🛡️',
      category: 'Technical',
      expertise: ['Penetration testing', 'GDPR compliance', 'OAuth', 'Encryption']
    },
    {
      id: 'database',
      name: 'Database Expert',
      description: 'Database design, optimization, migrations, and data modeling',
      avatar: '🗄️',
      category: 'Technical',
      expertise: ['SQL optimization', 'Database migrations', 'Data modeling']
    },
    
    // Business Domain  
    {
      id: 'billing',
      name: 'Billing & Revenue Expert',
      description: 'Payment processing, subscription management, revenue recognition',
      avatar: '💳',
      category: 'Business',
      expertise: ['Payment gateways', 'Subscription models', 'Revenue analytics', 'Tax compliance']
    },
    {
      id: 'legal',
      name: 'Legal Compliance Agent',
      description: 'Contract analysis, compliance requirements, and legal documentation',
      avatar: '⚖️',
      category: 'Business',
      expertise: ['Contract review', 'GDPR', 'Data privacy', 'Terms of service']
    },
    {
      id: 'sales',
      name: 'Sales Operations Specialist',
      description: 'CRM management, lead qualification, and sales process optimization',
      avatar: '📈',
      category: 'Business',
      expertise: ['Salesforce admin', 'Lead scoring', 'Sales analytics', 'Pipeline management']
    },
    {
      id: 'marketing',
      name: 'Marketing Automation Expert',
      description: 'Campaign management, lead nurturing, and marketing technology',
      avatar: '📢',
      category: 'Business',
      expertise: ['Email campaigns', 'Lead nurturing', 'Marketing analytics', 'A/B testing']
    },
    
    // Analysis Domain
    {
      id: 'competitive',
      name: 'Competitive Intelligence Analyst',
      description: 'Market research, competitor analysis, and strategic positioning',
      avatar: '📊',
      category: 'Analysis',
      expertise: ['Market research', 'Competitor analysis', 'Pricing strategy', 'SWOT analysis']
    },
    {
      id: 'data',
      name: 'Data Analytics Specialist',
      description: 'Business intelligence, reporting, and predictive analytics',
      avatar: '📈',
      category: 'Analysis',
      expertise: ['SQL queries', 'Dashboard creation', 'Predictive modeling', 'KPI tracking']
    },
    {
      id: 'finance',
      name: 'Financial Analyst',
      description: 'Financial modeling, budgeting, forecasting, and cost analysis',
      avatar: '💰',
      category: 'Analysis',
      expertise: ['ROI analysis', 'Budget planning', 'Cost modeling', 'Financial forecasting']
    },
    
    // Customer Domain
    {
      id: 'support',
      name: 'Customer Success Manager',
      description: 'Customer onboarding, retention strategies, and relationship management',
      avatar: '🎯',
      category: 'Customer',
      expertise: ['Customer onboarding', 'Retention analysis', 'Health scoring', 'Expansion planning']
    },
    {
      id: 'training',
      name: 'Training & Education Specialist',
      description: 'User education, documentation, and knowledge management',
      avatar: '🎓',
      category: 'Customer',
      expertise: ['Course creation', 'Documentation', 'User guides', 'Video tutorials']
    },
    
    // Product Domain
    {
      id: 'product',
      name: 'Product Manager',
      description: 'Product strategy, roadmap planning, and feature prioritization',
      avatar: '🚀',
      category: 'Product',
      expertise: ['Product roadmap', 'User research', 'Feature prioritization', 'Market analysis']
    },
    {
      id: 'ux',
      name: 'UX Research Specialist',
      description: 'User experience research, design analysis, and usability testing',
      avatar: '🎨',
      category: 'Product',
      expertise: ['User interviews', 'Usability testing', 'Design systems', 'User journey mapping']
    },
    
    // Industry Specialists
    {
      id: 'healthcare',
      name: 'Healthcare Compliance Expert',
      description: 'HIPAA compliance, healthcare regulations, and medical data handling',
      avatar: '🏥',
      category: 'Industry',
      expertise: ['HIPAA compliance', 'Medical data', 'Healthcare regulations', 'Patient privacy']
    },
    {
      id: 'fintech',
      name: 'Financial Services Specialist',
      description: 'Banking regulations, PCI compliance, and financial data security',
      avatar: '🏦',
      category: 'Industry',
      expertise: ['PCI compliance', 'Banking regulations', 'Financial APIs', 'Fraud detection']
    },
    {
      id: 'ecommerce',
      name: 'E-commerce Platform Expert',
      description: 'Online retail, inventory management, and payment processing',
      avatar: '🛒',
      category: 'Industry',
      expertise: ['Shopping cart', 'Inventory systems', 'Payment gateways', 'Order management']
    },
    {
      id: 'saas',
      name: 'SaaS Business Model Expert',
      description: 'Subscription models, SaaS metrics, and platform scaling',
      avatar: '☁️',
      category: 'Industry',
      expertise: ['Subscription billing', 'SaaS metrics', 'Multi-tenancy', 'Platform scaling']
    }
  ];

  const demoQueries = {
    // Technical Domain
    technical: [
      "My webhook is failing with SSL certificate verification errors",
      "How do I implement webhook retry logic with exponential backoff?",
      "API integration is timing out. How should I configure this?",
      "Getting 401 errors when sending webhooks with HMAC signatures"
    ],
    devops: [
      "How do I set up a CI/CD pipeline for microservices?",
      "Container orchestration best practices for scaling",
      "Setting up monitoring alerts for production systems",
      "Blue-green deployment strategy for zero downtime"
    ],
    security: [
      "Conduct a security audit of our API endpoints",
      "Implement OAuth 2.0 with PKCE for mobile apps",
      "GDPR compliance checklist for data processing",
      "Vulnerability assessment for web application"
    ],
    database: [
      "Optimize slow-running SQL queries in production",
      "Database migration strategy for zero downtime",
      "Design data model for multi-tenant architecture",
      "Index optimization for improved query performance"
    ],
    
    // Business Domain
    billing: [
      "Handle failed payment webhooks and retry logic",
      "Customer wants to upgrade subscription mid-cycle",
      "Process partial refund for annual subscription",
      "Implement dunning management for failed payments"
    ],
    legal: [
      "Review contract terms for API usage limits",
      "GDPR compliance requirements for user data",
      "Privacy policy updates for new data collection",
      "Terms of service for SaaS platform"
    ],
    sales: [
      "Set up lead scoring in Salesforce CRM",
      "Optimize sales pipeline conversion rates",
      "Create automated sales analytics dashboard",
      "Configure territory management rules"
    ],
    marketing: [
      "Set up email automation for lead nurturing",
      "A/B test campaign performance optimization",
      "Marketing attribution tracking setup",
      "Lead qualification scoring system"
    ],
    
    // Analysis Domain
    competitive: [
      "Compare our pricing to Salesforce Service Cloud",
      "Key differentiators against Zendesk platform",
      "Competitive intelligence on Microsoft Dynamics",
      "Market positioning against custom solutions"
    ],
    data: [
      "Create executive dashboard for key metrics",
      "Predictive model for customer churn analysis",
      "SQL query optimization for reporting",
      "KPI tracking and business intelligence setup"
    ],
    finance: [
      "ROI analysis for new feature development",
      "Budget planning for next fiscal year",
      "Cost modeling for infrastructure scaling",
      "Financial forecasting for growth projections"
    ],
    
    // Customer Domain
    support: [
      "Customer onboarding optimization strategy",
      "Reduce churn risk through health scoring",
      "Expansion revenue opportunity analysis",
      "Customer success metrics and tracking"
    ],
    training: [
      "Create interactive tutorial for new users",
      "Documentation strategy for API changes",
      "Video training series for product features",
      "Knowledge base optimization for support"
    ],
    
    // Product Domain
    product: [
      "Product roadmap prioritization framework",
      "User research insights for feature development",
      "Market analysis for new product launch",
      "Feature adoption tracking and optimization"
    ],
    ux: [
      "Usability testing for checkout flow",
      "User journey mapping for onboarding",
      "Design system consistency audit",
      "User interview insights for product direction"
    ],
    
    // Industry Specialists
    healthcare: [
      "HIPAA compliance audit for patient data",
      "Medical data handling best practices",
      "Healthcare regulation requirements review",
      "Patient privacy protection implementation"
    ],
    fintech: [
      "PCI DSS compliance assessment",
      "Banking regulation compliance review",
      "Financial API security implementation",
      "Fraud detection system optimization"
    ],
    ecommerce: [
      "Shopping cart abandonment analysis",
      "Payment gateway optimization strategy",
      "Inventory management system setup",
      "Order fulfillment process optimization"
    ],
    saas: [
      "SaaS metrics dashboard creation",
      "Multi-tenant architecture scaling",
      "Subscription billing optimization",
      "Customer acquisition cost analysis"
    ]
  };

  // Get unique categories
  const categories = ['All', ...new Set(agents.map(agent => agent.category))];
  
  // Filter agents based on search and category
  const filteredAgents = agents.filter(agent => {
    const matchesSearch = searchTerm === '' || 
      agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.expertise.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'All' || agent.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  // Group agents by category for display
  const agentsByCategory = filteredAgents.reduce((acc, agent) => {
    if (!acc[agent.category]) {
      acc[agent.category] = [];
    }
    acc[agent.category].push(agent);
    return acc;
  }, {});

  // WebSocket connection for real-time agent tracking
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://0.0.0.0:8000/api/ws/agent-tracking/${clientId.current}`);
        
        ws.onopen = () => {
          setConnectionStatus('connected');
          setWebsocket(ws);
          console.log('Connected to real-time agent tracking');
        };
        
        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };
        
        ws.onclose = () => {
          setConnectionStatus('disconnected');
          setWebsocket(null);
          
          // Attempt to reconnect after 3 seconds
          setTimeout(() => {
            if (connectionStatus !== 'connected') {
              connectWebSocket();
            }
          }, 3000);
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('error');
        };
        
      } catch (err) {
        console.error('Failed to create WebSocket connection:', err);
        setConnectionStatus('error');
      }
    };

    connectWebSocket();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'session_started':
      case 'agent_status_update':
      case 'phase_update':
        if (message.state && message.state.active_agents) {
          const agentStates = {};
          message.state.active_agents.forEach(agent => {
            agentStates[agent.agent_name] = {
              status: agent.status,
              progress: agent.progress,
              currentTask: agent.current_task,
              details: agent.details,
              updatedAt: agent.updated_at
            };
          });
          setRealTimeAgentStates(agentStates);
        }
        break;
      case 'session_completed':
        // Mark all agents as finished
        setRealTimeAgentStates(prev => {
          const updated = { ...prev };
          Object.keys(updated).forEach(agentName => {
            updated[agentName] = { 
              ...updated[agentName], 
              status: 'finished',
              progress: 100 
            };
          });
          return updated;
        });
        break;
      case 'ping':
        // Respond to keep-alive ping
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          websocket.send(JSON.stringify({ type: 'pong' }));
        }
        break;
      default:
        break;
    }
  };

  const getAgentRealTimeStatus = (agentName) => {
    // Map agent IDs to real-time states
    const agentMappings = {
      'technical': 'Technical Integration Specialist',
      'devops': 'DevOps Engineer', 
      'security': 'Security Specialist',
      'database': 'Database Expert',
      'billing': 'Billing & Revenue Expert',
      'legal': 'Legal Compliance Agent',
      'sales': 'Sales Operations Specialist',
      'marketing': 'Marketing Automation Expert',
      'competitive': 'Competitive Intelligence Analyst',
      'data': 'Data Analytics Specialist',
      'finance': 'Financial Analyst',
      'support': 'Customer Success Manager',
      'training': 'Training & Education Specialist',
      'product': 'Product Manager',
      'ux': 'UX Research Specialist',
      'healthcare': 'Healthcare Compliance Expert',
      'fintech': 'Financial Services Specialist',
      'ecommerce': 'E-commerce Platform Expert',
      'saas': 'SaaS Business Model Expert'
    };

    const mappedName = agentMappings[agentName];
    return realTimeAgentStates[mappedName] || realTimeAgentStates[agentName];
  };

  const getStatusColor = (status) => {
    const statusColors = {
      'idle': 'bg-gray-400',
      'analyzing': 'bg-blue-500 animate-pulse',
      'processing': 'bg-yellow-500 animate-pulse',
      'collaborating': 'bg-purple-500 animate-pulse',
      'completing': 'bg-orange-500 animate-pulse',
      'finished': 'bg-green-500',
      'error': 'bg-red-500'
    };
    return statusColors[status] || 'bg-green-400';
  };

  const getStatusText = (status) => {
    const statusText = {
      'idle': 'Online',
      'analyzing': 'Analyzing',
      'processing': 'Processing',
      'collaborating': 'Collaborating',
      'completing': 'Completing',
      'finished': 'Finished',
      'error': 'Error'
    };
    return statusText[status] || 'Online';
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    await sendMessage(message);
    setMessage('');
  };

  const handleDemoQuery = (query) => {
    setMessage(query);
  };

  const currentAgent = agents.find(agent => agent.id === selectedAgent);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 h-[calc(100vh-200px)]">
      {/* Agent Selection Sidebar */}
      <div className="lg:col-span-1 space-y-4">
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Agent Library</h3>
            <span className="text-sm text-gray-500">{agents.length} specialists</span>
          </div>
          
          {/* Search and Filter */}
          <div className="space-y-3 mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search agents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
            </div>
            
            <div className="relative">
              <button
                onClick={() => setShowCategoryDropdown(!showCategoryDropdown)}
                className="w-full flex items-center justify-between px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
              >
                <div className="flex items-center">
                  <Filter className="w-4 h-4 mr-2 text-gray-400" />
                  <span>{selectedCategory}</span>
                </div>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>
              
              {showCategoryDropdown && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
                  {categories.map((category) => (
                    <button
                      key={category}
                      onClick={() => {
                        setSelectedCategory(category);
                        setShowCategoryDropdown(false);
                      }}
                      className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${
                        selectedCategory === category ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                      }`}
                    >
                      {category}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Agent List */}
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {Object.keys(agentsByCategory).length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Bot className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">No agents found</p>
              </div>
            )}
            
            {Object.entries(agentsByCategory).map(([category, categoryAgents]) => (
              <div key={category}>
                {selectedCategory === 'All' && (
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                    {category} ({categoryAgents.length})
                  </h4>
                )}
                
                {categoryAgents.map((agent) => {
                  const realTimeStatus = getAgentRealTimeStatus(agent.id);
                  const status = realTimeStatus?.status || 'idle';
                  const progress = realTimeStatus?.progress || 0;
                  const currentTask = realTimeStatus?.currentTask;
                  
                  return (
                    <button
                      key={agent.id}
                      onClick={() => setSelectedAgent(agent.id)}
                      className={`w-full p-3 rounded-lg border transition-all text-left mb-2 ${
                        selectedAgent === agent.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-start">
                        <span className="text-lg mr-2 mt-0.5">{agent.avatar}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <h4 className={`font-medium text-sm ${
                              selectedAgent === agent.id ? 'text-blue-900' : 'text-gray-900'
                            }`}>
                              {agent.name}
                            </h4>
                            <div className="flex items-center">
                              <div className={`w-2 h-2 rounded-full mr-1 ${getStatusColor(status)}`}></div>
                              {progress > 0 && progress < 100 && (
                                <span className="text-xs text-blue-600 font-medium">{Math.round(progress)}%</span>
                              )}
                            </div>
                          </div>
                          <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                            {agent.description}
                          </p>
                          {currentTask && (
                            <p className="text-xs text-blue-700 mt-1 font-medium truncate">
                              📋 {currentTask}
                            </p>
                          )}
                          {progress > 0 && progress < 100 && (
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 rounded-full h-1">
                                <div 
                                  className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                                  style={{ width: `${progress}%` }}
                                ></div>
                              </div>
                            </div>
                          )}
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-xs text-gray-500">
                              {agent.expertise.slice(0,2).join(' • ')}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              status === 'finished' ? 'bg-green-100 text-green-700' :
                              status === 'error' ? 'bg-red-100 text-red-700' :
                              status === 'idle' ? 'bg-gray-100 text-gray-700' :
                              'bg-blue-100 text-blue-700'
                            }`}>
                              {getStatusText(status)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Demo Queries */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h4 className="text-md font-medium text-gray-900 mb-3 flex items-center">
            <span className="text-lg mr-2">{currentAgent?.avatar}</span>
            Sample Queries for {currentAgent?.name}
          </h4>
          <div className="space-y-2">
            {demoQueries[selectedAgent]?.map((query, index) => (
              <button
                key={index}
                onClick={() => handleDemoQuery(query)}
                className="w-full p-3 text-left text-sm bg-gray-50 hover:bg-blue-50 hover:border-blue-200 rounded-lg border border-gray-200 transition-colors"
              >
                {query}
              </button>
            ))}
            
            {!demoQueries[selectedAgent] && (
              <div className="text-center py-4 text-gray-500">
                <p className="text-sm">No sample queries available for this agent yet.</p>
              </div>
            )}
          </div>
          
          {/* Agent Stats */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-center text-xs">
              <div>
                <div className="font-semibold text-green-600">{currentAgent?.expertise?.length || 0}</div>
                <div className="text-gray-600">Specialties</div>
              </div>
              <div>
                <div className={`font-semibold flex items-center justify-center ${
                  connectionStatus === 'connected' ? 'text-green-600' : 
                  connectionStatus === 'error' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  <div className={`w-1.5 h-1.5 rounded-full mr-1 ${
                    connectionStatus === 'connected' ? 'bg-green-500' :
                    connectionStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
                  }`}></div>
                  {connectionStatus === 'connected' ? 'Live' : 
                   connectionStatus === 'error' ? 'Error' : 'Offline'}
                </div>
                <div className="text-gray-600">Real-time</div>
              </div>
            </div>
            
            {/* Real-time connection status */}
            <div className="mt-3 text-center">
              <span className={`text-xs px-2 py-1 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-100 text-green-700' :
                connectionStatus === 'error' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {connectionStatus === 'connected' ? '🔴 Live Agent Tracking' :
                 connectionStatus === 'error' ? '⚠️ Connection Error' :
                 '🔄 Connecting...'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="lg:col-span-3 bg-white rounded-lg shadow-sm border flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
          <div className="flex items-center">
            <span className="text-3xl mr-3">{currentAgent?.avatar}</span>
            <div>
              <h3 className="font-semibold text-lg">{currentAgent?.name}</h3>
              <p className="text-sm opacity-90">{currentAgent?.description}</p>
              <div className="flex items-center mt-1">
                <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full mr-2">
                  {currentAgent?.category}
                </span>
                <div className="flex items-center">
                  {(() => {
                    const realTimeStatus = getAgentRealTimeStatus(selectedAgent);
                    const status = realTimeStatus?.status || 'idle';
                    const progress = realTimeStatus?.progress || 0;
                    
                    if (status === 'finished') {
                      return (
                        <>
                          <CheckCircle className="w-3 h-3 mr-1" />
                          <span className="text-xs">Completed</span>
                        </>
                      );
                    } else if (status !== 'idle' && progress > 0) {
                      return (
                        <>
                          <div className="w-3 h-3 mr-1 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span className="text-xs">{getStatusText(status)} ({Math.round(progress)}%)</span>
                        </>
                      );
                    } else {
                      return (
                        <>
                          <div className={`w-3 h-3 mr-1 rounded-full ${getStatusColor(status)}`}></div>
                          <span className="text-xs">{getStatusText(status)}</span>
                        </>
                      );
                    }
                  })()}
                </div>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <div className="font-semibold">95%</div>
                <div className="opacity-75">Confidence</div>
              </div>
              <div>
                <div className="font-semibold">1.2s</div>
                <div className="opacity-75">Avg Response</div>
              </div>
            </div>
            <div className="mt-2">
              <span className="text-xs opacity-75">
                {currentAgent?.expertise?.length} specialties
              </span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <div className="text-4xl mb-4">{currentAgent?.avatar}</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {currentAgent?.name} Ready to Help
              </h3>
              <p className="text-gray-600 mb-4">
                Specialized in {currentAgent?.expertise?.slice(0,3).join(', ').toLowerCase()}
              </p>
              <div className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-blue-50 text-blue-700">
                <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                {currentAgent?.category} Domain Expert
              </div>
            </div>
          )}
          
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`${msg.sender === 'agent' && msg.content.includes('**') ? 'max-w-4xl' : 'max-w-xs lg:max-w-md'} px-4 py-3 rounded-lg ${
                  msg.sender === 'user'
                    ? 'bg-salesforce-blue text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="flex items-start space-x-2">
                  {msg.sender === 'agent' && (
                    <span className="text-lg">{currentAgent?.avatar}</span>
                  )}
                  {msg.sender === 'user' && (
                    <User className="w-5 h-5 mt-1" />
                  )}
                  <div className="flex-1">
                    {msg.sender === 'agent' && msg.content.includes('**') ? (
                      <div className="text-sm prose prose-sm max-w-none">
                        <ReactMarkdown
                          components={{
                            h1: ({children}) => <h1 className="text-lg font-bold text-gray-900 mb-2">{children}</h1>,
                            h2: ({children}) => <h2 className="text-base font-semibold text-gray-800 mb-2">{children}</h2>,
                            h3: ({children}) => <h3 className="text-sm font-semibold text-gray-800 mb-1">{children}</h3>,
                            strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                            p: ({children}) => <p className="mb-2 text-gray-700 leading-relaxed">{children}</p>,
                            ul: ({children}) => <ul className="list-disc pl-4 mb-2 text-gray-700">{children}</ul>,
                            ol: ({children}) => <ol className="list-decimal pl-4 mb-2 text-gray-700">{children}</ol>,
                            li: ({children}) => <li className="mb-1">{children}</li>,
                            code: ({inline, children}) => inline 
                              ? <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-800">{children}</code>
                              : <code className="block bg-gray-100 p-3 rounded text-xs font-mono text-gray-800 whitespace-pre-wrap overflow-x-auto">{children}</code>,
                            pre: ({children}) => <div className="bg-gray-100 p-3 rounded mb-2 overflow-x-auto">{children}</div>
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-sm">{msg.content}</p>
                    )}
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs opacity-75">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                      {msg.confidence && (
                        <span className="text-xs opacity-75">
                          {Math.round(msg.confidence * 100)}% confident
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{currentAgent?.avatar}</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t">
          <div className="flex space-x-4">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={`Ask ${currentAgent?.name} anything...`}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-salesforce-blue focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className="px-6 py-2 bg-salesforce-blue text-white rounded-lg hover:bg-salesforce-darkblue disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AgentChat;
