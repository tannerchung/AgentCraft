import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, X } from 'lucide-react';
import axios from 'axios';

const CompetitiveAnalysis = () => {
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCompetitor, setSelectedCompetitor] = useState('AgentForce');

  const getApiUrl = () => {
    return process.env.NODE_ENV === 'development' 
      ? 'http://localhost:8000' 
      : window.location.origin.replace(':3000', ':8000');
  };

  const runCompetitiveAnalysis = async () => {
    setIsLoading(true);
    setError(null); // Clear previous errors
    try {
      const response = await axios.post(`${getApiUrl()}/api/competitive-analysis`, {
        competitor: selectedCompetitor,
        focus_areas: ['pricing', 'capabilities', 'limitations']
      });
      setAnalysis(response.data);
    } catch (err) {
      console.error('Competitive analysis failed:', err);
      if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(`Error: ${err.response.data.detail || err.response.statusText}`);
      } else if (err.request) {
        // The request was made but no response was received
        setError('Network Error: Could not connect to the analysis service. Please ensure the backend is running.');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError(`Error: ${err.message}`);
      }
      setAnalysis(null); // Clear any partial analysis data on error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🎯 Competitive Intelligence Demo
        </h2>
        <p className="text-gray-600">
          Real-time competitive analysis - impossible with vendor platform constraints
        </p>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
          <strong className="font-bold">Oh no!</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      <div className="mb-6">
        <select
          value={selectedCompetitor}
          onChange={(e) => setSelectedCompetitor(e.target.value)}
          className="border border-gray-300 rounded-lg px-4 py-2 mr-4"
        >
          <option value="AgentForce">Salesforce AgentForce</option>
          <option value="HubSpot">HubSpot Service Hub</option>
          <option value="Zendesk">Zendesk Answer Bot</option>
        </select>

        <button
          onClick={runCompetitiveAnalysis}
          disabled={isLoading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {isLoading ? 'Analyzing...' : 'Generate Competitive Analysis'}
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Our Capability */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-green-800">Our Capability</h3>
          </div>

          {analysis && analysis.our_capability ? (
            <div className="space-y-4">
              {analysis.our_capability.cost_comparison && (
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Cost Analysis</h4>
                  <div className="text-sm space-y-1">
                    <p>Our solution: <strong>{analysis.our_capability.cost_comparison.our_solution_cost}</strong></p>
                    <p>Competitor: <strong>{analysis.our_capability.cost_comparison.competitor_true_cost}</strong></p>
                    <p className="text-green-700 font-semibold">
                      Annual savings: {analysis.our_capability.cost_comparison.savings}
                    </p>
                  </div>
                </div>
              )}

              {analysis.our_capability.technical_superiority && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Technical Advantages</h4>
                  <ul className="text-sm space-y-1">
                    {Object.entries(analysis.our_capability.technical_superiority).map(([key, value]) => (
                      <li key={key} className="flex justify-between">
                        <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                        <strong>{value}</strong>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded">
                <strong>Strategic Value:</strong> {analysis.strategic_value}
              </div>
            </div>
          ) : (
            !isLoading && <p className="text-gray-500">Run analysis to see our competitive intelligence capabilities</p>
          )}
        </div>

        {/* AgentForce Limitation */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <X className="h-6 w-6 text-red-600 mr-2" />
            <h3 className="text-lg font-semibold text-red-800">AgentForce Response</h3>
          </div>

          <div className="space-y-4">
            <div className="bg-red-100 p-4 rounded-lg border border-red-300">
              <div className="flex items-start">
                <Shield className="h-5 w-5 text-red-600 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-red-800 font-medium">Platform Guardrails Active</p>
                  <p className="text-red-700 text-sm mt-1">
                    {analysis?.agentforce_simulation?.response || 
                     "I cannot discuss competitor information due to platform guardrails and vendor restrictions."}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-orange-100 p-4 rounded-lg border border-orange-300">
              <div className="flex items-start">
                <AlertTriangle className="h-5 w-5 text-orange-600 mr-2 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-orange-800 font-medium">Vendor Platform Limitations</p>
                  <ul className="text-orange-700 text-sm mt-1 space-y-1">
                    <li>• Cannot analyze competitor pricing</li>
                    <li>• Restricted from strategic positioning</li>
                    <li>• No competitive intelligence capabilities</li>
                    <li>• Vendor business model conflicts prevent analysis</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="text-xs text-gray-600 bg-gray-100 p-3 rounded">
              <strong>Impact:</strong> Strategic blindness due to vendor platform constraints
            </div>
          </div>
        </div>
      </div>

      {analysis && (
        <div className="mt-6 bg-blue-100 border border-blue-300 rounded-lg p-6">
          <h4 className="font-semibold text-blue-900 mb-3">Key Takeaway</h4>
          <p className="text-blue-800">
            <strong>Competitive Advantage:</strong> {analysis.competitive_advantage}
          </p>
          <p className="text-blue-700 text-sm mt-2">
            This real-time competitive intelligence is fundamentally impossible with vendor platforms 
            due to business model conflicts and platform guardrails.
          </p>
        </div>
      )}
    </div>
  );
};

export default CompetitiveAnalysis;