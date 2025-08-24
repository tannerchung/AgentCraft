
import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Clock, DollarSign, Users, CheckCircle, AlertTriangle } from 'lucide-react';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalQueries: 1247,
    avgResponseTime: 1.2,
    costSavings: 45000,
    agentEfficiency: 94,
    customerSatisfaction: 4.8
  });

  const [realTimeData, setRealTimeData] = useState([]);

  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalQueries: prev.totalQueries + Math.floor(Math.random() * 3),
        avgResponseTime: Math.max(0.8, prev.avgResponseTime + (Math.random() - 0.5) * 0.1),
        costSavings: prev.costSavings + Math.floor(Math.random() * 100)
      }));

      setRealTimeData(prev => {
        const newData = [...prev.slice(-9), {
          time: new Date().toLocaleTimeString(),
          agentcraft: Math.floor(Math.random() * 20) + 80,
          agentforce: Math.floor(Math.random() * 15) + 45
        }];
        return newData;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const comparisonData = [
    { name: 'Response Speed', agentcraft: 95, agentforce: 65 },
    { name: 'Technical Depth', agentcraft: 92, agentforce: 58 },
    { name: 'Customization', agentcraft: 98, agentforce: 45 },
    { name: 'Cost Efficiency', agentcraft: 89, agentforce: 72 },
    { name: 'Domain Expertise', agentcraft: 96, agentforce: 52 }
  ];

  const agentPerformance = [
    { name: 'Technical Support', value: 35, color: '#0176d3' },
    { name: 'Competitive Analysis', value: 25, color: '#005fb2' },
    { name: 'Billing Support', value: 20, color: '#54a3ff' },
    { name: 'General Inquiry', value: 20, color: '#91c3ff' }
  ];

  const StatCard = ({ title, value, icon: Icon, trend, color = 'text-green-600' }) => (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {trend && (
            <p className={`text-sm ${color} flex items-center mt-1`}>
              <TrendingUp className="w-4 h-4 mr-1" />
              {trend}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-full bg-gradient-to-r from-salesforce-blue to-salesforce-darkblue`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          <StatCard
            title="Total Queries"
            value={metrics.totalQueries.toLocaleString()}
            icon={Users}
            trend="+12% this week"
          />
          <StatCard
            title="Avg Response Time"
            value={`${metrics.avgResponseTime.toFixed(1)}s`}
            icon={Clock}
            trend="-15% improved"
          />
          <StatCard
            title="Cost Savings"
            value={`$${(metrics.costSavings / 1000).toFixed(0)}K`}
            icon={DollarSign}
            trend="+$2.3K this month"
          />
          <StatCard
            title="Agent Efficiency"
            value={`${metrics.agentEfficiency}%`}
            icon={CheckCircle}
            trend="+3% this week"
          />
          <StatCard
            title="Satisfaction"
            value={`${metrics.customerSatisfaction}/5.0`}
            icon={TrendingUp}
            trend="+0.2 this month"
          />
        </div>
      </div>

      {/* Competitive Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-900">AgentCraft vs AgentForce</h3>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-salesforce-blue rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">AgentCraft</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-gray-400 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">AgentForce</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={comparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="agentcraft" fill="#0176d3" name="AgentCraft" />
              <Bar dataKey="agentforce" fill="#9ca3af" name="AgentForce" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Agent Performance Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={agentPerformance}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {agentPerformance.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Real-time Performance */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-gray-900">Real-time Performance Comparison</h3>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Live Data</span>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={realTimeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="agentcraft" stroke="#0176d3" strokeWidth={3} name="AgentCraft" />
            <Line type="monotone" dataKey="agentforce" stroke="#9ca3af" strokeWidth={3} name="AgentForce" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Cost Calculator */}
      <div className="bg-gradient-to-r from-salesforce-blue to-salesforce-darkblue rounded-lg shadow-lg p-8 text-white">
        <h3 className="text-2xl font-bold mb-6">Cost Savings Calculator</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-4xl font-bold">${(metrics.costSavings / 1000).toFixed(0)}K</p>
            <p className="text-lg opacity-90">Monthly Savings</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold">{((metrics.costSavings * 12) / 1000).toFixed(0)}K</p>
            <p className="text-lg opacity-90">Annual Projection</p>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold">67%</p>
            <p className="text-lg opacity-90">Cost Reduction</p>
          </div>
        </div>
        <div className="mt-6 flex items-center justify-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          <p className="text-sm opacity-90">
            Based on reduced training time, faster resolution, and specialized expertise
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
