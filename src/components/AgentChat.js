
import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { useAgentChat } from '../hooks/useAgentChat';

const AgentChat = () => {
  const [selectedAgent, setSelectedAgent] = useState('technical');
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef(null);
  
  const { messages, sendMessage, isLoading, agentStatus } = useAgentChat(selectedAgent);

  const agents = [
    {
      id: 'technical',
      name: 'Technical Support',
      description: 'Webhook troubleshooting, API integration, SSL issues',
      avatar: '🔧',
      expertise: ['Webhooks', 'APIs', 'SSL', 'Authentication']
    },
    {
      id: 'billing',
      name: 'Billing Specialist',
      description: 'Payment processing, subscription management, invoicing',
      avatar: '💳',
      expertise: ['Payments', 'Subscriptions', 'Invoicing', 'Refunds']
    },
    {
      id: 'competitive',
      name: 'Competitive Analysis',
      description: 'Market intelligence, competitor analysis, positioning',
      avatar: '📊',
      expertise: ['Market Research', 'Competitive Intel', 'Positioning']
    }
  ];

  const demoQueries = {
    technical: [
      "My webhook is failing with SSL certificate verification errors",
      "I'm getting 401 errors when sending webhooks with HMAC signatures",
      "How do I implement webhook retry logic with exponential backoff?",
      "My API integration is timing out. How should I configure this?"
    ],
    billing: [
      "How do I handle failed payment webhooks?",
      "Customer wants to upgrade their subscription mid-cycle",
      "How do I process a partial refund for an annual subscription?",
      "What's the best way to handle dunning management?"
    ],
    competitive: [
      "How does our pricing compare to Salesforce Service Cloud?",
      "What are the key differentiators against Zendesk?",
      "Show me competitive intelligence on Microsoft Dynamics",
      "What's our positioning against custom-built solutions?"
    ]
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    await sendMessage(message);
    setMessage('');
  };

  const handleDemoQuery = (query) => {
    setMessage(query);
  };

  const currentAgent = agents.find(agent => agent.id === selectedAgent);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 h-[calc(100vh-200px)]">
      {/* Agent Selection Sidebar */}
      <div className="lg:col-span-1 space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Agent</h3>
          <div className="space-y-3">
            {agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent.id)}
                className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                  selectedAgent === agent.id
                    ? 'border-salesforce-blue bg-salesforce-lightblue'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-center mb-2">
                  <span className="text-2xl mr-3">{agent.avatar}</span>
                  <div>
                    <h4 className="font-medium text-gray-900">{agent.name}</h4>
                    <div className="flex items-center mt-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      <span className="text-xs text-gray-500">Online</span>
                    </div>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-2">{agent.description}</p>
                <div className="flex flex-wrap gap-1">
                  {agent.expertise.map((skill) => (
                    <span
                      key={skill}
                      className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Demo Queries */}
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-3">Try These Queries</h4>
          <div className="space-y-2">
            {demoQueries[selectedAgent]?.map((query, index) => (
              <button
                key={index}
                onClick={() => handleDemoQuery(query)}
                className="w-full p-3 text-left text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="lg:col-span-3 bg-white rounded-lg shadow-sm border flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-salesforce-blue to-salesforce-darkblue text-white rounded-t-lg">
          <div className="flex items-center">
            <span className="text-2xl mr-3">{currentAgent?.avatar}</span>
            <div>
              <h3 className="font-semibold">{currentAgent?.name}</h3>
              <p className="text-sm opacity-90">{currentAgent?.description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <CheckCircle className="w-4 h-4 mr-1" />
              <span className="text-sm">Ready</span>
            </div>
            <div className="text-right">
              <p className="text-sm">Confidence: {agentStatus.confidence}%</p>
              <p className="text-xs opacity-75">Avg Response: {agentStatus.avgResponseTime}s</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-8">
              <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ready to help with {currentAgent?.name.toLowerCase()}
              </h3>
              <p className="text-gray-600">
                Ask me anything about {currentAgent?.expertise.join(', ').toLowerCase()}
              </p>
            </div>
          )}
          
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`${msg.sender === 'agent' && msg.content.includes('**') ? 'max-w-4xl' : 'max-w-xs lg:max-w-md'} px-4 py-3 rounded-lg ${
                  msg.sender === 'user'
                    ? 'bg-salesforce-blue text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="flex items-start space-x-2">
                  {msg.sender === 'agent' && (
                    <span className="text-lg">{currentAgent?.avatar}</span>
                  )}
                  {msg.sender === 'user' && (
                    <User className="w-5 h-5 mt-1" />
                  )}
                  <div className="flex-1">
                    {msg.sender === 'agent' && msg.content.includes('**') ? (
                      <div className="text-sm prose prose-sm max-w-none">
                        <ReactMarkdown
                          components={{
                            h1: ({children}) => <h1 className="text-lg font-bold text-gray-900 mb-2">{children}</h1>,
                            h2: ({children}) => <h2 className="text-base font-semibold text-gray-800 mb-2">{children}</h2>,
                            h3: ({children}) => <h3 className="text-sm font-semibold text-gray-800 mb-1">{children}</h3>,
                            strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                            p: ({children}) => <p className="mb-2 text-gray-700 leading-relaxed">{children}</p>,
                            ul: ({children}) => <ul className="list-disc pl-4 mb-2 text-gray-700">{children}</ul>,
                            ol: ({children}) => <ol className="list-decimal pl-4 mb-2 text-gray-700">{children}</ol>,
                            li: ({children}) => <li className="mb-1">{children}</li>,
                            code: ({inline, children}) => inline 
                              ? <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono text-gray-800">{children}</code>
                              : <code className="block bg-gray-100 p-3 rounded text-xs font-mono text-gray-800 whitespace-pre-wrap overflow-x-auto">{children}</code>,
                            pre: ({children}) => <div className="bg-gray-100 p-3 rounded mb-2 overflow-x-auto">{children}</div>
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="text-sm">{msg.content}</p>
                    )}
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs opacity-75">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                      {msg.confidence && (
                        <span className="text-xs opacity-75">
                          {Math.round(msg.confidence * 100)}% confident
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-3">
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{currentAgent?.avatar}</span>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t">
          <div className="flex space-x-4">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={`Ask ${currentAgent?.name} anything...`}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-salesforce-blue focus:border-transparent"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className="px-6 py-2 bg-salesforce-blue text-white rounded-lg hover:bg-salesforce-darkblue disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AgentChat;
