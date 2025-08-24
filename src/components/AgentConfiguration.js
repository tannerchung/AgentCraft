import React, { useState, useEffect } from 'react';
import { 
  Settings, Search, Edit3, Copy, Trash2, Plus, Save, X, 
  Eye, Code, TestTube, BarChart3, ArrowRight, AlertCircle,
  CheckCircle, Info, Download, Upload, RefreshCw
} from 'lucide-react';
import QueryAnalyzer from './QueryAnalyzer';

const AgentConfiguration = () => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editForm, setEditForm] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // overview, query-analysis, configuration

  // Agent configurations (currently stored in memory - would come from PostgreSQL in production)
  const [agents, setAgents] = useState([
    // Technical Domain
    {
      id: 'technical',
      name: 'Technical Integration Specialist',
      description: 'APIs, webhooks, SSL, authentication, and system integrations',
      avatar: '🔧',
      category: 'Technical',
      status: 'active',
      lastModified: '2024-08-20T10:30:00Z',
      performance: { successRate: 94.5, avgConfidence: 89.2, escalationRate: 3.8 },
      configuration: {
        keywords: ['webhook', 'api', 'integration', 'ssl', 'authentication', 'timeout', 'certificate'],
        confidenceThreshold: 0.7,
        escalationRules: ['low_confidence', 'security_context', 'multiple_failures'],
        responseFormat: 'structured',
        maxResponseLength: 2000,
        promptTemplate: "You are a senior technical integration specialist. Analyze the technical issue and provide specific, actionable solutions with code examples when appropriate.",
        customPrompts: {
          webhook_issues: "Focus on webhook signature validation, SSL certificates, and retry logic",
          api_integration: "Provide REST API best practices and authentication troubleshooting",
          ssl_problems: "Analyze certificate chains, TLS versions, and security protocols"
        }
      },
      expertise: ['Webhook debugging', 'API authentication', 'SSL certificates', 'System architecture'],
      metrics: {
        totalQueries: 1247,
        successfulResolutions: 1178,
        averageResponseTime: '1.2s',
        userSatisfaction: 4.6,
        topKeywords: ['webhook', 'ssl', 'api', 'timeout', 'authentication']
      }
    },
    {
      id: 'devops',
      name: 'DevOps Engineer',
      description: 'Deployment, infrastructure, monitoring, and performance optimization',
      avatar: '⚙️',
      category: 'Technical',
      status: 'active',
      lastModified: '2024-08-19T09:15:00Z',
      performance: { successRate: 92.1, avgConfidence: 87.4, escalationRate: 4.2 },
      configuration: {
        keywords: ['deployment', 'docker', 'kubernetes', 'ci/cd', 'monitoring', 'infrastructure', 'pipeline'],
        confidenceThreshold: 0.7,
        escalationRules: ['low_confidence', 'production_critical', 'security_context'],
        responseFormat: 'structured',
        maxResponseLength: 2500,
        promptTemplate: "You are a senior DevOps engineer. Provide infrastructure solutions with deployment strategies and monitoring best practices.",
        customPrompts: {
          deployment_issues: "Focus on CI/CD pipelines, containerization, and zero-downtime deployment",
          monitoring_setup: "Provide comprehensive monitoring and alerting configurations",
          infrastructure_scaling: "Analyze scaling strategies and performance optimization"
        }
      },
      expertise: ['CI/CD', 'Docker', 'Kubernetes', 'Monitoring', 'Performance tuning'],
      metrics: {
        totalQueries: 892,
        successfulResolutions: 821,
        averageResponseTime: '1.5s',
        userSatisfaction: 4.4,
        topKeywords: ['docker', 'kubernetes', 'deployment', 'monitoring', 'pipeline']
      }
    },
    {
      id: 'security',
      name: 'Security Specialist',
      description: 'Security audits, compliance, vulnerability assessment, and encryption',
      avatar: '🛡️',
      category: 'Technical',
      status: 'active',
      lastModified: '2024-08-18T14:15:00Z',
      performance: { successRate: 96.8, avgConfidence: 92.1, escalationRate: 2.1 },
      configuration: {
        keywords: ['security', 'vulnerability', 'encryption', 'compliance', 'oauth', 'gdpr', 'audit'],
        confidenceThreshold: 0.8,
        escalationRules: ['legal_compliance', 'high_risk_assessment', 'regulatory_requirements'],
        responseFormat: 'detailed',
        maxResponseLength: 3000,
        promptTemplate: "You are a cybersecurity expert. Provide thorough security analysis with compliance considerations and risk assessments.",
        customPrompts: {
          vulnerability_assessment: "Conduct systematic security evaluation with risk scoring",
          compliance_review: "Ensure GDPR, HIPAA, and industry-specific compliance requirements",
          security_audit: "Provide comprehensive security audit with actionable recommendations"
        }
      },
      expertise: ['Penetration testing', 'GDPR compliance', 'OAuth', 'Encryption'],
      metrics: {
        totalQueries: 674,
        successfulResolutions: 652,
        averageResponseTime: '1.8s',
        userSatisfaction: 4.8,
        topKeywords: ['security', 'gdpr', 'compliance', 'vulnerability', 'oauth']
      }
    },
    {
      id: 'database',
      name: 'Database Expert',
      description: 'Database design, optimization, migrations, and data modeling',
      avatar: '🗄️',
      category: 'Technical',
      status: 'active',
      lastModified: '2024-08-17T11:30:00Z',
      performance: { successRate: 91.7, avgConfidence: 88.9, escalationRate: 5.1 },
      configuration: {
        keywords: ['database', 'sql', 'migration', 'optimization', 'query', 'index', 'schema'],
        confidenceThreshold: 0.7,
        escalationRules: ['low_confidence', 'data_loss_risk', 'performance_critical'],
        responseFormat: 'structured',
        maxResponseLength: 2200,
        promptTemplate: "You are a database expert. Provide database solutions with optimization strategies and migration plans.",
        customPrompts: {
          query_optimization: "Focus on SQL query performance, indexing strategies, and execution plans",
          database_migration: "Provide zero-downtime migration strategies and data validation",
          schema_design: "Design efficient database schemas and data modeling best practices"
        }
      },
      expertise: ['SQL optimization', 'Database migrations', 'Data modeling', 'Performance tuning'],
      metrics: {
        totalQueries: 548,
        successfulResolutions: 502,
        averageResponseTime: '2.1s',
        userSatisfaction: 4.3,
        topKeywords: ['sql', 'database', 'query', 'optimization', 'migration']
      }
    },

    // Business Domain
    {
      id: 'billing',
      name: 'Billing & Revenue Expert',
      description: 'Payment processing, subscription management, revenue recognition',
      avatar: '💳',
      category: 'Business',
      status: 'active',
      lastModified: '2024-08-16T16:45:00Z',
      performance: { successRate: 95.2, avgConfidence: 90.1, escalationRate: 3.1 },
      configuration: {
        keywords: ['billing', 'payment', 'subscription', 'invoice', 'revenue', 'refund', 'dunning'],
        confidenceThreshold: 0.75,
        escalationRules: ['revenue_impact', 'legal_compliance', 'customer_escalation'],
        responseFormat: 'structured',
        maxResponseLength: 1800,
        promptTemplate: "You are a billing and revenue expert. Provide solutions for payment processing and subscription management.",
        customPrompts: {
          payment_failures: "Focus on payment gateway issues, retry logic, and dunning management",
          subscription_changes: "Handle subscription upgrades, downgrades, and prorations",
          revenue_recognition: "Ensure proper revenue accounting and compliance"
        }
      },
      expertise: ['Payment gateways', 'Subscription models', 'Revenue analytics', 'Tax compliance'],
      metrics: {
        totalQueries: 723,
        successfulResolutions: 689,
        averageResponseTime: '1.4s',
        userSatisfaction: 4.7,
        topKeywords: ['payment', 'subscription', 'billing', 'refund', 'invoice']
      }
    },
    {
      id: 'legal',
      name: 'Legal Compliance Agent',
      description: 'Contract analysis, compliance requirements, and legal documentation',
      avatar: '⚖️',
      category: 'Business',
      status: 'active',
      lastModified: '2024-08-15T13:20:00Z',
      performance: { successRate: 97.3, avgConfidence: 94.5, escalationRate: 1.8 },
      configuration: {
        keywords: ['legal', 'contract', 'compliance', 'gdpr', 'privacy', 'terms', 'policy'],
        confidenceThreshold: 0.85,
        escalationRules: ['legal_risk', 'regulatory_compliance', 'contract_disputes'],
        responseFormat: 'detailed',
        maxResponseLength: 3500,
        promptTemplate: "You are a legal compliance expert. Provide thorough legal analysis with risk assessments and compliance guidance.",
        customPrompts: {
          contract_review: "Analyze contract terms, risks, and compliance requirements",
          privacy_compliance: "Ensure GDPR, CCPA, and data protection compliance",
          policy_drafting: "Draft legal policies and terms of service"
        }
      },
      expertise: ['Contract review', 'GDPR', 'Data privacy', 'Terms of service'],
      metrics: {
        totalQueries: 234,
        successfulResolutions: 228,
        averageResponseTime: '2.8s',
        userSatisfaction: 4.9,
        topKeywords: ['gdpr', 'contract', 'compliance', 'privacy', 'legal']
      }
    },
    {
      id: 'sales',
      name: 'Sales Operations Specialist',
      description: 'CRM management, lead qualification, and sales process optimization',
      avatar: '📈',
      category: 'Business',
      status: 'active',
      lastModified: '2024-08-14T10:10:00Z',
      performance: { successRate: 89.6, avgConfidence: 85.7, escalationRate: 6.2 },
      configuration: {
        keywords: ['sales', 'crm', 'lead', 'pipeline', 'salesforce', 'qualification', 'territory'],
        confidenceThreshold: 0.7,
        escalationRules: ['low_confidence', 'revenue_impact', 'customer_escalation'],
        responseFormat: 'structured',
        maxResponseLength: 2000,
        promptTemplate: "You are a sales operations expert. Provide CRM solutions and sales process optimizations.",
        customPrompts: {
          crm_configuration: "Configure Salesforce CRM for optimal sales workflows",
          lead_scoring: "Implement lead scoring models and qualification processes",
          sales_analytics: "Create sales dashboards and performance tracking"
        }
      },
      expertise: ['Salesforce admin', 'Lead scoring', 'Sales analytics', 'Pipeline management'],
      metrics: {
        totalQueries: 445,
        successfulResolutions: 399,
        averageResponseTime: '1.6s',
        userSatisfaction: 4.2,
        topKeywords: ['salesforce', 'lead', 'pipeline', 'crm', 'sales']
      }
    },
    {
      id: 'marketing',
      name: 'Marketing Automation Expert',
      description: 'Campaign management, lead nurturing, and marketing technology',
      avatar: '📢',
      category: 'Business',
      status: 'active',
      lastModified: '2024-08-13T14:55:00Z',
      performance: { successRate: 92.8, avgConfidence: 88.3, escalationRate: 4.7 },
      configuration: {
        keywords: ['marketing', 'campaign', 'automation', 'email', 'lead', 'nurturing', 'attribution'],
        confidenceThreshold: 0.7,
        escalationRules: ['low_confidence', 'campaign_critical', 'attribution_complex'],
        responseFormat: 'structured',
        maxResponseLength: 2100,
        promptTemplate: "You are a marketing automation expert. Provide campaign strategies and marketing technology solutions.",
        customPrompts: {
          email_automation: "Design email automation workflows and lead nurturing sequences",
          campaign_optimization: "Optimize campaign performance and A/B testing strategies",
          attribution_tracking: "Implement marketing attribution and ROI tracking"
        }
      },
      expertise: ['Email campaigns', 'Lead nurturing', 'Marketing analytics', 'A/B testing'],
      metrics: {
        totalQueries: 612,
        successfulResolutions: 568,
        averageResponseTime: '1.7s',
        userSatisfaction: 4.4,
        topKeywords: ['email', 'campaign', 'automation', 'nurturing', 'marketing']
      }
    },

    // Analysis Domain
    {
      id: 'competitive',
      name: 'Competitive Intelligence Analyst',
      description: 'Market research, competitor analysis, and strategic positioning',
      avatar: '📊',
      category: 'Analysis',
      status: 'active',
      lastModified: '2024-08-12T09:30:00Z',
      performance: { successRate: 93.4, avgConfidence: 89.7, escalationRate: 4.1 },
      configuration: {
        keywords: ['competitive', 'competitor', 'market', 'analysis', 'positioning', 'strategy', 'intelligence'],
        confidenceThreshold: 0.75,
        escalationRules: ['strategic_impact', 'market_sensitive', 'executive_request'],
        responseFormat: 'detailed',
        maxResponseLength: 2800,
        promptTemplate: "You are a competitive intelligence analyst. Provide comprehensive market analysis and strategic insights.",
        customPrompts: {
          competitor_analysis: "Analyze competitor strengths, weaknesses, and market positioning",
          market_research: "Provide market trends analysis and opportunity assessment",
          strategic_positioning: "Develop competitive differentiation and positioning strategies"
        }
      },
      expertise: ['Market research', 'Competitor analysis', 'Pricing strategy', 'SWOT analysis'],
      metrics: {
        totalQueries: 378,
        successfulResolutions: 353,
        averageResponseTime: '2.3s',
        userSatisfaction: 4.6,
        topKeywords: ['competitor', 'market', 'analysis', 'positioning', 'strategy']
      }
    },
    {
      id: 'data',
      name: 'Data Analytics Specialist',
      description: 'Business intelligence, reporting, and predictive analytics',
      avatar: '📈',
      category: 'Analysis',
      status: 'active',
      lastModified: '2024-08-11T15:45:00Z',
      performance: { successRate: 90.3, avgConfidence: 86.8, escalationRate: 5.9 },
      configuration: {
        keywords: ['analytics', 'data', 'dashboard', 'reporting', 'kpi', 'metrics', 'intelligence'],
        confidenceThreshold: 0.7,
        escalationRules: ['data_quality', 'complex_analysis', 'executive_reporting'],
        responseFormat: 'structured',
        maxResponseLength: 2400,
        promptTemplate: "You are a data analytics expert. Provide business intelligence solutions and data-driven insights.",
        customPrompts: {
          dashboard_creation: "Design executive dashboards with key performance indicators",
          data_analysis: "Perform statistical analysis and predictive modeling",
          reporting_automation: "Automate business reporting and data pipelines"
        }
      },
      expertise: ['SQL queries', 'Dashboard creation', 'Predictive modeling', 'KPI tracking'],
      metrics: {
        totalQueries: 689,
        successfulResolutions: 622,
        averageResponseTime: '1.9s',
        userSatisfaction: 4.3,
        topKeywords: ['dashboard', 'analytics', 'data', 'kpi', 'reporting']
      }
    },
    {
      id: 'finance',
      name: 'Financial Analyst',
      description: 'Financial modeling, budgeting, forecasting, and cost analysis',
      avatar: '💰',
      category: 'Analysis',
      status: 'active',
      lastModified: '2024-08-10T12:20:00Z',
      performance: { successRate: 94.7, avgConfidence: 91.2, escalationRate: 3.3 },
      configuration: {
        keywords: ['financial', 'budget', 'forecast', 'roi', 'cost', 'revenue', 'modeling'],
        confidenceThreshold: 0.8,
        escalationRules: ['financial_impact', 'executive_decision', 'regulatory_compliance'],
        responseFormat: 'detailed',
        maxResponseLength: 2600,
        promptTemplate: "You are a financial analyst. Provide comprehensive financial analysis with modeling and forecasting.",
        customPrompts: {
          financial_modeling: "Create financial models for ROI analysis and forecasting",
          budget_planning: "Develop budget plans with variance analysis and controls",
          cost_analysis: "Analyze cost structures and optimization opportunities"
        }
      },
      expertise: ['ROI analysis', 'Budget planning', 'Cost modeling', 'Financial forecasting'],
      metrics: {
        totalQueries: 312,
        successfulResolutions: 295,
        averageResponseTime: '2.2s',
        userSatisfaction: 4.8,
        topKeywords: ['budget', 'roi', 'forecast', 'financial', 'cost']
      }
    },

    // Customer Domain
    {
      id: 'support',
      name: 'Customer Success Manager',
      description: 'Customer onboarding, retention strategies, and relationship management',
      avatar: '🎯',
      category: 'Customer',
      status: 'active',
      lastModified: '2024-08-09T11:15:00Z',
      performance: { successRate: 96.1, avgConfidence: 92.3, escalationRate: 2.8 },
      configuration: {
        keywords: ['customer', 'success', 'onboarding', 'retention', 'churn', 'satisfaction', 'engagement'],
        confidenceThreshold: 0.75,
        escalationRules: ['customer_at_risk', 'executive_escalation', 'retention_critical'],
        responseFormat: 'structured',
        maxResponseLength: 2200,
        promptTemplate: "You are a customer success expert. Provide strategies for customer onboarding, retention, and relationship management.",
        customPrompts: {
          onboarding_optimization: "Design customer onboarding processes for maximum success",
          retention_strategy: "Develop customer retention and churn prevention strategies",
          health_scoring: "Implement customer health scoring and engagement tracking"
        }
      },
      expertise: ['Customer onboarding', 'Retention analysis', 'Health scoring', 'Expansion planning'],
      metrics: {
        totalQueries: 456,
        successfulResolutions: 438,
        averageResponseTime: '1.6s',
        userSatisfaction: 4.7,
        topKeywords: ['onboarding', 'retention', 'churn', 'customer', 'success']
      }
    },
    {
      id: 'training',
      name: 'Training & Education Specialist',
      description: 'User education, documentation, and knowledge management',
      avatar: '🎓',
      category: 'Customer',
      status: 'active',
      lastModified: '2024-08-08T16:30:00Z',
      performance: { successRate: 91.5, avgConfidence: 87.6, escalationRate: 5.2 },
      configuration: {
        keywords: ['training', 'education', 'documentation', 'tutorial', 'knowledge', 'learning', 'guide'],
        confidenceThreshold: 0.7,
        escalationRules: ['content_accuracy', 'technical_complexity', 'user_feedback'],
        responseFormat: 'structured',
        maxResponseLength: 2300,
        promptTemplate: "You are a training and education expert. Provide comprehensive learning solutions and documentation strategies.",
        customPrompts: {
          content_creation: "Create training materials, tutorials, and user guides",
          documentation_strategy: "Develop documentation frameworks and knowledge bases",
          learning_optimization: "Optimize learning experiences and user adoption"
        }
      },
      expertise: ['Course creation', 'Documentation', 'User guides', 'Video tutorials'],
      metrics: {
        totalQueries: 334,
        successfulResolutions: 305,
        averageResponseTime: '1.8s',
        userSatisfaction: 4.4,
        topKeywords: ['documentation', 'tutorial', 'training', 'guide', 'education']
      }
    },

    // Product Domain
    {
      id: 'product',
      name: 'Product Manager',
      description: 'Product strategy, roadmap planning, and feature prioritization',
      avatar: '🚀',
      category: 'Product',
      status: 'active',
      lastModified: '2024-08-07T13:45:00Z',
      performance: { successRate: 88.9, avgConfidence: 84.2, escalationRate: 7.1 },
      configuration: {
        keywords: ['product', 'roadmap', 'feature', 'strategy', 'requirements', 'user', 'market'],
        confidenceThreshold: 0.7,
        escalationRules: ['strategic_decision', 'resource_allocation', 'market_impact'],
        responseFormat: 'structured',
        maxResponseLength: 2500,
        promptTemplate: "You are a product management expert. Provide strategic product guidance and roadmap planning.",
        customPrompts: {
          roadmap_planning: "Develop product roadmaps with feature prioritization frameworks",
          user_research: "Analyze user research and market feedback for product decisions",
          feature_specification: "Create detailed feature specifications and requirements"
        }
      },
      expertise: ['Product roadmap', 'User research', 'Feature prioritization', 'Market analysis'],
      metrics: {
        totalQueries: 567,
        successfulResolutions: 504,
        averageResponseTime: '2.0s',
        userSatisfaction: 4.2,
        topKeywords: ['roadmap', 'feature', 'product', 'user', 'strategy']
      }
    },
    {
      id: 'ux',
      name: 'UX Research Specialist',
      description: 'User experience research, design analysis, and usability testing',
      avatar: '🎨',
      category: 'Product',
      status: 'active',
      lastModified: '2024-08-06T10:25:00Z',
      performance: { successRate: 93.7, avgConfidence: 89.4, escalationRate: 4.3 },
      configuration: {
        keywords: ['ux', 'user', 'design', 'usability', 'research', 'interface', 'experience'],
        confidenceThreshold: 0.75,
        escalationRules: ['design_complexity', 'user_impact', 'accessibility_compliance'],
        responseFormat: 'structured',
        maxResponseLength: 2400,
        promptTemplate: "You are a UX research expert. Provide user experience insights and design recommendations.",
        customPrompts: {
          usability_testing: "Design and conduct usability testing with actionable insights",
          user_research: "Perform user research and behavioral analysis",
          design_optimization: "Optimize user interfaces for better user experience"
        }
      },
      expertise: ['User interviews', 'Usability testing', 'Design systems', 'User journey mapping'],
      metrics: {
        totalQueries: 423,
        successfulResolutions: 396,
        averageResponseTime: '1.7s',
        userSatisfaction: 4.6,
        topKeywords: ['usability', 'design', 'user', 'interface', 'experience']
      }
    },

    // Industry Specialists
    {
      id: 'healthcare',
      name: 'Healthcare Compliance Expert',
      description: 'HIPAA compliance, healthcare regulations, and medical data handling',
      avatar: '🏥',
      category: 'Industry',
      status: 'active',
      lastModified: '2024-08-05T14:10:00Z',
      performance: { successRate: 98.2, avgConfidence: 95.7, escalationRate: 1.3 },
      configuration: {
        keywords: ['healthcare', 'hipaa', 'medical', 'patient', 'compliance', 'phi', 'regulation'],
        confidenceThreshold: 0.9,
        escalationRules: ['regulatory_compliance', 'patient_safety', 'legal_requirement'],
        responseFormat: 'detailed',
        maxResponseLength: 3200,
        promptTemplate: "You are a healthcare compliance expert. Provide thorough analysis of HIPAA and healthcare regulations.",
        customPrompts: {
          hipaa_compliance: "Ensure complete HIPAA compliance with risk assessments",
          medical_data: "Handle medical data with privacy and security best practices",
          healthcare_regulations: "Navigate healthcare regulations and compliance requirements"
        }
      },
      expertise: ['HIPAA compliance', 'Medical data', 'Healthcare regulations', 'Patient privacy'],
      metrics: {
        totalQueries: 156,
        successfulResolutions: 153,
        averageResponseTime: '2.5s',
        userSatisfaction: 4.9,
        topKeywords: ['hipaa', 'compliance', 'medical', 'patient', 'healthcare']
      }
    },
    {
      id: 'fintech',
      name: 'Financial Services Specialist',
      description: 'Banking regulations, PCI compliance, and financial data security',
      avatar: '🏦',
      category: 'Industry',
      status: 'active',
      lastModified: '2024-08-04T09:55:00Z',
      performance: { successRate: 97.1, avgConfidence: 93.8, escalationRate: 1.9 },
      configuration: {
        keywords: ['fintech', 'banking', 'pci', 'financial', 'regulation', 'compliance', 'security'],
        confidenceThreshold: 0.85,
        escalationRules: ['regulatory_compliance', 'financial_risk', 'security_breach'],
        responseFormat: 'detailed',
        maxResponseLength: 3000,
        promptTemplate: "You are a financial services expert. Provide comprehensive guidance on banking regulations and financial compliance.",
        customPrompts: {
          pci_compliance: "Ensure PCI DSS compliance with comprehensive security measures",
          banking_regulations: "Navigate banking regulations and financial compliance requirements",
          financial_security: "Implement financial data security and fraud prevention"
        }
      },
      expertise: ['PCI compliance', 'Banking regulations', 'Financial APIs', 'Fraud detection'],
      metrics: {
        totalQueries: 289,
        successfulResolutions: 281,
        averageResponseTime: '2.1s',
        userSatisfaction: 4.8,
        topKeywords: ['pci', 'banking', 'compliance', 'financial', 'security']
      }
    },
    {
      id: 'ecommerce',
      name: 'E-commerce Platform Expert',
      description: 'Online retail, inventory management, and payment processing',
      avatar: '🛒',
      category: 'Industry',
      status: 'active',
      lastModified: '2024-08-03T12:40:00Z',
      performance: { successRate: 91.8, avgConfidence: 88.1, escalationRate: 4.9 },
      configuration: {
        keywords: ['ecommerce', 'retail', 'shopping', 'cart', 'inventory', 'payment', 'order'],
        confidenceThreshold: 0.75,
        escalationRules: ['revenue_impact', 'customer_experience', 'payment_issues'],
        responseFormat: 'structured',
        maxResponseLength: 2300,
        promptTemplate: "You are an e-commerce expert. Provide solutions for online retail operations and customer experience optimization.",
        customPrompts: {
          cart_optimization: "Optimize shopping cart experience and conversion rates",
          inventory_management: "Implement inventory management and fulfillment strategies",
          payment_processing: "Configure payment gateways and checkout optimization"
        }
      },
      expertise: ['Shopping cart', 'Inventory systems', 'Payment gateways', 'Order management'],
      metrics: {
        totalQueries: 634,
        successfulResolutions: 582,
        averageResponseTime: '1.5s',
        userSatisfaction: 4.4,
        topKeywords: ['cart', 'payment', 'inventory', 'order', 'shopping']
      }
    },
    {
      id: 'saas',
      name: 'SaaS Business Model Expert',
      description: 'Subscription models, SaaS metrics, and platform scaling',
      avatar: '☁️',
      category: 'Industry',
      status: 'active',
      lastModified: '2024-08-02T15:20:00Z',
      performance: { successRate: 90.4, avgConfidence: 86.9, escalationRate: 5.6 },
      configuration: {
        keywords: ['saas', 'subscription', 'metrics', 'scaling', 'tenant', 'churn', 'mrr'],
        confidenceThreshold: 0.75,
        escalationRules: ['business_critical', 'scaling_issues', 'revenue_impact'],
        responseFormat: 'structured',
        maxResponseLength: 2400,
        promptTemplate: "You are a SaaS business expert. Provide guidance on subscription models, metrics, and platform scaling.",
        customPrompts: {
          saas_metrics: "Analyze SaaS metrics including MRR, churn, and customer lifetime value",
          subscription_billing: "Implement subscription billing models and pricing strategies",
          platform_scaling: "Scale multi-tenant SaaS platforms for growth"
        }
      },
      expertise: ['Subscription billing', 'SaaS metrics', 'Multi-tenancy', 'Platform scaling'],
      metrics: {
        totalQueries: 445,
        successfulResolutions: 402,
        averageResponseTime: '1.8s',
        userSatisfaction: 4.3,
        topKeywords: ['saas', 'subscription', 'metrics', 'mrr', 'churn']
      }
    }
  ]);

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = searchTerm === '' || 
      agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.configuration.keywords.some(keyword => 
        keyword.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesCategory = selectedCategory === 'All' || agent.category === selectedCategory;
    
    return matchesSearch && matchesCategory;
  });

  const categories = ['All', ...new Set(agents.map(agent => agent.category))];

  const handleEditAgent = (agent) => {
    setEditForm({ ...agent });
    setIsEditing(true);
  };

  const handleSaveAgent = () => {
    if (editForm) {
      setAgents(prev => prev.map(agent => 
        agent.id === editForm.id ? editForm : agent
      ));
      setSelectedAgent(editForm);
      setIsEditing(false);
      setEditForm(null);
    }
  };

  const handleTestQuery = async () => {
    if (!testQuery.trim() || !selectedAgent) return;
    
    // Simulate query analysis
    const keywords = selectedAgent.configuration.keywords;
    const matchedKeywords = keywords.filter(keyword => 
      testQuery.toLowerCase().includes(keyword.toLowerCase())
    );
    
    const confidence = Math.min(95, (matchedKeywords.length / keywords.length) * 100 + Math.random() * 20);
    
    setTestResults({
      query: testQuery,
      matchedKeywords,
      confidence: confidence.toFixed(1),
      wouldTrigger: confidence > (selectedAgent.configuration.confidenceThreshold * 100),
      alternativeAgents: agents.filter(a => a.id !== selectedAgent.id).slice(0, 2),
      estimatedResponse: confidence > 70 ? 'High quality response expected' : 'May require escalation'
    });
  };

  const handleDuplicateAgent = (agent) => {
    const newAgent = {
      ...agent,
      id: `${agent.id}_copy_${Date.now()}`,
      name: `${agent.name} (Copy)`,
      status: 'draft',
      lastModified: new Date().toISOString()
    };
    setAgents(prev => [...prev, newAgent]);
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Settings className="w-8 h-8 mr-3 text-blue-600" />
          Agent Configuration
        </h1>
        <p className="text-gray-600 mt-2">
          Configure, customize, and optimize your AI agent library
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Agent List */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="px-6 py-4 border-b">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Agent Library</h2>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 text-sm flex items-center"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  New Agent
                </button>
              </div>
              
              {/* Search and Filter */}
              <div className="space-y-3">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search agents or keywords..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                  />
                </div>
                
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* Agent Cards */}
            <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
              {filteredAgents.map((agent) => (
                <div
                  key={agent.id}
                  className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                    selectedAgent?.id === agent.id ? 'bg-blue-50 border-r-2 border-r-blue-500' : ''
                  }`}
                  onClick={() => setSelectedAgent(agent)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start">
                      <span className="text-2xl mr-3">{agent.avatar}</span>
                      <div>
                        <h3 className="font-medium text-gray-900">{agent.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{agent.category}</p>
                        <div className="flex items-center mt-2 space-x-4 text-xs text-gray-500">
                          <span className="flex items-center">
                            <div className={`w-2 h-2 rounded-full mr-1 ${
                              agent.status === 'active' ? 'bg-green-400' : 
                              agent.status === 'draft' ? 'bg-yellow-400' : 'bg-red-400'
                            }`}></div>
                            {agent.status}
                          </span>
                          <span>{agent.performance.successRate.toFixed(1)}% success</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex space-x-1">
                      <button
                        onClick={(e) => {e.stopPropagation(); handleEditAgent(agent);}}
                        className="p-1 text-gray-400 hover:text-blue-600"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => {e.stopPropagation(); handleDuplicateAgent(agent);}}
                        className="p-1 text-gray-400 hover:text-green-600"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Configuration Details */}
        <div className="lg:col-span-2">
          {selectedAgent ? (
            <div className="space-y-6">
              {/* Tab Navigation */}
              <div className="bg-white rounded-lg shadow-sm border">
                <div className="border-b border-gray-200">
                  <nav className="flex space-x-8 px-6">
                    {[
                      { id: 'overview', name: 'Overview', icon: BarChart3 },
                      { id: 'query-analysis', name: 'Query Analysis', icon: TestTube },
                      { id: 'configuration', name: 'Configuration', icon: Code }
                    ].map((tab) => {
                      const Icon = tab.icon;
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                            activeTab === tab.id
                              ? 'border-blue-500 text-blue-600'
                              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                          }`}
                        >
                          <Icon className="w-4 h-4 mr-2" />
                          {tab.name}
                        </button>
                      );
                    })}
                  </nav>
                </div>
              </div>

              {/* Tab Content */}
              {activeTab === 'overview' && (
                <>
              {/* Agent Overview */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-start">
                    <span className="text-4xl mr-4">{selectedAgent.avatar}</span>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{selectedAgent.name}</h2>
                      <p className="text-gray-600 mt-1">{selectedAgent.description}</p>
                      <div className="flex items-center mt-3 space-x-4">
                        <span className={`px-3 py-1 rounded-full text-sm ${
                          selectedAgent.status === 'active' ? 'bg-green-100 text-green-800' :
                          selectedAgent.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {selectedAgent.status}
                        </span>
                        <span className="text-sm text-gray-500">
                          Modified: {new Date(selectedAgent.lastModified).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEditAgent(selectedAgent)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center"
                    >
                      <Edit3 className="w-4 h-4 mr-2" />
                      Edit Configuration
                    </button>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {selectedAgent.performance.successRate}%
                    </div>
                    <div className="text-sm text-gray-600">Success Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {selectedAgent.performance.avgConfidence}%
                    </div>
                    <div className="text-sm text-gray-600">Avg Confidence</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {selectedAgent.performance.escalationRate}%
                    </div>
                    <div className="text-sm text-gray-600">Escalation Rate</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600">
                      {selectedAgent.metrics?.totalQueries || 0}
                    </div>
                    <div className="text-sm text-gray-600">Total Queries</div>
                  </div>
                </div>
              </div>

              {/* Query Analysis & Testing */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <TestTube className="w-5 h-5 mr-2 text-green-600" />
                  Query Analysis & Testing
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Test Query
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={testQuery}
                        onChange={(e) => setTestQuery(e.target.value)}
                        placeholder="Enter a query to test against this agent..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                      <button
                        onClick={handleTestQuery}
                        disabled={!testQuery.trim()}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center"
                      >
                        <TestTube className="w-4 h-4 mr-1" />
                        Test
                      </button>
                    </div>
                  </div>

                  {testResults && (
                    <div className="mt-4 p-4 border rounded-lg bg-gray-50">
                      <h4 className="font-medium text-gray-900 mb-3">Analysis Results:</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Confidence Score:</span>
                          <span className={`font-semibold ${
                            parseFloat(testResults.confidence) > 70 ? 'text-green-600' : 'text-yellow-600'
                          }`}>
                            {testResults.confidence}%
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">Would Trigger:</span>
                          <span className={`font-semibold ${
                            testResults.wouldTrigger ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {testResults.wouldTrigger ? 'Yes' : 'No'}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-600">Matched Keywords:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {testResults.matchedKeywords.map(keyword => (
                              <span key={keyword} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>

                </>
              )}

              {/* Query Analysis Tab */}
              {activeTab === 'query-analysis' && (
                <QueryAnalyzer 
                  query={testQuery}
                  agents={agents}
                  onQueryChange={setTestQuery}
                />
              )}

              {/* Configuration Tab */}
              {activeTab === 'configuration' && (
                <div className="bg-white rounded-lg shadow-sm border p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Code className="w-5 h-5 mr-2 text-purple-600" />
                    Configuration Details
                  </h3>
                  
                  <div className="space-y-6">
                    {/* Keywords */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Trigger Keywords
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {selectedAgent.configuration.keywords.map((keyword, index) => (
                          <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Thresholds */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Confidence Threshold
                        </label>
                        <div className="text-2xl font-bold text-blue-600">
                          {(selectedAgent.configuration.confidenceThreshold * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Max Response Length
                        </label>
                        <div className="text-2xl font-bold text-green-600">
                          {selectedAgent.configuration.maxResponseLength}
                        </div>
                      </div>
                    </div>

                    {/* Escalation Rules */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Escalation Rules
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {selectedAgent.configuration.escalationRules.map((rule, index) => (
                          <span key={index} className="px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full">
                            {rule.replace('_', ' ')}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Prompt Template */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Prompt Template
                      </label>
                      <div className="bg-gray-100 p-3 rounded-lg text-sm text-gray-700">
                        {selectedAgent.configuration.promptTemplate}
                      </div>
                    </div>

                    {/* Custom Prompts */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Custom Prompts by Context
                      </label>
                      <div className="space-y-3">
                        {Object.entries(selectedAgent.configuration.customPrompts).map(([context, prompt]) => (
                          <div key={context} className="border rounded-lg p-3">
                            <h6 className="font-medium text-sm text-gray-900 mb-2">
                              {context.replace('_', ' ').toUpperCase()}
                            </h6>
                            <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                              {prompt}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
              <Settings className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-900 mb-2">
                Select an Agent to Configure
              </h3>
              <p className="text-gray-600">
                Choose an agent from the library to view and modify its configuration
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {isEditing && editForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <h3 className="text-xl font-semibold text-gray-900">
                Edit Agent Configuration
              </h3>
              <button
                onClick={() => setIsEditing(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Agent Name
                  </label>
                  <input
                    type="text"
                    value={editForm.name}
                    onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    value={editForm.category}
                    onChange={(e) => setEditForm({...editForm, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Technical">Technical</option>
                    <option value="Business">Business</option>
                    <option value="Analysis">Analysis</option>
                    <option value="Customer">Customer</option>
                    <option value="Product">Product</option>
                    <option value="Industry">Industry</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Keywords */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Trigger Keywords (comma-separated)
                </label>
                <input
                  type="text"
                  value={editForm.configuration.keywords.join(', ')}
                  onChange={(e) => setEditForm({
                    ...editForm,
                    configuration: {
                      ...editForm.configuration,
                      keywords: e.target.value.split(',').map(k => k.trim()).filter(k => k)
                    }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Confidence Threshold */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confidence Threshold: {(editForm.configuration.confidenceThreshold * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.1"
                  value={editForm.configuration.confidenceThreshold}
                  onChange={(e) => setEditForm({
                    ...editForm,
                    configuration: {
                      ...editForm.configuration,
                      confidenceThreshold: parseFloat(e.target.value)
                    }
                  })}
                  className="w-full"
                />
              </div>

              {/* Prompt Template */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prompt Template
                </label>
                <textarea
                  value={editForm.configuration.promptTemplate}
                  onChange={(e) => setEditForm({
                    ...editForm,
                    configuration: {
                      ...editForm.configuration,
                      promptTemplate: e.target.value
                    }
                  })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 p-6 border-t">
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveAgent}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
              >
                <Save className="w-4 h-4 mr-2" />
                Save Configuration
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentConfiguration;