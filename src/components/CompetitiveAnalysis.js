
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { Shield, TrendingUp, AlertTriangle, CheckCircle, X } from 'lucide-react';
import apiService from '../services/api';

const CompetitiveAnalysis = () => {
  const [selectedCompetitor, setSelectedCompetitor] = useState('salesforce');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [blockedScenario, setBlockedScenario] = useState(false);
  const [error, setError] = useState(null);

  const competitors = [
    { id: 'salesforce', name: 'Salesforce AgentForce', logo: '☁️', color: '#00A1E0' },
    { id: 'zendesk', name: 'Zendesk', logo: '🎧', color: '#03363D' },
    { id: 'microsoft', name: 'Microsoft Dynamics', logo: '🔷', color: '#0078D4' },
    { id: 'custom', name: 'Custom Solutions', logo: '⚙️', color: '#6B7280' }
  ];

  const comparisonMetrics = [
    { metric: 'Implementation Speed', agentcraft: 95, competitor: 45 },
    { metric: 'Customization Capability', agentcraft: 98, competitor: 52 },
    { metric: 'Domain Expertise', agentcraft: 96, competitor: 58 },
    { metric: 'Cost Efficiency', agentcraft: 89, competitor: 62 },
    { metric: 'Time to Value', agentcraft: 92, competitor: 48 }
  ];

  const radarData = [
    { subject: 'Technical Depth', agentcraft: 96, competitor: 58, fullMark: 100 },
    { subject: 'Flexibility', agentcraft: 98, competitor: 45, fullMark: 100 },
    { subject: 'Speed', agentcraft: 95, competitor: 52, fullMark: 100 },
    { subject: 'Cost', agentcraft: 89, competitor: 72, fullMark: 100 },
    { subject: 'Scalability', agentcraft: 87, competitor: 78, fullMark: 100 },
    { subject: 'Support', agentcraft: 94, competitor: 85, fullMark: 100 }
  ];

  // Fallback data for when API is not available
  const fallbackAnalysisData = {
    salesforce: {
      strengths: [
        "Established enterprise presence",
        "Comprehensive CRM integration",
        "Large ecosystem of apps",
        "Strong brand recognition"
      ],
      weaknesses: [
        "Limited customization for specialized use cases",
        "High complexity for simple implementations",
        "Expensive licensing model",
        "Slow deployment for custom solutions"
      ],
      positioning: {
        title: "AgentCraft vs Salesforce AgentForce",
        summary: "While Salesforce offers broad enterprise solutions, AgentCraft provides specialized, domain-specific expertise that can be rapidly deployed and customized.",
        keyDifferentiators: [
          "Specialized domain knowledge vs general-purpose responses",
          "Rapid customization vs lengthy implementation cycles",
          "Cost-effective specialized agents vs expensive enterprise licensing",
          "Direct technical solutions vs generic guidance"
        ]
      },
      marketShare: 23.5,
      customerSatisfaction: 3.7,
      avgImplementationTime: 180
    },
    zendesk: {
      strengths: [
        "User-friendly interface",
        "Strong ticketing system",
        "Good integration capabilities",
        "Reasonable pricing for basic features"
      ],
      weaknesses: [
        "Limited AI capabilities",
        "Basic automation features",
        "Not suitable for complex technical issues",
        "Limited customization options"
      ],
      positioning: {
        title: "AgentCraft vs Zendesk",
        summary: "Zendesk excels at ticket management, but AgentCraft provides intelligent, specialized problem-solving capabilities.",
        keyDifferentiators: [
          "AI-driven solutions vs manual ticket routing",
          "Technical expertise vs general support",
          "Proactive problem solving vs reactive ticketing",
          "Specialized knowledge base vs generic responses"
        ]
      },
      marketShare: 15.2,
      customerSatisfaction: 4.1,
      avgImplementationTime: 30
    },
    microsoft: {
      strengths: [
        "Integration with Office 365",
        "Enterprise security features",
        "Familiar Microsoft ecosystem",
        "Comprehensive business tools"
      ],
      weaknesses: [
        "Complex setup and configuration",
        "Limited AI specialization",
        "Expensive for small to medium businesses",
        "Generic support capabilities"
      ],
      positioning: {
        title: "AgentCraft vs Microsoft Dynamics",
        summary: "Microsoft provides broad business tools, while AgentCraft offers focused, intelligent agent capabilities.",
        keyDifferentiators: [
          "Specialized AI agents vs general business tools",
          "Rapid deployment vs complex setup",
          "Domain-specific expertise vs generic functionality",
          "Cost-effective solutions vs enterprise licensing"
        ]
      },
      marketShare: 18.7,
      customerSatisfaction: 3.9,
      avgImplementationTime: 120
    },
    custom: {
      strengths: [
        "Fully customizable solutions",
        "Complete control over features",
        "No vendor lock-in",
        "Can be highly optimized"
      ],
      weaknesses: [
        "High development costs",
        "Long implementation time",
        "Requires technical expertise",
        "Ongoing maintenance burden"
      ],
      positioning: {
        title: "AgentCraft vs Custom Solutions",
        summary: "Custom solutions offer flexibility but require significant investment. AgentCraft provides specialized capabilities with rapid deployment.",
        keyDifferentiators: [
          "Pre-built specialized agents vs custom development",
          "Rapid deployment vs long development cycles",
          "Lower total cost of ownership vs high development costs",
          "Proven solutions vs experimental implementations"
        ]
      },
      marketShare: 42.6,
      customerSatisfaction: 3.5,
      avgImplementationTime: 365
    }
  };

  useEffect(() => {
    loadCompetitiveAnalysis();
  }, [selectedCompetitor]);

  const loadCompetitiveAnalysis = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiService.getCompetitiveAnalysis(selectedCompetitor);
      setAnalysisData(data);
    } catch (error) {
      console.error('Competitive Analysis API Error:', error);
      setError('API not available - using demo data');
      // Use fallback data when API is not available
      setAnalysisData(fallbackAnalysisData[selectedCompetitor]);
    } finally {
      setLoading(false);
    }
  };

  const simulateBlockedScenario = () => {
    setBlockedScenario(true);
    setTimeout(() => setBlockedScenario(false), 5000);
  };

  const currentCompetitor = competitors.find(c => c.id === selectedCompetitor);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-salesforce-blue mx-auto mb-4"></div>
          <p className="text-gray-600">Loading competitive analysis...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Competitive Analysis</h2>
          <p className="text-gray-600 mt-2">Real-time competitive intelligence and positioning</p>
          {error && (
            <p className="text-amber-600 text-sm mt-1 flex items-center">
              <AlertTriangle className="w-4 h-4 mr-1" />
              {error}
            </p>
          )}
        </div>
        <button
          onClick={simulateBlockedScenario}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center"
        >
          <Shield className="w-4 h-4 mr-2" />
          Simulate "Blocked by Guardrails"
        </button>
      </div>

      {/* Blocked Scenario Overlay */}
      {blockedScenario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-8 max-w-md mx-4">
            <div className="text-center">
              <X className="w-16 h-16 text-red-600 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h3>
              <p className="text-gray-600 mb-4">
                "I cannot provide competitive intelligence as it may violate our usage policies regarding competitive analysis."
              </p>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-left">
                <p className="text-sm text-red-800">
                  <strong>Typical GenAI Response:</strong> Generic guardrails prevent specialized competitive analysis, limiting business intelligence capabilities.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Competitor Selection */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {competitors.map((competitor) => (
          <button
            key={competitor.id}
            onClick={() => setSelectedCompetitor(competitor.id)}
            className={`p-4 rounded-lg border-2 transition-all ${
              selectedCompetitor === competitor.id
                ? 'border-salesforce-blue bg-salesforce-lightblue'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
          >
            <div className="text-center">
              <span className="text-3xl mb-2 block">{competitor.logo}</span>
              <h3 className="font-medium text-gray-900">{competitor.name}</h3>
            </div>
          </button>
        ))}
      </div>

      {/* Analysis Content */}
      {analysisData && (
        <>
          {/* Competitive Positioning */}
          <div className="bg-gradient-to-r from-salesforce-blue to-salesforce-darkblue rounded-lg shadow-lg p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">{analysisData.positioning?.title || `AgentCraft vs ${currentCompetitor?.name}`}</h3>
            <p className="text-lg opacity-90 mb-6">
              {analysisData.positioning?.summary || "Competitive analysis summary not available."}
            </p>
            
            {analysisData.positioning?.keyDifferentiators && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysisData.positioning.keyDifferentiators.map((differentiator, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <CheckCircle className="w-5 h-5 mt-1 flex-shrink-0" />
                    <span className="text-sm">{differentiator}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
                {currentCompetitor?.name} Strengths
              </h3>
              <ul className="space-y-3">
                {(analysisData.strengths || []).map((strength, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 text-amber-600 mr-2" />
                {currentCompetitor?.name} Weaknesses
              </h3>
              <ul className="space-y-3">
                {(analysisData.weaknesses || []).map((weakness, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <div className="w-2 h-2 bg-amber-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">{weakness}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Performance Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Performance Comparison</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={comparisonMetrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="agentcraft" fill="#0176d3" name="AgentCraft" />
                  <Bar dataKey="competitor" fill="#9ca3af" name={currentCompetitor?.name} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Radar Chart */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">Capability Matrix</h3>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar
                    name="AgentCraft"
                    dataKey="agentcraft"
                    stroke="#0176d3"
                    fill="#0176d3"
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                  <Radar
                    name={currentCompetitor?.name}
                    dataKey="competitor"
                    stroke="#9ca3af"
                    fill="#9ca3af"
                    fillOpacity={0.1}
                    strokeWidth={2}
                  />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Market Statistics */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">Market Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">{analysisData.marketShare || 'N/A'}%</p>
                <p className="text-gray-600">Market Share</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">{analysisData.customerSatisfaction || 'N/A'}/5.0</p>
                <p className="text-gray-600">Customer Satisfaction</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-gray-900">{analysisData.avgImplementationTime || 'N/A'}</p>
                <p className="text-gray-600">Avg Implementation (days)</p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* AgentCraft Advantages */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-lg p-8 text-white">
        <h3 className="text-2xl font-bold mb-6">AgentCraft Competitive Advantages</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <TrendingUp className="w-8 h-8 mx-auto mb-3" />
            <p className="font-semibold mb-2">Specialized Expertise</p>
            <p className="text-sm opacity-90">Domain-specific knowledge vs generic responses</p>
          </div>
          <div className="text-center">
            <CheckCircle className="w-8 h-8 mx-auto mb-3" />
            <p className="font-semibold mb-2">Rapid Deployment</p>
            <p className="text-sm opacity-90">Hours vs months for customization</p>
          </div>
          <div className="text-center">
            <Shield className="w-8 h-8 mx-auto mb-3" />
            <p className="font-semibold mb-2">Cost Efficiency</p>
            <p className="text-sm opacity-90">67% reduction in support costs</p>
          </div>
          <div className="text-center">
            <AlertTriangle className="w-8 h-8 mx-auto mb-3" />
            <p className="font-semibold mb-2">No Guardrail Blocks</p>
            <p className="text-sm opacity-90">Full competitive intelligence access</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitiveAnalysis;
