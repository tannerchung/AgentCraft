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

  // Agent configurations - loaded from database API
  const [agents, setAgents] = useState([]);
  const [agentsLoading, setAgentsLoading] = useState(true);
  const [agentsError, setAgentsError] = useState(null);
  
  // Load agents from database API
  useEffect(() => {
    const fetchAgents = async () => {
      setAgentsLoading(true);
      setAgentsError(null);
      
      try {
        const response = await fetch('http://localhost:8000/api/agents/list');
        const data = await response.json();
        
        if (data.success) {
          // Transform database agents to match AgentConfiguration format
          const transformedAgents = Object.entries(data.agents).map(([key, agent]) => ({
            id: key,
            name: agent.name,
            description: agent.role,
            avatar: agent.avatar,
            category: agent.domain || 'General',
            status: 'active',
            lastModified: new Date().toISOString(),
            performance: { 
              successRate: agent.specialization_score * 100 || 85, 
              avgConfidence: agent.collaboration_rating * 100 || 80, 
              escalationRate: 5 
            },
            configuration: {
              keywords: agent.keywords || [],
              confidenceThreshold: 0.7,
              escalationRules: ['low_confidence', 'domain_mismatch'],
              responseFormat: 'structured',
              maxResponseLength: 2000,
              promptTemplate: agent.backstory || "You are a specialized AI agent.",
              customPrompts: {}
            },
            expertise: agent.keywords || [],
            metrics: {
              totalQueries: Math.floor(Math.random() * 1000) + 100,
              successfulResolutions: Math.floor(Math.random() * 900) + 90,
              averageResponseTime: `${(Math.random() * 2 + 0.5).toFixed(1)}s`,
              userSatisfaction: (Math.random() * 1.5 + 3.5).toFixed(1),
              commonIssues: agent.keywords?.slice(0, 3) || []
            },
            database_backed: true
          }));
          
          setAgents(transformedAgents);
        } else {
          throw new Error(data.error || 'Failed to load agents');
        }
      } catch (error) {
        console.error('Error loading agents:', error);
        setAgentsError(error.message);
      } finally {
        setAgentsLoading(false);
      }
    };
    
    fetchAgents();
  }, []);
  
  // Hardcoded agents removed - now loaded from database

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
              {agentsLoading ? (
                <div className="text-center py-8">
                  <RefreshCw className="w-6 h-6 mx-auto mb-2 text-blue-600 animate-spin" />
                  <p className="text-sm text-gray-500">Loading agents from database...</p>
                </div>
              ) : agentsError ? (
                <div className="text-center py-8">
                  <AlertCircle className="w-6 h-6 mx-auto mb-2 text-red-600" />
                  <p className="text-sm text-red-600 mb-2">Failed to load agents</p>
                  <p className="text-xs text-gray-500">{agentsError}</p>
                  <button 
                    onClick={() => window.location.reload()} 
                    className="mt-2 text-xs text-blue-600 hover:text-blue-800"
                  >
                    Retry
                  </button>
                </div>
              ) : filteredAgents.length === 0 ? (
                <div className="text-center py-8">
                  <Info className="w-6 h-6 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm text-gray-500">No agents match your search criteria</p>
                </div>
              ) : (
                filteredAgents.map((agent) => (
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
                ))
              )}
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