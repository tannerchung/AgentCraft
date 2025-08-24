
import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, CheckCircle, Clock, Users, ArrowRight, Brain, Send, User, Bot, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const MultiAgentDemo = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [agentProgress, setAgentProgress] = useState({
    technical: 0,
    billing: 0,
    competitive: 0,
    coordinator: 0
  });
  
  // Chat interface state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [escalationTriggered, setEscalationTriggered] = useState(false);
  const [activeAgents, setActiveAgents] = useState([]);

  const scenario = {
    title: "Complex Customer Issue: Enterprise Integration",
    description: "Customer has webhook failures, billing discrepancies, and needs competitive positioning for internal presentation",
    steps: [
      {
        id: 1,
        title: "Issue Analysis",
        description: "Coordinator analyzes the multi-faceted customer issue",
        agent: "coordinator",
        duration: 2000,
        output: "Identified 3 distinct issues requiring specialized expertise"
      },
      {
        id: 2,
        title: "Technical Diagnosis",
        description: "Technical agent investigates webhook failures",
        agent: "technical",
        duration: 3000,
        output: "SSL certificate chain incomplete, HMAC signature mismatch detected"
      },
      {
        id: 3,
        title: "Billing Investigation",
        description: "Billing agent reviews payment discrepancies",
        agent: "billing",
        duration: 2500,
        output: "Prorated charges calculation error, refund processing initiated"
      },
      {
        id: 4,
        title: "Competitive Research",
        description: "Competitive agent prepares positioning materials",
        agent: "competitive",
        duration: 3500,
        output: "ROI analysis complete, competitive advantage document generated"
      },
      {
        id: 5,
        title: "Solution Synthesis",
        description: "Coordinator compiles comprehensive response",
        agent: "coordinator",
        duration: 2000,
        output: "Integrated solution plan with technical fixes, billing resolution, and strategic positioning"
      }
    ]
  };

  const agents = {
    // Core Orchestration
    coordinator: {
      name: "Orchestration Agent",
      avatar: "🧠",
      color: "purple",
      description: "Coordinates multi-agent workflows and synthesizes responses",
      specialties: ["workflow management", "agent routing", "response synthesis"],
      category: "orchestration"
    },
    
    // Technical Domain
    technical: {
      name: "Technical Integration Specialist",
      avatar: "🔧",
      color: "blue", 
      description: "APIs, webhooks, SSL, authentication, and system integrations",
      specialties: ["webhook debugging", "API authentication", "SSL certificates", "system architecture"],
      category: "technical"
    },
    devops: {
      name: "DevOps Engineer",
      avatar: "⚙️",
      color: "blue",
      description: "Deployment, infrastructure, monitoring, and performance optimization",
      specialties: ["CI/CD", "Docker", "Kubernetes", "monitoring", "performance tuning"],
      category: "technical"
    },
    security: {
      name: "Security Specialist",
      avatar: "🛡️",
      color: "red",
      description: "Security audits, compliance, vulnerability assessment, and encryption",
      specialties: ["penetration testing", "GDPR compliance", "OAuth", "encryption", "security audits"],
      category: "technical"
    },
    database: {
      name: "Database Expert",
      avatar: "🗄️",
      color: "green",
      description: "Database design, optimization, migrations, and data modeling",
      specialties: ["SQL optimization", "database migrations", "data modeling", "performance tuning"],
      category: "technical"
    },
    
    // Business Domain  
    billing: {
      name: "Billing & Revenue Expert",
      avatar: "💳",
      color: "green",
      description: "Payment processing, subscription management, revenue recognition",
      specialties: ["payment gateways", "subscription models", "revenue analytics", "tax compliance"],
      category: "business"
    },
    legal: {
      name: "Legal Compliance Agent",
      avatar: "⚖️", 
      color: "gray",
      description: "Contract analysis, compliance requirements, and legal documentation",
      specialties: ["contract review", "GDPR", "data privacy", "terms of service"],
      category: "business"
    },
    sales: {
      name: "Sales Operations Specialist",
      avatar: "📈",
      color: "green",
      description: "CRM management, lead qualification, and sales process optimization",
      specialties: ["Salesforce admin", "lead scoring", "sales analytics", "pipeline management"],
      category: "business"
    },
    marketing: {
      name: "Marketing Automation Expert",
      avatar: "📢",
      color: "pink",
      description: "Campaign management, lead nurturing, and marketing technology",
      specialties: ["email campaigns", "lead nurturing", "marketing analytics", "A/B testing"],
      category: "business"
    },
    
    // Analysis Domain
    competitive: {
      name: "Competitive Intelligence Analyst",
      avatar: "📊",
      color: "orange",
      description: "Market research, competitor analysis, and strategic positioning",
      specialties: ["market research", "competitor analysis", "pricing strategy", "SWOT analysis"],
      category: "analysis"
    },
    data: {
      name: "Data Analytics Specialist",
      avatar: "📈",
      color: "blue",
      description: "Business intelligence, reporting, and predictive analytics",
      specialties: ["SQL queries", "dashboard creation", "predictive modeling", "KPI tracking"],
      category: "analysis"
    },
    finance: {
      name: "Financial Analyst",
      avatar: "💰",
      color: "green",
      description: "Financial modeling, budgeting, forecasting, and cost analysis",
      specialties: ["ROI analysis", "budget planning", "cost modeling", "financial forecasting"],
      category: "analysis"
    },
    
    // Customer Domain
    support: {
      name: "Customer Success Manager",
      avatar: "🎯",
      color: "teal",
      description: "Customer onboarding, retention strategies, and relationship management",
      specialties: ["customer onboarding", "retention analysis", "health scoring", "expansion planning"],
      category: "customer"
    },
    training: {
      name: "Training & Education Specialist", 
      avatar: "🎓",
      color: "blue",
      description: "User education, documentation, and knowledge management",
      specialties: ["course creation", "documentation", "user guides", "video tutorials"],
      category: "customer"
    },
    
    // Product Domain
    product: {
      name: "Product Manager",
      avatar: "🚀",
      color: "purple",
      description: "Product strategy, roadmap planning, and feature prioritization",
      specialties: ["product roadmap", "user research", "feature prioritization", "market analysis"],
      category: "product"
    },
    ux: {
      name: "UX Research Specialist",
      avatar: "🎨",
      color: "pink",
      description: "User experience research, design analysis, and usability testing",
      specialties: ["user interviews", "usability testing", "design systems", "user journey mapping"],
      category: "product"
    },
    
    // Industry Specialists
    healthcare: {
      name: "Healthcare Compliance Expert",
      avatar: "🏥",
      color: "red",
      description: "HIPAA compliance, healthcare regulations, and medical data handling",
      specialties: ["HIPAA compliance", "medical data", "healthcare regulations", "patient privacy"],
      category: "industry"
    },
    fintech: {
      name: "Financial Services Specialist",
      avatar: "🏦",
      color: "blue", 
      description: "Banking regulations, PCI compliance, and financial data security",
      specialties: ["PCI compliance", "banking regulations", "financial APIs", "fraud detection"],
      category: "industry"
    },
    ecommerce: {
      name: "E-commerce Platform Expert",
      avatar: "🛒",
      color: "orange",
      description: "Online retail, inventory management, and payment processing",
      specialties: ["shopping cart", "inventory systems", "payment gateways", "order management"],
      category: "industry"
    },
    saas: {
      name: "SaaS Business Model Expert",
      avatar: "☁️",
      color: "blue",
      description: "Subscription models, SaaS metrics, and platform scaling",
      specialties: ["subscription billing", "SaaS metrics", "multi-tenancy", "platform scaling"],
      category: "industry"
    }
  };

  useEffect(() => {
    let interval;
    
    if (isRunning && currentStep < scenario.steps.length) {
      const currentStepData = scenario.steps[currentStep];
      const stepDuration = currentStepData.duration;
      const agentType = currentStepData.agent;
      
      interval = setInterval(() => {
        setAgentProgress(prev => {
          const newProgress = Math.min(prev[agentType] + (100 / (stepDuration / 100)), 100);
          
          if (newProgress >= 100) {
            setTimeout(() => {
              setCurrentStep(step => step + 1);
              setAgentProgress(prev => ({ ...prev, [agentType]: 0 }));
            }, 500);
          }
          
          return { ...prev, [agentType]: newProgress };
        });
      }, 100);
    }
    
    if (currentStep >= scenario.steps.length) {
      setIsRunning(false);
    }
    
    return () => clearInterval(interval);
  }, [isRunning, currentStep]);

  const startDemo = () => {
    setIsRunning(true);
    setCurrentStep(0);
    setAgentProgress({ technical: 0, billing: 0, competitive: 0, coordinator: 0 });
  };

  const pauseDemo = () => {
    setIsRunning(false);
  };

  const resetDemo = () => {
    setIsRunning(false);
    setCurrentStep(0);
    setAgentProgress({ technical: 0, billing: 0, competitive: 0, coordinator: 0 });
    setMessages([]);
    setEscalationTriggered(false);
    setActiveAgents([]);
  };

  // Chat functionality
  const handleUserQuery = async (query = inputMessage) => {
    if (!query.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsProcessing(true);
    
    // Start orchestration
    await orchestrateAgentResponse(query);
  };

  const orchestrateAgentResponse = async (query) => {
    try {
      // Step 1: Coordinator analyzes the query
      setActiveAgents(['coordinator']);
      const coordinatorMessage = {
        id: Date.now() + 1,
        type: 'agent',
        agent: 'coordinator',
        content: `🧠 **Coordinator Agent**: Analyzing your query and determining required expertise...

**Query Analysis**: "${query}"
**Complexity Assessment**: ${assessQueryComplexity(query)}
**Required Specialists**: ${determineRequiredAgents(query).join(', ')}`,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, coordinatorMessage]);
      await sleep(2000);

      // Step 2: Route to specialized agents
      const requiredAgents = determineRequiredAgents(query);
      setActiveAgents(requiredAgents);

      for (const agentType of requiredAgents) {
        const agentResponse = await getSpecializedResponse(query, agentType);
        const agentMessage = {
          id: Date.now() + Math.random(),
          type: 'agent',
          agent: agentType,
          content: agentResponse,
          timestamp: new Date().toLocaleTimeString()
        };
        
        setMessages(prev => [...prev, agentMessage]);
        await sleep(1500);
      }

      // Step 3: Check for HITL escalation
      const shouldEscalate = await checkEscalation(query, requiredAgents);
      if (shouldEscalate) {
        setEscalationTriggered(true);
        const escalationMessage = {
          id: Date.now() + Math.random(),
          type: 'escalation',
          content: `🚨 **Human Escalation Triggered**: This query requires human expertise due to complexity and multiple technical domains involved.

**Escalation Reason**: Complex multi-domain issue requiring human judgment
**Priority**: High
**Estimated Human Response**: 2-3 minutes
**Agents Involved**: ${requiredAgents.length} specialists

A human expert has been notified and will provide additional guidance.`,
          timestamp: new Date().toLocaleTimeString()
        };
        
        setMessages(prev => [...prev, escalationMessage]);
      }

      // Step 4: Coordinator synthesis
      setTimeout(async () => {
        setActiveAgents(['coordinator']);
        const synthesiMessage = {
          id: Date.now() + Math.random(),
          type: 'agent',
          agent: 'coordinator',
          content: `🧠 **Coordinator Agent**: **Solution Synthesis Complete**

**Multi-Agent Resolution Summary**:
✅ Technical analysis completed by specialist agents
✅ All domain expertise applied to your specific issue  
✅ Coordinated response prevents information silos
${shouldEscalate ? '✅ Human expert notified for complex aspects' : ''}

**Next Steps**: ${generateNextSteps(query, requiredAgents)}

**Resolution Time**: ${(requiredAgents.length * 1.5 + 2).toFixed(1)} minutes (vs 15-30 min traditional support)`,
          timestamp: new Date().toLocaleTimeString()
        };
        
        setMessages(prev => [...prev, synthesiMessage]);
        setActiveAgents([]);
        setIsProcessing(false);
      }, 2000);

    } catch (error) {
      console.error('Orchestration error:', error);
      setIsProcessing(false);
    }
  };

  const assessQueryComplexity = (query) => {
    const complexity = query.length / 100 + (query.split('?').length - 1) * 0.3;
    return complexity > 1 ? 'High' : complexity > 0.5 ? 'Medium' : 'Low';
  };

  const determineRequiredAgents = (query) => {
    const queryLower = query.toLowerCase();
    const selectedAgents = [];
    
    // Technical Domain
    if (queryLower.includes('webhook') || queryLower.includes('api') || queryLower.includes('integration') || queryLower.includes('ssl') || queryLower.includes('timeout') || queryLower.includes('authentication')) {
      selectedAgents.push('technical');
    }
    if (queryLower.includes('deployment') || queryLower.includes('docker') || queryLower.includes('kubernetes') || queryLower.includes('ci/cd') || queryLower.includes('monitoring')) {
      selectedAgents.push('devops');
    }
    if (queryLower.includes('security') || queryLower.includes('vulnerability') || queryLower.includes('encryption') || queryLower.includes('compliance') || queryLower.includes('oauth')) {
      selectedAgents.push('security');
    }
    if (queryLower.includes('database') || queryLower.includes('sql') || queryLower.includes('migration') || queryLower.includes('data model')) {
      selectedAgents.push('database');
    }
    
    // Business Domain
    if (queryLower.includes('billing') || queryLower.includes('payment') || queryLower.includes('subscription') || queryLower.includes('invoice') || queryLower.includes('revenue')) {
      selectedAgents.push('billing');
    }
    if (queryLower.includes('legal') || queryLower.includes('contract') || queryLower.includes('gdpr') || queryLower.includes('terms') || queryLower.includes('privacy')) {
      selectedAgents.push('legal');
    }
    if (queryLower.includes('sales') || queryLower.includes('crm') || queryLower.includes('lead') || queryLower.includes('pipeline') || queryLower.includes('salesforce admin')) {
      selectedAgents.push('sales');
    }
    if (queryLower.includes('marketing') || queryLower.includes('campaign') || queryLower.includes('email') || queryLower.includes('nurturing')) {
      selectedAgents.push('marketing');
    }
    
    // Analysis Domain  
    if (queryLower.includes('competitor') || queryLower.includes('market') || queryLower.includes('agentforce') || queryLower.includes('compare') || queryLower.includes('pricing strategy')) {
      selectedAgents.push('competitive');
    }
    if (queryLower.includes('analytics') || queryLower.includes('dashboard') || queryLower.includes('reporting') || queryLower.includes('kpi') || queryLower.includes('metrics')) {
      selectedAgents.push('data');
    }
    if (queryLower.includes('budget') || queryLower.includes('cost') || queryLower.includes('roi') || queryLower.includes('financial') || queryLower.includes('forecast')) {
      selectedAgents.push('finance');
    }
    
    // Customer Domain
    if (queryLower.includes('customer success') || queryLower.includes('onboarding') || queryLower.includes('retention') || queryLower.includes('churn')) {
      selectedAgents.push('support');
    }
    if (queryLower.includes('training') || queryLower.includes('documentation') || queryLower.includes('tutorial') || queryLower.includes('education')) {
      selectedAgents.push('training');
    }
    
    // Product Domain
    if (queryLower.includes('product') || queryLower.includes('roadmap') || queryLower.includes('feature') || queryLower.includes('user research')) {
      selectedAgents.push('product');
    }
    if (queryLower.includes('ux') || queryLower.includes('user experience') || queryLower.includes('design') || queryLower.includes('usability')) {
      selectedAgents.push('ux');
    }
    
    // Industry Specialists
    if (queryLower.includes('healthcare') || queryLower.includes('hipaa') || queryLower.includes('medical') || queryLower.includes('patient')) {
      selectedAgents.push('healthcare');
    }
    if (queryLower.includes('fintech') || queryLower.includes('banking') || queryLower.includes('pci') || queryLower.includes('financial services')) {
      selectedAgents.push('fintech');
    }
    if (queryLower.includes('ecommerce') || queryLower.includes('shopping') || queryLower.includes('cart') || queryLower.includes('inventory') || queryLower.includes('order')) {
      selectedAgents.push('ecommerce');
    }
    if (queryLower.includes('saas') || queryLower.includes('multi-tenant') || queryLower.includes('subscription model') || queryLower.includes('saas metrics')) {
      selectedAgents.push('saas');
    }
    
    // Remove duplicates and ensure we have at least one agent
    const uniqueAgents = [...new Set(selectedAgents)];
    return uniqueAgents.length > 0 ? uniqueAgents : ['technical'];
  };

  const getSpecializedResponse = async (query, agentType) => {
    const responses = {
      // Technical Domain
      technical: `🔧 **Technical Integration Specialist**: I've analyzed your integration issue and identified the root cause.

**Technical Analysis**:
- API endpoint verification completed
- SSL certificate chain validation
- Authentication flow assessment

**Solution**: Updated integration code with proper error handling and timeout configuration
**Implementation Time**: 15-20 minutes`,

      devops: `⚙️ **DevOps Engineer**: I've reviewed your deployment pipeline and infrastructure setup.

**Infrastructure Analysis**:
- Container orchestration optimized
- CI/CD pipeline configuration reviewed
- Monitoring alerts configured

**Deployment Plan**: Rolling update with zero-downtime deployment strategy
**Timeline**: 30-45 minutes`,

      security: `🛡️ **Security Specialist**: I've completed a security assessment of your request.

**Security Audit Results**:
- Vulnerability scan completed
- Compliance requirements verified
- Encryption protocols validated

**Security Recommendations**: Implemented OAuth 2.0 with PKCE and updated security headers
**Risk Level**: Mitigated to Low`,

      database: `🗄️ **Database Expert**: I've analyzed your database performance and optimization needs.

**Database Analysis**:
- Query performance profiling completed
- Index optimization recommendations
- Data model review finalized

**Optimization Results**: 40% query performance improvement with new indexing strategy
**Migration Time**: 2-3 hours`,

      // Business Domain
      billing: `💳 **Billing & Revenue Expert**: I've reviewed your billing configuration and revenue streams.

**Revenue Analysis**:
- Payment gateway integration verified
- Subscription model optimization
- Tax compliance validation

**Resolution**: Billing discrepancy corrected, automated reconciliation implemented
**Revenue Impact**: $2,400/month optimization`,

      legal: `⚖️ **Legal Compliance Agent**: I've reviewed the legal and compliance aspects of your request.

**Compliance Review**:
- GDPR data handling compliance verified
- Terms of service alignment confirmed
- Contract obligations assessed

**Legal Clearance**: All requirements met, documentation updated per regulations
**Risk Assessment**: Low compliance risk`,

      sales: `📈 **Sales Operations Specialist**: I've analyzed your CRM data and sales process optimization.

**Sales Analysis**:
- Lead scoring model optimization
- Pipeline conversion analysis
- Salesforce configuration review

**Optimization Results**: 25% improvement in lead conversion with updated scoring
**Implementation**: CRM workflow automated`,

      marketing: `📢 **Marketing Automation Expert**: I've reviewed your campaign performance and automation setup.

**Campaign Analysis**:
- Email automation sequences optimized
- Lead nurturing workflows enhanced
- A/B testing results analyzed

**Marketing Results**: 35% increase in engagement with optimized campaign flows
**ROI Improvement**: 180% campaign ROI`,

      // Analysis Domain
      competitive: `📊 **Competitive Intelligence Analyst**: I've completed comprehensive market analysis.

**Market Intelligence**:
- Competitor feature comparison matrix
- Pricing strategy analysis
- Market positioning assessment

**Strategic Insights**: AgentCraft offers 75% cost advantage with superior flexibility
**Competitive Edge**: Custom agent library vs fixed solutions`,

      data: `📈 **Data Analytics Specialist**: I've analyzed your data patterns and created actionable insights.

**Analytics Summary**:
- KPI dashboard updated with real-time metrics
- Predictive model accuracy improved
- Custom reporting pipeline implemented

**Business Impact**: Data-driven decisions enabled, 90% accuracy in forecasting
**Dashboard**: Real-time executive summary available`,

      finance: `💰 **Financial Analyst**: I've completed financial modeling and ROI analysis.

**Financial Assessment**:
- Budget allocation optimization
- Cost-benefit analysis completed
- ROI projections updated

**Financial Results**: 340% ROI projected, $125K annual cost savings identified
**Budget Impact**: 28% operational efficiency gain`,

      // Customer Domain  
      support: `🎯 **Customer Success Manager**: I've analyzed customer health metrics and retention strategies.

**Customer Success Analysis**:
- Health score improvement plan
- Onboarding optimization completed
- Expansion opportunity identification

**Success Metrics**: 92% customer satisfaction, 15% expansion revenue identified
**Retention**: Churn risk reduced by 40%`,

      training: `🎓 **Training & Education Specialist**: I've developed comprehensive training materials.

**Educational Resources**:
- Interactive tutorial series created
- Video training modules produced
- Knowledge base documentation updated

**Learning Outcomes**: 95% user completion rate, 60% reduction in support tickets
**Training Impact**: Accelerated user adoption`,

      // Product Domain
      product: `🚀 **Product Manager**: I've analyzed product requirements and market fit.

**Product Strategy**:
- Feature prioritization matrix updated
- User research insights incorporated
- Product roadmap alignment confirmed

**Product Results**: Feature adoption increased 45%, user satisfaction up 30%
**Roadmap**: Q1 delivery timeline confirmed`,

      ux: `🎨 **UX Research Specialist**: I've completed user experience analysis and design recommendations.

**UX Research Findings**:
- User journey optimization completed
- Usability testing results analyzed
- Design system consistency improved

**UX Improvements**: 50% reduction in user friction, 35% increase in task completion
**Design Impact**: Conversion rate improved 25%`,

      // Industry Specialists
      healthcare: `🏥 **Healthcare Compliance Expert**: I've ensured HIPAA compliance and healthcare regulation adherence.

**Healthcare Compliance**:
- HIPAA risk assessment completed
- Medical data handling protocols verified
- Patient privacy safeguards implemented

**Compliance Status**: 100% HIPAA compliant, audit-ready documentation
**Risk Mitigation**: Healthcare data security optimized`,

      fintech: `🏦 **Financial Services Specialist**: I've reviewed banking regulations and PCI compliance requirements.

**FinTech Analysis**:
- PCI DSS compliance verification
- Banking regulation alignment
- Financial API security assessment

**Compliance Results**: PCI Level 1 compliance achieved, regulatory requirements met
**Security Posture**: Bank-grade security implemented`,

      ecommerce: `🛒 **E-commerce Platform Expert**: I've optimized your online retail operations and payment processing.

**E-commerce Optimization**:
- Shopping cart abandonment analysis
- Payment gateway optimization
- Inventory management automation

**Business Results**: 28% cart conversion improvement, 99.9% payment success rate
**Revenue Impact**: $18K monthly revenue increase`,

      saas: `☁️ **SaaS Business Model Expert**: I've analyzed your SaaS metrics and platform scalability.

**SaaS Analysis**:
- Subscription model optimization
- Multi-tenancy architecture review
- SaaS metrics dashboard creation

**SaaS Results**: 22% MRR growth, 95% uptime achieved, platform scaling optimized
**Business Impact**: Customer acquisition cost reduced 30%`
    };

    const agent = agents[agentType];
    const response = responses[agentType];
    
    if (response) {
      return response;
    }
    
    // Fallback response for any new agents
    return `${agent?.avatar || '🤖'} **${agent?.name || 'Specialist Agent'}**: I've analyzed your request using my specialized expertise in ${agent?.specialties?.slice(0,2).join(' and ') || 'this domain'}.

**Analysis Complete**: Detailed assessment finished with actionable recommendations
**Expertise Applied**: ${agent?.category || 'Specialized'} domain knowledge utilized
**Resolution**: Customized solution developed for your specific requirements

**Next Steps**: Implementation plan ready for immediate deployment`;
  };

  const checkEscalation = async (query, agents) => {
    // Simple escalation logic - escalate if multiple agents and complex query
    return agents.length > 1 && query.length > 100;
  };

  const generateNextSteps = (query, agents) => {
    if (agents.includes('technical')) return 'Implement technical solution and test integration';
    if (agents.includes('billing')) return 'Review updated billing statement and confirm charges';
    if (agents.includes('competitive')) return 'Share competitive analysis with your team';
    return 'Follow up if you need additional assistance';
  };

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const getColorClasses = (color) => {
    const colors = {
      purple: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
      blue: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' },
      green: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' },
      orange: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-200' },
      red: { bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200' },
      gray: { bg: 'bg-gray-100', text: 'text-gray-700', border: 'border-gray-200' },
      pink: { bg: 'bg-pink-100', text: 'text-pink-700', border: 'border-pink-200' },
      teal: { bg: 'bg-teal-100', text: 'text-teal-700', border: 'border-teal-200' }
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Multi-Agent Orchestration Demo</h2>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Submit a query and watch specialized agents collaborate in real-time to analyze, triage, and resolve complex issues.
        </p>
      </div>

      {/* Interactive Chat Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chat Interface */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b bg-gradient-to-r from-blue-50 to-purple-50">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Brain className="w-6 h-6 mr-2 text-blue-600" />
              Multi-Agent Query Interface
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Ask about technical issues, billing, or competitive analysis
            </p>
          </div>
          
          {/* Messages */}
          <div className="h-96 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-gray-500 py-8">
                <Users className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>Try queries like:</p>
                <div className="mt-4 space-y-2 text-sm">
                  <button
                    onClick={() => setInputMessage("We need HIPAA compliance review for our healthcare platform, database migration planning, and security audit for patient data handling")}
                    className="block mx-auto px-3 py-1 bg-red-50 text-red-700 rounded-full hover:bg-red-100 transition-colors"
                  >
                    Healthcare compliance + security + database
                  </button>
                  <button
                    onClick={() => setInputMessage("Our e-commerce site needs PCI compliance, payment gateway optimization, and UX research for checkout conversion")}
                    className="block mx-auto px-3 py-1 bg-orange-50 text-orange-700 rounded-full hover:bg-orange-100 transition-colors"
                  >
                    E-commerce platform optimization
                  </button>
                  <button
                    onClick={() => setInputMessage("Need SaaS metrics analysis, competitive intelligence on market positioning, and marketing automation for lead nurturing")}
                    className="block mx-auto px-3 py-1 bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors"
                  >
                    SaaS growth strategy
                  </button>
                  <button
                    onClick={() => setInputMessage("DevOps pipeline optimization, database performance tuning, and financial ROI analysis for infrastructure costs")}
                    className="block mx-auto px-3 py-1 bg-green-50 text-green-700 rounded-full hover:bg-green-100 transition-colors"
                  >
                    Technical infrastructure + financial analysis
                  </button>
                  <button
                    onClick={() => setInputMessage("Product roadmap planning, customer success onboarding optimization, and training documentation for new features")}
                    className="block mx-auto px-3 py-1 bg-purple-50 text-purple-700 rounded-full hover:bg-purple-100 transition-colors"
                  >
                    Product + customer success
                  </button>
                </div>
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg p-4 ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white ml-12'
                      : message.type === 'escalation'
                      ? 'bg-orange-100 text-orange-800 mr-12 border border-orange-200'
                      : 'bg-white text-gray-800 mr-12 border border-gray-200 shadow-sm'
                  }`}
                >
                  <div className="flex items-start">
                    {message.type === 'user' ? (
                      <User className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
                    ) : message.type === 'escalation' ? (
                      <AlertTriangle className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0 text-orange-600" />
                    ) : (
                      <div className="mr-2 mt-0.5">
                        <span className="text-2xl">{agents[message.agent]?.avatar || '🤖'}</span>
                      </div>
                    )}
                    
                    <div className="flex-1">
                      {message.type === 'agent' && (
                        <div className="text-xs text-gray-500 mb-2">
                          <strong>{agents[message.agent]?.name}</strong> • 
                          {message.timestamp}
                        </div>
                      )}

                      <div className="whitespace-pre-wrap text-sm">
                        {message.content}
                      </div>

                      {message.type !== 'user' && (
                        <div className="text-xs text-gray-400 mt-2">
                          {message.timestamp}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {isProcessing && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 rounded-lg p-4 mr-12 border border-gray-200">
                  <div className="flex items-center">
                    <Brain className="h-5 w-5 mr-2 text-blue-600" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                      <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                    </div>
                    <span className="ml-2 text-sm">Orchestrating agents...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleUserQuery()}
                placeholder="Describe your multi-domain issue (technical, billing, competitive)..."
                className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isProcessing}
              />
              <button
                onClick={() => handleUserQuery()}
                disabled={isProcessing || !inputMessage.trim()}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
            
            <div className="flex justify-between items-center mt-3">
              <p className="text-xs text-gray-500">
                Multi-agent orchestration with HITL escalation
              </p>
              
              <button
                onClick={resetDemo}
                className="text-xs text-gray-500 hover:text-gray-700 flex items-center"
              >
                <RotateCcw className="w-3 h-3 mr-1" />
                Clear Chat
              </button>
            </div>
          </div>
        </div>

        {/* Agent Library Overview */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center justify-between">
              Agent Library ({Object.keys(agents).length} specialists)
              <span className="text-sm font-normal text-gray-500">vs AgentForce's 7 fixed agents</span>
            </h3>
            <p className="text-sm text-gray-600">Dynamic agent assignment from comprehensive specialist library</p>
          </div>
          
          <div className="p-4">
            {/* Active Agents */}
            {activeAgents.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2 flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></div>
                  Active Agents ({activeAgents.length})
                </h4>
                <div className="space-y-2">
                  {activeAgents.map(agentType => {
                    const agent = agents[agentType];
                    const colors = getColorClasses(agent.color);
                    return (
                      <div key={agentType} className={`p-3 rounded-lg border-2 ${colors.border} ${colors.bg}`}>
                        <div className="flex items-center">
                          <span className="text-lg mr-2">{agent.avatar}</span>
                          <div className="flex-1">
                            <h5 className={`font-medium text-sm ${colors.text}`}>{agent.name}</h5>
                            <p className="text-xs text-gray-600">{agent.specialties.slice(0,2).join(', ')}</p>
                          </div>
                          <span className={`px-2 py-1 text-xs rounded-full ${colors.bg} ${colors.text} border ${colors.border}`}>
                            {agent.category}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            
            {/* Agent Categories Overview */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              {['technical', 'business', 'analysis', 'customer', 'product', 'industry'].map(category => {
                const categoryAgents = Object.entries(agents).filter(([_, agent]) => agent.category === category);
                const isActive = activeAgents.some(agentType => agents[agentType]?.category === category);
                
                return (
                  <div key={category} className={`p-2 rounded border ${
                    isActive ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'
                  }`}>
                    <div className="font-medium text-gray-700 capitalize mb-1">
                      {category} ({categoryAgents.length})
                      {isActive && <span className="ml-1 w-1 h-1 bg-green-400 rounded-full inline-block animate-pulse"></span>}
                    </div>
                    <div className="text-gray-600">
                      {categoryAgents.slice(0,3).map(([_, agent]) => agent.avatar).join(' ')}
                      {categoryAgents.length > 3 && '...'}
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* HITL Status */}
            {escalationTriggered && (
              <div className="mt-4 p-3 bg-orange-50 border-2 border-orange-200 rounded-lg">
                <div className="flex items-center">
                  <AlertTriangle className="w-5 h-5 text-orange-600 mr-2" />
                  <div className="flex-1">
                    <h4 className="font-medium text-orange-900 text-sm">HITL Escalation Active</h4>
                    <p className="text-xs text-orange-700">Human expert engaged for complex multi-domain issue</p>
                  </div>
                </div>
              </div>
            )}
            
            {/* Library Stats */}
            <div className="mt-4 pt-3 border-t border-gray-200">
              <div className="grid grid-cols-3 gap-4 text-center text-xs">
                <div>
                  <div className="font-semibold text-blue-600">{Object.keys(agents).length}</div>
                  <div className="text-gray-600">Total Agents</div>
                </div>
                <div>
                  <div className="font-semibold text-green-600">6</div>
                  <div className="text-gray-600">Categories</div>
                </div>
                <div>
                  <div className="font-semibold text-purple-600">∞</div>
                  <div className="text-gray-600">Customizable</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Agent Benefits */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-center mb-4">
          <CheckCircle className="w-8 h-8 mr-3" />
          <h3 className="text-2xl font-bold">Multi-Agent Orchestration Benefits</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-6">
          <div>
            <h4 className="font-semibold mb-2">📚 Comprehensive Library</h4>
            <ul className="space-y-1 text-sm">
              <li>• {Object.keys(agents).length} specialized agents vs AgentForce's 7</li>
              <li>• 6 domain categories with deep expertise</li>
              <li>• Industry-specific specialists (healthcare, fintech, e-commerce, SaaS)</li>
              <li>• Infinitely customizable and extensible</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">🎯 Dynamic Assignment</h4>
            <ul className="space-y-1 text-sm">
              <li>• Intelligent query analysis</li>
              <li>• Multi-agent coordination</li>
              <li>• Context-aware specialist routing</li>
              <li>• Real-time expertise matching</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">🚨 HITL Integration</h4>
            <ul className="space-y-1 text-sm">
              <li>• Automatic complexity detection</li>
              <li>• Human expert escalation</li>
              <li>• Seamless handoff processes</li>
              <li>• Continuous learning loops</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">⚡ Competitive Edge</h4>
            <ul className="space-y-1 text-sm">
              <li>• Custom agents vs fixed templates</li>
              <li>• Domain expertise depth</li>
              <li>• Single interaction resolution</li>
              <li>• 85% cost reduction vs platforms</li>
            </ul>
          </div>
        </div>

        {messages.length > 0 && (
          <div className="mt-6 p-4 bg-white/20 rounded-lg">
            <h4 className="font-semibold mb-2">Current Session Results:</h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold">{messages.filter(m => m.type === 'user').length}</p>
                <p className="text-xs opacity-90">User Queries</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{messages.filter(m => m.type === 'agent').length}</p>
                <p className="text-xs opacity-90">Agent Responses</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{escalationTriggered ? 'Yes' : 'No'}</p>
                <p className="text-xs opacity-90">HITL Triggered</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MultiAgentDemo;
