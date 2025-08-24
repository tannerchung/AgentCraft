import React, { useState, useEffect } from 'react';
import { Send, Bot, User, Zap, Clock, CheckCircle } from 'lucide-react';
import axios from 'axios';

const AgentDemo = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('');
  const [demoScenarios, setDemoScenarios] = useState({});
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    // Load demo scenarios and metrics on component mount
    loadDemoScenarios();
    loadMetrics();
  }, []);

  const loadDemoScenarios = async () => {
    try {
      const response = await axios.get('/api/demo-scenarios');
      setDemoScenarios(response.data.technical_scenarios);
    } catch (error) {
      console.error('Failed to load demo scenarios:', error);
    }
  };

  const loadMetrics = async () => {
    try {
      const response = await axios.get('/api/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  };

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const startTime = Date.now();
      
      const response = await axios.post('/api/chat', {
        agent_type: 'technical_support',
        message: message,
        context: { demo_mode: true }
      });

      const responseTime = Date.now() - startTime;

      // Extract the response content properly
      let responseContent;
      if (response.data.response && typeof response.data.response === 'object') {
        if (response.data.response.content) {
          // Handle the new structured response format
          responseContent = response.data.response.content;
          
          // If content contains AI analysis with JSON, format it properly
          if (responseContent.includes('**AI Technical Analysis:**')) {
            try {
              const jsonStart = responseContent.indexOf('{');
              const jsonEnd = responseContent.lastIndexOf('}') + 1;
              if (jsonStart !== -1 && jsonEnd > jsonStart) {
                const jsonStr = responseContent.substring(jsonStart, jsonEnd);
                const parsed = JSON.parse(jsonStr);
                
                // Create a structured response for better display
                responseContent = {
                  issue_analysis: {
                    diagnosis: parsed.diagnosis,
                    root_cause: parsed.root_cause,
                    solution: parsed.solution,
                    fix_code: parsed.working_code,
                    implementation_steps: parsed.implementation_steps,
                    testing_approach: parsed.testing_approach,
                    prevention: parsed.prevention,
                    implementation_time: parsed.estimated_fix_time
                  }
                };
              }
            } catch (parseError) {
              console.warn('Failed to parse AI response JSON:', parseError);
              // Keep the original content if parsing fails
            }
          }
        } else {
          responseContent = response.data.response;
        }
      } else {
        responseContent = response.data.response;
      }

      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: responseContent,
        agentInfo: response.data.agent_info,
        competitiveAdvantage: response.data.competitive_advantage,
        responseTime: responseTime,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);

      // Simulate AgentForce comparison
      setTimeout(() => {
        const agentForceMessage = {
          id: Date.now() + 2,
          type: 'agentforce_simulation',
          content: "I understand you're experiencing technical difficulties. Please check our API documentation or contact our technical support team for assistance with your webhook integration.",
          responseTime: 8000,
          timestamp: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, agentForceMessage]);
      }, 1000);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error. In a production system, this would trigger automatic failover.',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const selectScenario = (scenarioKey) => {
    const scenario = demoScenarios[scenarioKey];
    setInputMessage(scenario);
    setSelectedScenario(scenarioKey);
  };

  const clearChat = () => {
    setMessages([]);
    setSelectedScenario('');
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎯 AgentCraft Technical Demo
        </h1>
        <p className="text-gray-600">
          Specialized webhook expertise vs generic topic handling
        </p>
      </div>

      {/* Metrics Dashboard */}
      {metrics && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Clock className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <p className="text-sm text-blue-600 font-medium">Response Time</p>
                <p className="text-2xl font-bold text-blue-900">
                  {metrics.agent_performance.response_time}
                </p>
                <p className="text-xs text-blue-500">
                  vs {metrics.agentforce_comparison.response_time}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
              <div>
                <p className="text-sm text-green-600 font-medium">Accuracy Rate</p>
                <p className="text-2xl font-bold text-green-900">
                  {metrics.agent_performance.accuracy_rate}
                </p>
                <p className="text-xs text-green-500">
                  vs {metrics.agentforce_comparison.accuracy_rate}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Zap className="h-5 w-5 text-purple-600 mr-2" />
              <div>
                <p className="text-sm text-purple-600 font-medium">Cost Savings</p>
                <p className="text-2xl font-bold text-purple-900">
                  {metrics.cost_analysis.roi_percentage}
                </p>
                <p className="text-xs text-purple-500">
                  {metrics.cost_analysis.annual_savings} annually
                </p>
              </div>
            </div>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center">
              <Bot className="h-5 w-5 text-orange-600 mr-2" />
              <div>
                <p className="text-sm text-orange-600 font-medium">Specialization</p>
                <p className="text-2xl font-bold text-orange-900">
                  20+ Agents
                </p>
                <p className="text-xs text-orange-500">
                  vs 7 generic topics
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Demo Scenarios */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3">Quick Demo Scenarios:</h3>
        <div className="flex flex-wrap gap-2">
          {Object.entries(demoScenarios).map(([key, scenario]) => (
            <button
              key={key}
              onClick={() => selectScenario(key)}
              className={`px-3 py-1 rounded-full text-sm transition-colors ${
                selectedScenario === key
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </button>
          ))}
          <button
            onClick={clearChat}
            className="px-3 py-1 rounded-full text-sm bg-red-200 text-red-700 hover:bg-red-300"
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="border rounded-lg bg-gray-50">
        {/* Messages */}
        <div className="h-96 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <Bot className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Ask me about webhook integrations, API issues, or competitive comparisons!</p>
              <p className="text-sm mt-2">Try the demo scenarios above or type your own technical question.</p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg p-4 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white ml-12'
                    : message.type === 'agentforce_simulation'
                    ? 'bg-red-100 text-red-800 mr-12 border border-red-200'
                    : message.type === 'error'
                    ? 'bg-yellow-100 text-yellow-800 mr-12 border border-yellow-200'
                    : 'bg-white text-gray-800 mr-12 border border-gray-200 shadow-sm'
                }`}
              >
                <div className="flex items-start">
                  {message.type === 'user' ? (
                    <User className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
                  ) : message.type === 'agentforce_simulation' ? (
                    <div className="mr-2 mt-0.5">
                      <div className="h-5 w-5 bg-red-500 rounded text-white text-xs flex items-center justify-center">AF</div>
                    </div>
                  ) : (
                    <Bot className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0 text-blue-600" />
                  )}
                  
                  <div className="flex-1">
                    {message.type === 'agentforce_simulation' && (
                      <div className="text-xs font-semibold mb-1 text-red-600">
                        AgentForce Simulation (Generic Response):
                      </div>
                    )}
                    
                    {message.type === 'agent' && message.agentInfo && (
                      <div className="text-xs text-gray-500 mb-2">
                        <strong>{message.agentInfo.role}</strong> • 
                        Response time: {message.responseTime}ms
                      </div>
                    )}

                    <div className="whitespace-pre-wrap">
                      {typeof message.content === 'object' ? (
                        <div>
                          {message.content.issue_analysis && (
                            <div className="mb-3">
                              <h4 className="font-semibold text-green-800">Technical Analysis:</h4>
                              <p className="mt-1">{message.content.issue_analysis.diagnosis}</p>
                              <p className="mt-1"><strong>Solution:</strong> {message.content.issue_analysis.solution}</p>
                              
                              {message.content.issue_analysis.fix_code && (
                                <div className="mt-2">
                                  <h5 className="font-medium">Working Code Solution:</h5>
                                  <pre className="bg-gray-800 text-green-400 p-3 rounded mt-1 text-sm overflow-x-auto">
                                    {message.content.issue_analysis.fix_code}
                                  </pre>
                                </div>
                              )}

                              {message.content.issue_analysis.implementation_time && (
                                <p className="mt-2 text-sm text-gray-600">
                                  <strong>Implementation time:</strong> {message.content.issue_analysis.implementation_time}
                                </p>
                              )}
                            </div>
                          )}

                          {message.content.cost_comparison && (
                            <div className="mt-3 p-3 bg-blue-50 rounded">
                              <h4 className="font-semibold text-blue-800">Cost Analysis:</h4>
                              <div className="mt-1 text-sm">
                                <p>Our solution: {message.content.cost_comparison.our_solution_cost}</p>
                                <p>AgentForce: {message.content.cost_comparison.competitor_true_cost}</p>
                                <p className="font-semibold text-green-700">
                                  Savings: {message.content.cost_comparison.savings}
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                      ) : (
                        message.content
                      )}
                    </div>

                    {message.competitiveAdvantage && (
                      <div className="mt-3 text-xs bg-blue-100 text-blue-800 p-2 rounded">
                        <strong>Competitive Advantage:</strong> {message.competitiveAdvantage.vs_agentforce}
                      </div>
                    )}

                    <div className="text-xs text-gray-400 mt-2">
                      {message.timestamp}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 rounded-lg p-4 mr-12 border border-gray-200">
                <div className="flex items-center">
                  <Bot className="h-5 w-5 mr-2 text-blue-600" />
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask about webhook issues, API problems, or competitive comparisons..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            This demo shows specialized technical expertise vs generic topic handling
          </p>
        </div>
      </div>
    </div>
  );
};

export default AgentDemo;