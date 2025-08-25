import React, { useState } from 'react';
import RealPerformanceAnalytics from './components/RealPerformanceAnalytics';
import ABTestingDashboard from './components/ABTestingDashboard';
import AgentChat from './components/AgentChat';
import MultiAgentDemo from './components/MultiAgentDemo';
import AgentConfiguration from './components/AgentConfiguration';
import KnowledgeBaseManager from './components/KnowledgeBaseManager';
import { Activity, MessageSquare, Users, BarChart3, Zap, Settings, Database } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('performance');

  const tabs = [
    { id: 'performance', name: 'Performance Analytics', icon: BarChart3 },
    { id: 'multi-agent', name: 'Multi-Agent Demo', icon: Users },
    { id: 'knowledge', name: 'Knowledge Base', icon: Database },
    { id: 'config', name: 'Agent Configuration', icon: Settings },
    { id: 'chat', name: 'Agent Chat', icon: MessageSquare },
    { id: 'ab-testing', name: 'A/B Testing', icon: Zap },
  ];

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'performance':
        return <RealPerformanceAnalytics />;
      case 'multi-agent':
        return <MultiAgentDemo />;
      case 'knowledge':
        return <KnowledgeBaseManager />;
      case 'config':
        return <AgentConfiguration />;
      case 'chat':
        return <AgentChat />;
      case 'ab-testing':
        return <ABTestingDashboard />;
      default:
        return <RealPerformanceAnalytics />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="gradient-bg text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-3xl font-bold">🛠️ AgentCraft</h1>
              </div>
              <div className="ml-4">
                <p className="text-lg font-medium">Specialized AI Agent Architecture</p>
                <p className="text-sm opacity-90">Demonstrating domain expertise advantages</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium">Live Demo</p>
                <p className="text-xs opacity-75">Salesforce Architecture Review</p>
              </div>
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-salesforce-blue text-salesforce-blue'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderActiveComponent()}
      </main>
    </div>
  );
}

export default App;