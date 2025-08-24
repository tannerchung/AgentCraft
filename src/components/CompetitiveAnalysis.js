
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { TrendingUp, DollarSign, Clock, Shield, Zap, AlertTriangle } from 'lucide-react';
import { apiService } from '../services/api';

const CompetitiveAnalysis = () => {
  const [selectedCompetitor, setSelectedCompetitor] = useState('salesforce');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [blockedScenario, setBlockedScenario] = useState(false);

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

  useEffect(() => {
    loadCompetitiveAnalysis();
  }, [selectedCompetitor]);

  const loadCompetitiveAnalysis = async () => {
    setLoading(true);
    try {
      const data = await apiService.getCompetitiveAnalysis(selectedCompetitor);
      setAnalysisData(data);
    } catch (error) {
      console.error('Failed to load competitive analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const simulateBlockedScenario = () => {
    setBlockedScenario(true);
    setTimeout(() => setBlockedScenario(false), 5000);
  };

  const currentCompetitor = competitors.find(c => c.id === selectedCompetitor);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Competitive Analysis</h2>
          <p className="text-gray-600 mt-2">Real-time competitive intelligence and positioning</p>
        </div>
        <button
          onClick={simulateBlockedScenario}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center"
        >
          <Shield className="w-4 h-4 mr-2" />
          Simulate "Blocked by Guardrails"
        </button>
      </div>

      {/* Blocked Scenario Alert */}
      {blockedScenario && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-red-900">AgentForce Response: Blocked by Guardrails</h3>
              <p className="text-red-700 mt-1">
                "I'm sorry, but I cannot provide competitive analysis or discuss other vendors due to platform restrictions and guardrails."
              </p>
            </div>
          </div>
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <Zap className="w-5 h-5 text-green-600 mr-2" />
              <span className="font-medium text-green-900">AgentCraft Response:</span>
            </div>
            <p className="text-green-800 mt-2">
              "I can provide comprehensive competitive analysis, including detailed comparisons, market positioning, 
              and strategic recommendations. My specialized competitive intelligence capabilities are unrestricted."
            </p>
          </div>
        </div>
      )}

      {/* Competitor Selection */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Select Competitor</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
              <div className="text-3xl mb-2">{competitor.logo}</div>
              <div className="text-sm font-medium text-gray-900">{competitor.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Live Comparison Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Bar Chart Comparison */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900">
              AgentCraft vs {currentCompetitor?.name}
            </h3>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-salesforce-blue rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">AgentCraft</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-gray-400 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">{currentCompetitor?.name}</span>
              </div>
            </div>
          </div>
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

      {/* Detailed Analysis */}
      {analysisData && !loading && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Strengths & Weaknesses */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              {currentCompetitor?.name} Analysis
            </h3>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-green-700 mb-2">Strengths</h4>
                <ul className="space-y-1">
                  {analysisData.analysis.strengths.map((strength, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-center">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-red-700 mb-2">Weaknesses</h4>
                <ul className="space-y-1">
                  {analysisData.analysis.weaknesses.map((weakness, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-center">
                      <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
                      {weakness}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Our Advantages */}
          <div className="bg-gradient-to-br from-salesforce-blue to-salesforce-darkblue rounded-lg shadow-sm p-6 text-white">
            <h3 className="text-xl font-semibold mb-4">Our Competitive Advantages</h3>
            <ul className="space-y-3">
              {analysisData.our_advantages.map((advantage, index) => (
                <li key={index} className="flex items-start">
                  <Zap className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm">{advantage}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Market Metrics */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Market Metrics</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Market Share</span>
                <span className="font-semibold">{analysisData.analysis.market_share}%</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Pricing Level</span>
                <span className="font-semibold">{analysisData.analysis.pricing}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Customization Score</span>
                <span className="font-semibold">{analysisData.analysis.customization_score}/10</span>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t">
              <h4 className="font-medium text-gray-900 mb-2">Recommended Positioning</h4>
              <p className="text-sm text-gray-600">{analysisData.recommended_positioning}</p>
            </div>
          </div>
        </div>
      )}

      {/* Cost Impact Calculator */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">ROI Calculator</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <DollarSign className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-green-700">67%</p>
            <p className="text-sm text-gray-600">Cost Reduction</p>
          </div>
          
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-blue-700">89%</p>
            <p className="text-sm text-gray-600">Faster Implementation</p>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <TrendingUp className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-purple-700">4.8/5</p>
            <p className="text-sm text-gray-600">Customer Satisfaction</p>
          </div>
          
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <Zap className="w-8 h-8 text-orange-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-orange-700">24x</p>
            <p className="text-sm text-gray-600">Faster Customization</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitiveAnalysis;
