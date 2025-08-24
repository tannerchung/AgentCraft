
import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, CheckCircle, Clock, Users, ArrowRight, Brain } from 'lucide-react';

const MultiAgentDemo = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [agentProgress, setAgentProgress] = useState({
    technical: 0,
    billing: 0,
    competitive: 0,
    coordinator: 0
  });

  const scenario = {
    title: "Complex Customer Issue: Enterprise Integration",
    description: "Customer has webhook failures, billing discrepancies, and needs competitive positioning for internal presentation",
    steps: [
      {
        id: 1,
        title: "Issue Analysis",
        description: "Coordinator analyzes the multi-faceted customer issue",
        agent: "coordinator",
        duration: 2000,
        output: "Identified 3 distinct issues requiring specialized expertise"
      },
      {
        id: 2,
        title: "Technical Diagnosis",
        description: "Technical agent investigates webhook failures",
        agent: "technical",
        duration: 3000,
        output: "SSL certificate chain incomplete, HMAC signature mismatch detected"
      },
      {
        id: 3,
        title: "Billing Investigation",
        description: "Billing agent reviews payment discrepancies",
        agent: "billing",
        duration: 2500,
        output: "Prorated charges calculation error, refund processing initiated"
      },
      {
        id: 4,
        title: "Competitive Research",
        description: "Competitive agent prepares positioning materials",
        agent: "competitive",
        duration: 3500,
        output: "ROI analysis complete, competitive advantage document generated"
      },
      {
        id: 5,
        title: "Solution Synthesis",
        description: "Coordinator compiles comprehensive response",
        agent: "coordinator",
        duration: 2000,
        output: "Integrated solution plan with technical fixes, billing resolution, and strategic positioning"
      }
    ]
  };

  const agents = {
    coordinator: {
      name: "Orchestration Agent",
      avatar: "🧠",
      color: "purple",
      description: "Coordinates multi-agent workflows and synthesizes responses"
    },
    technical: {
      name: "Technical Specialist",
      avatar: "🔧",
      color: "blue",
      description: "Deep technical expertise in APIs, webhooks, and integrations"
    },
    billing: {
      name: "Billing Expert",
      avatar: "💳",
      color: "green",
      description: "Payment processing, subscription management, and billing workflows"
    },
    competitive: {
      name: "Competitive Analyst",
      avatar: "📊",
      color: "orange",
      description: "Market intelligence, competitive positioning, and strategic analysis"
    }
  };

  useEffect(() => {
    let interval;
    
    if (isRunning && currentStep < scenario.steps.length) {
      const currentStepData = scenario.steps[currentStep];
      const stepDuration = currentStepData.duration;
      const agentType = currentStepData.agent;
      
      interval = setInterval(() => {
        setAgentProgress(prev => {
          const newProgress = Math.min(prev[agentType] + (100 / (stepDuration / 100)), 100);
          
          if (newProgress >= 100) {
            setTimeout(() => {
              setCurrentStep(step => step + 1);
              setAgentProgress(prev => ({ ...prev, [agentType]: 0 }));
            }, 500);
          }
          
          return { ...prev, [agentType]: newProgress };
        });
      }, 100);
    }
    
    if (currentStep >= scenario.steps.length) {
      setIsRunning(false);
    }
    
    return () => clearInterval(interval);
  }, [isRunning, currentStep]);

  const startDemo = () => {
    setIsRunning(true);
    setCurrentStep(0);
    setAgentProgress({ technical: 0, billing: 0, competitive: 0, coordinator: 0 });
  };

  const pauseDemo = () => {
    setIsRunning(false);
  };

  const resetDemo = () => {
    setIsRunning(false);
    setCurrentStep(0);
    setAgentProgress({ technical: 0, billing: 0, competitive: 0, coordinator: 0 });
  };

  const getColorClasses = (color) => {
    const colors = {
      purple: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200' },
      blue: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200' },
      green: { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' },
      orange: { bg: 'bg-orange-100', text: 'text-orange-700', border: 'border-orange-200' }
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Multi-Agent Orchestration Demo</h2>
        <p className="text-gray-600 max-w-3xl mx-auto">
          Watch how specialized agents collaborate to solve complex, multi-faceted customer issues 
          that would typically require multiple support interactions.
        </p>
      </div>

      {/* Scenario Description */}
      <div className="bg-gradient-to-r from-salesforce-blue to-salesforce-darkblue rounded-lg shadow-lg p-8 text-white">
        <div className="flex items-center mb-4">
          <Users className="w-8 h-8 mr-3" />
          <h3 className="text-2xl font-bold">{scenario.title}</h3>
        </div>
        <p className="text-lg opacity-90 mb-6">{scenario.description}</p>
        
        {/* Control Buttons */}
        <div className="flex space-x-4">
          <button
            onClick={startDemo}
            disabled={isRunning}
            className="flex items-center px-6 py-3 bg-white text-salesforce-blue rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Play className="w-5 h-5 mr-2" />
            Start Demo
          </button>
          
          <button
            onClick={pauseDemo}
            disabled={!isRunning}
            className="flex items-center px-6 py-3 bg-white/20 text-white border border-white/30 rounded-lg hover:bg-white/30 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Pause className="w-5 h-5 mr-2" />
            Pause
          </button>
          
          <button
            onClick={resetDemo}
            className="flex items-center px-6 py-3 bg-white/20 text-white border border-white/30 rounded-lg hover:bg-white/30 transition-colors"
          >
            <RotateCcw className="w-5 h-5 mr-2" />
            Reset
          </button>
        </div>
      </div>

      {/* Agent Status Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(agents).map(([agentType, agent]) => {
          const colors = getColorClasses(agent.color);
          const progress = agentProgress[agentType];
          const isActive = scenario.steps[currentStep]?.agent === agentType && isRunning;
          
          return (
            <div
              key={agentType}
              className={`p-6 rounded-lg border-2 transition-all ${
                isActive ? `${colors.border} ${colors.bg}` : 'border-gray-200 bg-white'
              }`}
            >
              <div className="flex items-center mb-4">
                <span className="text-3xl mr-3">{agent.avatar}</span>
                <div>
                  <h3 className={`font-semibold ${isActive ? colors.text : 'text-gray-900'}`}>
                    {agent.name}
                  </h3>
                  <div className="flex items-center mt-1">
                    <div className={`w-2 h-2 rounded-full mr-2 ${
                      isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-300'
                    }`}></div>
                    <span className="text-xs text-gray-500">
                      {isActive ? 'Processing...' : 'Ready'}
                    </span>
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mb-4">{agent.description}</p>
              
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    isActive ? 'bg-salesforce-blue' : 'bg-gray-400'
                  }`}
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">{Math.round(progress)}% Complete</p>
            </div>
          );
        })}
      </div>

      {/* Process Flow */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Process Flow</h3>
        
        <div className="space-y-4">
          {scenario.steps.map((step, index) => {
            const isCompleted = index < currentStep;
            const isActive = index === currentStep;
            const agent = agents[step.agent];
            const colors = getColorClasses(agent.color);
            
            return (
              <div
                key={step.id}
                className={`flex items-center p-4 rounded-lg border-2 transition-all ${
                  isActive ? `${colors.border} ${colors.bg}` :
                  isCompleted ? 'border-green-200 bg-green-50' :
                  'border-gray-200 bg-gray-50'
                }`}
              >
                {/* Step Number */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold mr-4 ${
                  isCompleted ? 'bg-green-600 text-white' :
                  isActive ? `${colors.text} bg-white border-2 ${colors.border}` :
                  'bg-gray-300 text-gray-600'
                }`}>
                  {isCompleted ? <CheckCircle className="w-5 h-5" /> : step.id}
                </div>
                
                {/* Agent Avatar */}
                <div className="flex-shrink-0 mr-4">
                  <span className="text-2xl">{agent.avatar}</span>
                </div>
                
                {/* Step Content */}
                <div className="flex-1">
                  <div className="flex items-center mb-1">
                    <h4 className={`font-medium ${isActive ? colors.text : 'text-gray-900'}`}>
                      {step.title}
                    </h4>
                    {isActive && (
                      <Clock className={`w-4 h-4 ml-2 animate-pulse ${colors.text}`} />
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                  
                  {/* Output */}
                  {(isCompleted || (isActive && agentProgress[step.agent] > 50)) && (
                    <div className="mt-2 p-2 bg-white/80 rounded border">
                      <p className="text-sm font-medium text-gray-700">Output:</p>
                      <p className="text-sm text-gray-600">{step.output}</p>
                    </div>
                  )}
                </div>
                
                {/* Arrow */}
                {index < scenario.steps.length - 1 && (
                  <ArrowRight className="w-5 h-5 text-gray-400 ml-4" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Results Summary */}
      {currentStep >= scenario.steps.length && (
        <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-lg p-8 text-white">
          <div className="flex items-center mb-4">
            <CheckCircle className="w-8 h-8 mr-3" />
            <h3 className="text-2xl font-bold">Multi-Agent Resolution Complete!</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div className="text-center">
              <p className="text-3xl font-bold">47s</p>
              <p className="text-sm opacity-90">Total Resolution Time</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold">4</p>
              <p className="text-sm opacity-90">Agents Coordinated</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold">100%</p>
              <p className="text-sm opacity-90">Issue Resolution</p>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-white/20 rounded-lg">
            <h4 className="font-semibold mb-2">Key Advantages Demonstrated:</h4>
            <ul className="space-y-1 text-sm">
              <li>• Single interaction resolves multi-faceted issues</li>
              <li>• Specialized expertise applied to each domain</li>
              <li>• Coordinated response prevents information silos</li>
              <li>• Dramatic reduction in customer effort and time</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiAgentDemo;
