import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Clock, Users, Activity, Database, Brain, CheckCircle, 
  AlertTriangle, Zap, TrendingUp
} from 'lucide-react';
import axios from 'axios';

const RealPerformanceAnalytics = () => {
  const [systemMetrics, setSystemMetrics] = useState(null);
  const [agentMetrics, setAgentMetrics] = useState(null);
  const [aiPerformanceMetrics, setAiPerformanceMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [websocketStats, setWebsocketStats] = useState(null);

  useEffect(() => {
    fetchRealMetrics();
    const interval = setInterval(fetchRealMetrics, 10000); // Poll every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRealMetrics = async () => {
    try {
      setLoading(true);
      
      // Fetch actual system metrics
      const [agentsResponse, wsStatsResponse, aiMetricsResponse] = await Promise.all([
        axios.get('/api/agents/status').catch(() => ({ data: { success: false } })),
        axios.get('/api/ws/stats').catch(() => ({ data: { success: false } })),
        axios.get('/api/ai-performance-metrics').catch(() => ({ data: { success: false } }))
      ]);

      if (agentsResponse.data.success) {
        setAgentMetrics({
          totalAgents: agentsResponse.data.total_agents,
          cacheStats: agentsResponse.data.cache_stats,
          agentsByDomain: agentsResponse.data.agents_by_domain,
          databaseConnected: agentsResponse.data.database_connected,
          memoryCached: agentsResponse.data.memory_cached
        });
      }

      if (wsStatsResponse.data.success) {
        setWebsocketStats(wsStatsResponse.data.stats);
      }

      if (aiMetricsResponse.data.success) {
        setAiPerformanceMetrics(aiMetricsResponse.data.metrics);
      }

      // Try to fetch Galileo metrics if available
      try {
        const galileoResponse = await axios.get('/api/galileo-metrics');
        if (galileoResponse.data.success) {
          setSystemMetrics(galileoResponse.data);
        }
      } catch (galileoError) {
        // Galileo metrics not available, use basic system health
        setSystemMetrics({
          systemHealth: 'operational',
          services: {
            database: agentsResponse.data.success ? 'connected' : 'disconnected',
            websockets: wsStatsResponse.data.success ? 'active' : 'inactive',
            agents: agentMetrics?.totalAgents > 0 ? 'loaded' : 'not_loaded'
          }
        });
      }

      setError(null);
    } catch (err) {
      setError('Failed to fetch metrics: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const SystemHealthCard = ({ title, value, status, icon: Icon, description }) => (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <div className="flex items-center mt-2">
            <div className={`w-2 h-2 rounded-full mr-2 ${
              status === 'active' || status === 'connected' || status === 'operational' 
                ? 'bg-green-500' 
                : status === 'partial' || status === 'warning'
                ? 'bg-yellow-500'
                : 'bg-red-500'
            }`}></div>
            <p className="text-xs text-gray-500">{description}</p>
          </div>
        </div>
        <div className="p-3 rounded-full bg-gradient-to-r from-blue-500 to-blue-600">
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  const AgentDomainChart = () => {
    if (!agentMetrics?.agentsByDomain) return null;

    const data = Object.entries(agentMetrics.agentsByDomain).map(([domain, agents]) => ({
      domain: domain.charAt(0).toUpperCase() + domain.slice(1),
      count: agents.length,
      agents: agents.map(a => a.name).join(', ')
    }));

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold mb-4">Agent Distribution by Domain</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ domain, count }) => `${domain} (${count})`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value, name, props) => [value, `${props.payload.domain} Agents`]} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  if (loading && !agentMetrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
          <p className="text-red-800">{error}</p>
        </div>
        <button 
          onClick={fetchRealMetrics}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Performance Analytics</h1>
          <p className="text-gray-600 mt-2">Real-time system performance and agent utilization</p>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SystemHealthCard
          title="Active Agents"
          value={agentMetrics?.totalAgents || 0}
          status={agentMetrics?.totalAgents > 0 ? 'active' : 'inactive'}
          icon={Brain}
          description={agentMetrics?.databaseConnected ? 'Database connected' : 'Database disconnected'}
        />
        
        <SystemHealthCard
          title="Cache Performance"
          value={agentMetrics?.cacheStats?.cache_age_seconds ? 
            `${Math.floor(agentMetrics.cacheStats.cache_age_seconds)}s` : 'N/A'}
          status={agentMetrics?.memoryCached ? 'active' : 'inactive'}
          icon={Database}
          description="Agent data cached in memory"
        />

        <SystemHealthCard
          title="WebSocket Connections"
          value={websocketStats?.active_connections || 0}
          status={websocketStats?.active_connections > 0 ? 'active' : 'inactive'}
          icon={Activity}
          description="Real-time connections active"
        />

        <SystemHealthCard
          title="System Status"
          value={systemMetrics?.systemHealth || 'Unknown'}
          status={systemMetrics?.systemHealth || 'unknown'}
          icon={CheckCircle}
          description="Overall system health"
        />
      </div>

      {/* Agent Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AgentDomainChart />
        
        {/* Cache Statistics */}
        {agentMetrics?.cacheStats && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4">Cache Performance</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Agents Cached:</span>
                <span className="font-semibold">{agentMetrics.cacheStats.total_agents}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cache TTL:</span>
                <span className="font-semibold">{agentMetrics.cacheStats.cache_ttl}s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Last Refresh:</span>
                <span className="font-semibold">
                  {agentMetrics.cacheStats.last_refresh ? 
                    new Date(agentMetrics.cacheStats.last_refresh * 1000).toLocaleTimeString() : 
                    'Never'
                  }
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Agent Details by Domain */}
      {agentMetrics?.agentsByDomain && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold mb-4">Agents by Domain</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(agentMetrics.agentsByDomain).map(([domain, agents]) => (
              <div key={domain} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium capitalize text-gray-900">{domain}</h4>
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                    {agents.length} agent{agents.length !== 1 ? 's' : ''}
                  </span>
                </div>
                <div className="space-y-1">
                  {agents.map((agent, idx) => (
                    <div key={idx} className="text-sm text-gray-600">
                      • {agent.name}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI/ML Performance Metrics */}
      {aiPerformanceMetrics && (
        <>
          {/* Response Time Metrics */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-blue-600" />
              Response Time Analytics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {aiPerformanceMetrics.response_times.average.toFixed(2)}s
                </p>
                <p className="text-sm text-gray-600">Average Response Time</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {aiPerformanceMetrics.response_times.median.toFixed(2)}s
                </p>
                <p className="text-sm text-gray-600">Median (P50)</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-yellow-600">
                  {aiPerformanceMetrics.response_times.p95.toFixed(2)}s
                </p>
                <p className="text-sm text-gray-600">95th Percentile</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-red-600">
                  {aiPerformanceMetrics.response_times.p99.toFixed(2)}s
                </p>
                <p className="text-sm text-gray-600">99th Percentile</p>
              </div>
            </div>
          </div>

          {/* Success Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
                Success vs Failed Requests
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={[
                        { name: 'Successful', value: aiPerformanceMetrics.success_metrics.successful_requests, fill: '#10B981' },
                        { name: 'Failed', value: aiPerformanceMetrics.success_metrics.failed_requests, fill: '#EF4444' }
                      ]}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value, percent }) => `${name}: ${value} (${(percent || 0).toFixed(1)}%)`}
                    />
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 text-center">
                <p className="text-sm text-gray-600">
                  Success Rate: <span className="font-semibold text-green-600">
                    {aiPerformanceMetrics.success_metrics.success_rate.toFixed(1)}%
                  </span>
                </p>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-purple-600" />
                Agent Utilization & Capacity
              </h3>
              <div className="space-y-3">
                {Object.entries(aiPerformanceMetrics.agent_utilization || {}).slice(0, 5).map(([agentName, util]) => (
                  <div key={agentName} className="border-b border-gray-100 pb-2">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700">{agentName}</span>
                      <span className="text-sm text-gray-600">{util.utilization_percent.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{ width: `${Math.min(util.utilization_percent, 100)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {util.interactions_last_24h} interactions (24h)
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Topic Coverage & Model Performance */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Database className="w-5 h-5 mr-2 text-indigo-600" />
                Topic Coverage & Specialization
              </h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={Object.entries(aiPerformanceMetrics.topic_coverage || {}).map(([topic, data]) => ({
                    topic: topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                    interactions: data.interactions,
                    success_rate: data.success_rate
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="topic" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="interactions" fill="#6366F1" name="Interactions" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Brain className="w-5 h-5 mr-2 text-orange-600" />
                Model Performance Metrics
              </h3>
              <div className="space-y-4">
                {Object.entries(aiPerformanceMetrics.model_performance || {}).slice(0, 4).map(([agentName, perf]) => (
                  <div key={agentName} className="border rounded-lg p-3">
                    <h4 className="font-medium text-gray-900 mb-2">{agentName}</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex justify-between">
                        <span>Accuracy:</span>
                        <span className="font-semibold">{perf.accuracy.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Precision:</span>
                        <span className="font-semibold">{perf.precision.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Recall:</span>
                        <span className="font-semibold">{perf.recall.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>F1 Score:</span>
                        <span className="font-semibold text-orange-600">{perf.f1_score.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Cost Analysis */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
              Cost Analysis & ROI
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">
                  ${aiPerformanceMetrics.cost_analysis.total_cost.toFixed(2)}
                </p>
                <p className="text-sm text-gray-600">Total Operating Cost</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">
                  ${aiPerformanceMetrics.cost_analysis.average_cost_per_resolution.toFixed(2)}
                </p>
                <p className="text-sm text-gray-600">Average Cost per Resolution</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">
                  {aiPerformanceMetrics.success_metrics.total_requests}
                </p>
                <p className="text-sm text-gray-600">Total Interactions Processed</p>
              </div>
            </div>
            
            <div className="mt-6">
              <h4 className="font-medium text-gray-900 mb-3">Cost Breakdown by Agent</h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={aiPerformanceMetrics.cost_analysis.cost_breakdown || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="agent" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip formatter={(value) => [`$${value.toFixed(2)}`, 'Cost']} />
                    <Bar dataKey="total_cost" fill="#10B981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Performance Notes */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start">
          <Zap className="w-5 h-5 text-blue-600 mr-3 mt-0.5" />
          <div>
            <h3 className="text-blue-900 font-medium">Performance Insights</h3>
            <p className="text-blue-800 text-sm mt-1">
              This dashboard shows real-time system performance metrics. All data is pulled from actual 
              running services including database connectivity, agent availability, and WebSocket connections.
              {agentMetrics?.databaseConnected && " Database integration is active."}
              {websocketStats?.active_connections > 0 && " Real-time tracking is operational."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealPerformanceAnalytics;