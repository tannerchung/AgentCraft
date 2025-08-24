import React, { useState, useEffect } from 'react';
import { 
  Brain, Search, Target, TrendingUp, AlertCircle, 
  CheckCircle, ArrowRight, Zap, BarChart3 
} from 'lucide-react';

const QueryAnalyzer = ({ query, agents, onQueryChange }) => {
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    if (query && query.length > 3) {
      analyzeQuery(query);
    } else {
      setAnalysis(null);
    }
  }, [query, agents]);

  const analyzeQuery = async (inputQuery) => {
    setIsAnalyzing(true);
    
    // Simulate real-time analysis
    setTimeout(() => {
      const queryLower = inputQuery.toLowerCase();
      const agentScores = [];
      
      // Score each agent based on keyword matching and relevance
      agents.forEach(agent => {
        let score = 0;
        let matchedKeywords = [];
        
        // Keyword matching
        agent.configuration.keywords.forEach(keyword => {
          if (queryLower.includes(keyword.toLowerCase())) {
            score += 15;
            matchedKeywords.push(keyword);
          }
        });
        
        // Category relevance boost
        if (agent.category === 'Technical' && (queryLower.includes('api') || queryLower.includes('integration'))) {
          score += 10;
        }
        if (agent.category === 'Security' && (queryLower.includes('security') || queryLower.includes('vulnerability'))) {
          score += 10;
        }
        
        // Expertise matching
        agent.expertise.forEach(skill => {
          if (queryLower.includes(skill.toLowerCase().split(' ')[0])) {
            score += 8;
            if (!matchedKeywords.includes(skill)) {
              matchedKeywords.push(skill);
            }
          }
        });
        
        // Historical performance boost
        score += (agent.performance.successRate - 80) / 4;
        
        // Query complexity assessment
        const complexity = assessComplexity(inputQuery);
        if (complexity === 'high' && agent.configuration.confidenceThreshold > 0.7) {
          score += 5;
        }
        
        agentScores.push({
          agent,
          score: Math.max(0, Math.min(100, score)),
          matchedKeywords,
          confidence: Math.min(95, score + Math.random() * 10),
          wouldTrigger: score > (agent.configuration.confidenceThreshold * 100)
        });
      });
      
      // Sort by score descending
      agentScores.sort((a, b) => b.score - a.score);
      
      // Determine recommended agents (top scorers above threshold)
      const recommendedAgents = agentScores.filter(item => 
        item.wouldTrigger && item.score > 30
      ).slice(0, 3);
      
      const complexity = assessComplexity(inputQuery);
      const sentiment = assessSentiment(inputQuery);
      
      setAnalysis({
        query: inputQuery,
        complexity,
        sentiment,
        agentScores,
        recommendedAgents,
        topAgent: agentScores[0] || null,
        requiresEscalation: complexity === 'high' || sentiment < -0.5 || recommendedAgents.length > 2,
        processingTime: Math.random() * 200 + 50,
        keywords: extractKeywords(inputQuery)
      });
      
      setIsAnalyzing(false);
    }, 800);
  };

  const assessComplexity = (query) => {
    const wordCount = query.split(' ').length;
    const questionCount = (query.match(/\?/g) || []).length;
    const technicalTerms = ['api', 'webhook', 'ssl', 'database', 'authentication', 'integration'];
    const technicalCount = technicalTerms.filter(term => 
      query.toLowerCase().includes(term)
    ).length;
    
    const complexityScore = (wordCount / 10) + (questionCount * 2) + (technicalCount * 1.5);
    
    if (complexityScore > 8) return 'high';
    if (complexityScore > 4) return 'medium';
    return 'low';
  };

  const assessSentiment = (query) => {
    const positiveWords = ['good', 'great', 'excellent', 'perfect', 'working', 'successful'];
    const negativeWords = ['broken', 'failing', 'error', 'problem', 'issue', 'wrong', 'bad'];
    
    const positive = positiveWords.filter(word => query.toLowerCase().includes(word)).length;
    const negative = negativeWords.filter(word => query.toLowerCase().includes(word)).length;
    
    return positive - negative;
  };

  const extractKeywords = (query) => {
    const stopWords = ['the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'are', 'how', 'what', 'when', 'where', 'why'];
    return query.toLowerCase()
      .split(/\W+/)
      .filter(word => word.length > 2 && !stopWords.includes(word))
      .slice(0, 8);
  };

  const getComplexityColor = (complexity) => {
    switch (complexity) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment > 0) return 'text-green-600 bg-green-100';
    if (sentiment < 0) return 'text-red-600 bg-red-100';
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center mb-4">
        <Brain className="w-6 h-6 text-purple-600 mr-2" />
        <h3 className="text-lg font-semibold text-gray-900">Real-Time Query Analysis</h3>
      </div>

      {/* Query Input */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Type a query to see real-time agent analysis..."
            className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-lg"
          />
        </div>
      </div>

      {isAnalyzing && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-2 text-blue-600">
            <Brain className="w-5 h-5 animate-pulse" />
            <span>Analyzing query...</span>
          </div>
        </div>
      )}

      {analysis && !isAnalyzing && (
        <div className="space-y-6">
          {/* Query Metrics */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getComplexityColor(analysis.complexity)}`}>
                {analysis.complexity.charAt(0).toUpperCase() + analysis.complexity.slice(1)}
              </div>
              <div className="text-xs text-gray-600 mt-1">Complexity</div>
            </div>
            
            <div className="text-center">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(analysis.sentiment)}`}>
                {analysis.sentiment > 0 ? 'Positive' : analysis.sentiment < 0 ? 'Negative' : 'Neutral'}
              </div>
              <div className="text-xs text-gray-600 mt-1">Sentiment</div>
            </div>
            
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">
                {analysis.recommendedAgents.length}
              </div>
              <div className="text-xs text-gray-600">Matching Agents</div>
            </div>
            
            <div className="text-center">
              <div className={`text-lg font-bold ${analysis.requiresEscalation ? 'text-orange-600' : 'text-green-600'}`}>
                {analysis.requiresEscalation ? 'Yes' : 'No'}
              </div>
              <div className="text-xs text-gray-600">HITL Escalation</div>
            </div>
          </div>

          {/* Top Recommended Agent */}
          {analysis.topAgent && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-blue-900">Top Recommended Agent</h4>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-blue-700">
                    {analysis.topAgent.confidence.toFixed(1)}% confidence
                  </span>
                  <div className={`w-2 h-2 rounded-full ${analysis.topAgent.wouldTrigger ? 'bg-green-400' : 'bg-red-400'}`}></div>
                </div>
              </div>
              
              <div className="flex items-center">
                <span className="text-3xl mr-3">{analysis.topAgent.agent.avatar}</span>
                <div className="flex-1">
                  <h5 className="font-medium text-gray-900">{analysis.topAgent.agent.name}</h5>
                  <p className="text-sm text-gray-600">{analysis.topAgent.agent.description}</p>
                  <div className="flex items-center mt-2 space-x-4">
                    <span className="text-xs text-blue-700">
                      Score: {analysis.topAgent.score.toFixed(1)}/100
                    </span>
                    <span className="text-xs text-blue-700">
                      Keywords: {analysis.topAgent.matchedKeywords.slice(0,3).join(', ')}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Agent Scoring Breakdown */}
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Agent Scoring Breakdown</h4>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {analysis.agentScores.slice(0, 6).map((item, index) => (
                <div key={item.agent.id} className={`p-3 rounded-lg border ${
                  item.wouldTrigger ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className="text-sm mr-2">#{index + 1}</span>
                      <span className="text-lg mr-2">{item.agent.avatar}</span>
                      <div>
                        <h6 className="font-medium text-sm text-gray-900">{item.agent.name}</h6>
                        <div className="text-xs text-gray-600">
                          {item.matchedKeywords.length > 0 ? (
                            <span>Matched: {item.matchedKeywords.slice(0,2).join(', ')}</span>
                          ) : (
                            <span>No keyword matches</span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className={`text-sm font-semibold ${
                        item.score > 50 ? 'text-green-600' : item.score > 25 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {item.score.toFixed(1)}
                      </div>
                      <div className="text-xs text-gray-500">
                        {item.wouldTrigger ? 'Would trigger' : 'Below threshold'}
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full ${
                          item.score > 50 ? 'bg-green-500' : item.score > 25 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(100, item.score)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Processing Stats */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">Processing Statistics</h4>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-600">Processing Time:</span>
                <span className="font-semibold ml-2">{analysis.processingTime.toFixed(0)}ms</span>
              </div>
              <div>
                <span className="text-gray-600">Keywords Extracted:</span>
                <span className="font-semibold ml-2">{analysis.keywords.length}</span>
              </div>
              <div>
                <span className="text-gray-600">Agents Evaluated:</span>
                <span className="font-semibold ml-2">{analysis.agentScores.length}</span>
              </div>
            </div>
            
            <div className="mt-3">
              <span className="text-gray-600 text-sm">Extracted Keywords:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {analysis.keywords.map((keyword, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryAnalyzer;