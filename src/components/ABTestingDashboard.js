import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Play, Pause, RotateCcw, TrendingUp, Users, Zap,
  CheckCircle, XCircle, AlertTriangle, Info, Settings
} from 'lucide-react';
import axios from 'axios';

const ABTestingDashboard = () => {
  const [experiments, setExperiments] = useState([]);
  const [activeExperiment, setActiveExperiment] = useState(null);
  const [experimentResults, setExperimentResults] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  
  useEffect(() => {
    initializeExperiments();
    fetchExperimentResults();
  }, []);

  const initializeExperiments = () => {
    const mockExperiments = [
      {
        id: 'exp_001',
        name: 'Confidence Threshold Optimization',
        description: 'Testing different confidence thresholds for HITL escalation',
        status: 'active',
        variants: [
          { id: 'control', name: 'Current (0.7)', allocation: 50, metrics: { conversions: 245, escalations: 12 } },
          { id: 'variant_a', name: 'Lower (0.6)', allocation: 50, metrics: { conversions: 238, escalations: 18 } }
        ],
        startDate: '2024-08-20',
        endDate: '2024-08-27',
        primaryMetric: 'escalation_rate'
      },
      {
        id: 'exp_002',
        name: 'Response Format A/B Test',
        description: 'Structured vs narrative response formatting',
        status: 'draft',
        variants: [
          { id: 'control', name: 'Current Format', allocation: 50, metrics: { conversions: 0, escalations: 0 } },
          { id: 'variant_b', name: 'Bullet Points', allocation: 50, metrics: { conversions: 0, escalations: 0 } }
        ],
        startDate: '2024-08-25',
        endDate: '2024-09-01',
        primaryMetric: 'satisfaction_score'
      },
      {
        id: 'exp_003',
        name: 'Vector Search Relevance',
        description: 'Testing different similarity thresholds for knowledge base search',
        status: 'completed',
        variants: [
          { id: 'control', name: 'Threshold 0.8', allocation: 50, metrics: { conversions: 89, escalations: 5 } },
          { id: 'variant_c', name: 'Threshold 0.75', allocation: 50, metrics: { conversions: 94, escalations: 3 } }
        ],
        startDate: '2024-08-10',
        endDate: '2024-08-17',
        primaryMetric: 'resolution_rate',
        result: 'variant_c_winner'
      }
    ];
    
    setExperiments(mockExperiments);
    setActiveExperiment(mockExperiments[0]);
  };

  const fetchExperimentResults = () => {
    // Mock experiment results data
    const mockResults = {
      statistical_significance: 95.2,
      confidence_interval: [0.02, 0.15],
      sample_size: 1247,
      conversion_rate_lift: 8.3,
      revenue_impact: 2340,
      recommendation: 'Deploy variant - statistically significant improvement'
    };
    
    setExperimentResults(mockResults);
  };

  const startExperiment = (experimentId) => {
    setIsRunning(true);
    // In production, this would make API call to start experiment
    console.log(`Starting experiment: ${experimentId}`);
  };

  const stopExperiment = (experimentId) => {
    setIsRunning(false);
    // In production, this would make API call to stop experiment
    console.log(`Stopping experiment: ${experimentId}`);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { bg: 'bg-green-100', text: 'text-green-800', icon: Play },
      draft: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Settings },
      completed: { bg: 'bg-blue-100', text: 'text-blue-800', icon: CheckCircle },
      paused: { bg: 'bg-gray-100', text: 'text-gray-800', icon: Pause }
    };
    
    const config = statusConfig[status] || statusConfig.draft;
    const Icon = config.icon;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const calculateConversionRate = (variant) => {
    const total = variant.metrics.conversions + variant.metrics.escalations;
    return total > 0 ? ((variant.metrics.conversions / total) * 100).toFixed(1) : 0;
  };

  // Chart data for variant comparison
  const variantComparisonData = activeExperiment ? activeExperiment.variants.map(variant => ({
    name: variant.name,
    conversion_rate: parseFloat(calculateConversionRate(variant)),
    escalations: variant.metrics.escalations,
    total_interactions: variant.metrics.conversions + variant.metrics.escalations
  })) : [];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Zap className="w-8 h-8 mr-3 text-yellow-600" />
          A/B Testing Dashboard
        </h1>
        <p className="text-gray-600 mt-2">
          Continuous optimization through data-driven experimentation
        </p>
      </div>

      {/* Experiment List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="px-6 py-4 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Active Experiments</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {experiments.map((experiment) => (
                <div
                  key={experiment.id}
                  className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                    activeExperiment?.id === experiment.id ? 'bg-blue-50 border-r-2 border-r-blue-500' : ''
                  }`}
                  onClick={() => setActiveExperiment(experiment)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{experiment.name}</h3>
                    {getStatusBadge(experiment.status)}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{experiment.description}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{experiment.startDate} - {experiment.endDate}</span>
                    <span>{experiment.variants.length} variants</span>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="p-4 border-t">
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center">
                <Play className="w-4 h-4 mr-2" />
                Create New Experiment
              </button>
            </div>
          </div>
        </div>

        {/* Experiment Details */}
        <div className="lg:col-span-2">
          {activeExperiment && (
            <div className="space-y-6">
              {/* Experiment Header */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">{activeExperiment.name}</h2>
                    <p className="text-gray-600 mt-1">{activeExperiment.description}</p>
                  </div>
                  <div className="flex space-x-3">
                    {activeExperiment.status === 'active' ? (
                      <button
                        onClick={() => stopExperiment(activeExperiment.id)}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors flex items-center"
                      >
                        <Pause className="w-4 h-4 mr-2" />
                        Pause
                      </button>
                    ) : activeExperiment.status === 'draft' ? (
                      <button
                        onClick={() => startExperiment(activeExperiment.id)}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center"
                      >
                        <Play className="w-4 h-4 mr-2" />
                        Start
                      </button>
                    ) : null}
                    
                    <button className="border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center">
                      <RotateCcw className="w-4 h-4 mr-2" />
                      Reset
                    </button>
                  </div>
                </div>
                
                <div className="grid grid-cols-4 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {activeExperiment.variants.reduce((sum, v) => sum + v.metrics.conversions + v.metrics.escalations, 0)}
                    </p>
                    <p className="text-sm text-gray-600">Total Interactions</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {experimentResults?.statistical_significance.toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-600">Statistical Significance</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {experimentResults?.conversion_rate_lift.toFixed(1)}%
                    </p>
                    <p className="text-sm text-gray-600">Conversion Lift</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-orange-600">7d</p>
                    <p className="text-sm text-gray-600">Time Remaining</p>
                  </div>
                </div>
              </div>

              {/* Variant Performance */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Variant Performance</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Conversion Rate Comparison</h4>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={variantComparisonData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="conversion_rate" fill="#0088FE" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Traffic Allocation</h4>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={activeExperiment.variants.map((variant, index) => ({
                            name: variant.name,
                            value: variant.allocation,
                            fill: COLORS[index % COLORS.length]
                          }))}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="value"
                          label={({ name, value }) => `${name}: ${value}%`}
                        />
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Detailed Results */}
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistical Analysis</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {activeExperiment.variants.map((variant, index) => (
                    <div key={variant.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium text-gray-900">{variant.name}</h4>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          index === 0 ? 'bg-blue-100 text-blue-800' : 
                          variant.id.includes('winner') ? 'bg-green-100 text-green-800' : 
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {index === 0 ? 'Control' : variant.id.includes('winner') ? 'Winner' : 'Variant'}
                        </span>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Conversion Rate</span>
                          <span className="font-semibold">{calculateConversionRate(variant)}%</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Successful Interactions</span>
                          <span className="font-semibold">{variant.metrics.conversions}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Escalations</span>
                          <span className="font-semibold text-red-600">{variant.metrics.escalations}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Traffic Share</span>
                          <span className="font-semibold">{variant.allocation}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                
                {/* Recommendation */}
                {experimentResults && (
                  <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                    <div className="flex items-start">
                      <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 mr-3" />
                      <div>
                        <h4 className="font-medium text-green-900">Recommendation</h4>
                        <p className="text-sm text-green-800 mt-1">
                          {experimentResults.recommendation}
                        </p>
                        <div className="mt-2 text-xs text-green-700">
                          <p>• Confidence Interval: [{experimentResults.confidence_interval.join(', ')}]</p>
                          <p>• Sample Size: {experimentResults.sample_size.toLocaleString()} interactions</p>
                          <p>• Estimated Revenue Impact: ${experimentResults.revenue_impact.toLocaleString()}/month</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h3 className="text-xl font-bold mb-3">Continuous Optimization Benefits</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h4 className="font-semibold mb-2">🎯 Data-Driven Decisions</h4>
            <ul className="text-sm space-y-1">
              <li>• Statistically significant improvements</li>
              <li>• Reduced bias in optimization</li>
              <li>• Quantified performance gains</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">⚡ Rapid iteration</h4>
            <ul className="text-sm space-y-1">
              <li>• Quick experiment setup</li>
              <li>• Real-time result monitoring</li>
              <li>• Automatic traffic allocation</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2">📈 Measurable ROI</h4>
            <ul className="text-sm space-y-1">
              <li>• Clear revenue impact tracking</li>
              <li>• Performance benchmark comparison</li>
              <li>• Compound improvement effects</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ABTestingDashboard;