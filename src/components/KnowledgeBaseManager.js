
import React, { useState, useEffect } from 'react';
import { Database, Search, Globe, FileText, RefreshCw, Settings } from 'lucide-react';

const KnowledgeBaseManager = () => {
  const [knowledgeStatus, setKnowledgeStatus] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [targetCompany, setTargetCompany] = useState('zapier');
  const [availableCompanies, setAvailableCompanies] = useState({});
  const [crawlUrls, setCrawlUrls] = useState([]);
  const [trainingData, setTrainingData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadKnowledgeStatus();
    loadCompanies();
  }, []);

  useEffect(() => {
    if (targetCompany) {
      loadCompanyCrawlUrls();
    }
  }, [targetCompany]);

  const loadKnowledgeStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/knowledge-base/status');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setKnowledgeStatus(data);
    } catch (error) {
      console.error('Error loading knowledge status:', error);
      // Set to null to indicate error state
      setKnowledgeStatus(null);
    }
  };

  const loadCompanies = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/companies');
      const data = await response.json();
      if (data.success) {
        setAvailableCompanies(data.companies);
        setTargetCompany(data.current_company);
      }
    } catch (error) {
      console.error('Error loading companies:', error);
    }
  };

  const loadCompanyCrawlUrls = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/crawl/company-urls');
      const data = await response.json();
      if (data.success) {
        setCrawlUrls(data.urls);
      }
    } catch (error) {
      console.error('Error loading crawl URLs:', error);
    }
  };

  const switchCompany = async (companyId) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/switch-company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_id: companyId })
      });
      
      const data = await response.json();
      if (data.success) {
        setTargetCompany(companyId);
        await loadKnowledgeStatus();
      }
    } catch (error) {
      console.error('Error switching company:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchKnowledgeBase = async () => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/knowledge-base/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          limit: 5,
          company_context: targetCompany
        })
      });
      
      const data = await response.json();
      if (data.success) {
        setSearchResults(data.results);
      }
    } catch (error) {
      console.error('Error searching knowledge base:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateTrainingData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/training-data/generate?count=50', {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.success) {
        setTrainingData(data);
      }
    } catch (error) {
      console.error('Error generating training data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const startCrawling = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/crawl/urls', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          urls: crawlUrls.slice(0, 5), // Limit to first 5 URLs for demo
          max_pages_per_url: 10
        })
      });
      
      const data = await response.json();
      if (data.success) {
        // Show success message
        setTimeout(() => loadKnowledgeStatus(), 2000);
      }
    } catch (error) {
      console.error('Error starting crawl:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const rebuildKnowledgeBase = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/knowledge/knowledge-base/rebuild', {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.success) {
        await loadKnowledgeStatus();
      }
    } catch (error) {
      console.error('Error rebuilding knowledge base:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📚 Knowledge Base Manager
          </h1>
          <p className="text-gray-600">
            Manage vector database, training data, and web crawling for dynamic company contexts
          </p>
        </div>

        {/* Company Selection */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Target Company Selection
          </h2>
          
          <div className="grid md:grid-cols-3 gap-4">
            {Object.entries(availableCompanies).map(([id, company]) => (
              <button
                key={id}
                onClick={() => switchCompany(id)}
                disabled={isLoading}
                className={`p-4 rounded-lg border-2 transition-all ${
                  targetCompany === id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                } disabled:opacity-50`}
              >
                <div className="text-2xl mb-2">{company.emoji}</div>
                <div className="font-semibold">{company.name}</div>
                <div className="text-sm text-gray-600">{company.industry}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Knowledge Base Status */}
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Database className="h-5 w-5 mr-2" />
              Vector Database Status
            </h3>
            
            {knowledgeStatus && knowledgeStatus.status ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Qdrant Service:</span>
                  <span className={knowledgeStatus.status.qdrant_available ? 'text-green-600' : 'text-red-600'}>
                    {knowledgeStatus.status.qdrant_available ? '✅ Active' : '❌ Inactive'}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span>Firecrawl Service:</span>
                  <span className={knowledgeStatus.status.firecrawl_available ? 'text-green-600' : 'text-orange-600'}>
                    {knowledgeStatus.status.firecrawl_available ? '✅ Active' : '⚠️ Mock Mode'}
                  </span>
                </div>
                
                {knowledgeStatus.status.qdrant_metrics && (
                  <div className="border-t pt-3 mt-3">
                    <div className="text-sm text-gray-600">
                      <div>Indexed Points: {knowledgeStatus.status.qdrant_metrics.indexed_points || 0}</div>
                      <div>Vector Dimension: {knowledgeStatus.status.qdrant_metrics.embedding_dimension}</div>
                    </div>
                  </div>
                )}
                
                <button
                  onClick={rebuildKnowledgeBase}
                  disabled={isLoading}
                  className="w-full mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Rebuild Knowledge Base
                </button>
              </div>
            ) : knowledgeStatus === null ? (
              <div className="text-center py-4">
                <div className="text-red-600 mb-2">❌ Backend Service Unavailable</div>
                <div className="text-sm text-gray-600">
                  Please ensure the backend is running:
                  <code className="block mt-1 text-xs bg-gray-100 p-1 rounded">cd backend && python main.py</code>
                </div>
              </div>
            ) : (
              <div className="text-gray-500">Loading status...</div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Training Data
            </h3>
            
            <div className="space-y-4">
              <button
                onClick={generateTrainingData}
                disabled={isLoading}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                Generate Mock Tickets (50)
              </button>
              
              {trainingData && (
                <div className="border-t pt-4">
                  <div className="text-sm space-y-2">
                    <div>Generated: {trainingData.tickets_generated} tickets</div>
                    <div>Resolution Rate: {(trainingData.insights.resolution_rate * 100).toFixed(1)}%</div>
                    <div>Avg Resolution: {trainingData.insights.avg_resolution_time_hours}h</div>
                    <div>Satisfaction: {trainingData.insights.avg_satisfaction_rating}/5</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Knowledge Search */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Search className="h-5 w-5 mr-2" />
            Knowledge Base Search
          </h3>
          
          <div className="flex space-x-4 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search knowledge base..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500"
              onKeyPress={(e) => e.key === 'Enter' && searchKnowledgeBase()}
            />
            <button
              onClick={searchKnowledgeBase}
              disabled={isLoading || !searchQuery.trim()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Search
            </button>
          </div>
          
          {searchResults.length > 0 && (
            <div className="space-y-3">
              {searchResults.map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="font-medium text-gray-900">{result.title}</div>
                  <div className="text-sm text-gray-600 mt-1">{result.category}</div>
                  <div className="text-sm text-gray-800 mt-2">{result.content.substring(0, 200)}...</div>
                  <div className="text-xs text-blue-600 mt-2">
                    Similarity Score: {(result.similarity_score * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Web Crawling */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Globe className="h-5 w-5 mr-2" />
            Web Crawling ({availableCompanies[targetCompany]?.name || 'Unknown'})
          </h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Available URLs to Crawl:</h4>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {crawlUrls.slice(0, 10).map((url, index) => (
                  <div key={index} className="text-sm text-blue-600 hover:text-blue-800">
                    {url}
                  </div>
                ))}
              </div>
              
              <button
                onClick={startCrawling}
                disabled={isLoading || crawlUrls.length === 0}
                className="w-full mt-4 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 disabled:opacity-50"
              >
                Start Crawling (Demo Mode)
              </button>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Crawling Status:</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <div>✓ Documentation sites ready</div>
                <div>✓ Community forums accessible</div>
                <div>✓ Learning resources identified</div>
                <div>⚠️ Firecrawl in mock mode for demo</div>
              </div>
              
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <div className="text-xs text-blue-800">
                  <strong>Note:</strong> In production, this would crawl real documentation,
                  community posts, and support articles to build a comprehensive knowledge base.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBaseManager;
