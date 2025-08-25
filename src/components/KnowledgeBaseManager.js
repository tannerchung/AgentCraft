
import React, { useState, useEffect } from 'react';
import { Database, Search, Globe, FileText, RefreshCw, Settings, Plus, Edit2, Trash2, ExternalLink, AlertCircle, CheckCircle, Download } from 'lucide-react';

const KnowledgeBaseManager = () => {
  const [knowledgeStatus, setKnowledgeStatus] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [targetCompany, setTargetCompany] = useState('zapier');
  const [availableCompanies, setAvailableCompanies] = useState({});
  const [crawlUrls, setCrawlUrls] = useState([]);
  const [trainingData, setTrainingData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('');
  const [operationType, setOperationType] = useState('');
  const [showAddCompany, setShowAddCompany] = useState(false);
  const [showAddUrls, setShowAddUrls] = useState(false);
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newUrls, setNewUrls] = useState('');
  const [servicesStatus, setServicesStatus] = useState(null);
  const [crawlStatus, setCrawlStatus] = useState('idle');
  const [customTrainingCount, setCustomTrainingCount] = useState(50);

  useEffect(() => {
    loadKnowledgeStatus();
    loadCompanies();
    checkServicesStatus();
  }, []);

  useEffect(() => {
    if (targetCompany) {
      loadCompanyCrawlUrls();
    }
  }, [targetCompany]);

  const loadKnowledgeStatus = async () => {
    try {
      const apiUrl = process.env.NODE_ENV === 'development' 
        ? 'http://localhost:8000' 
        : window.location.origin.replace(':3000', ':8000');
      const response = await fetch(`${apiUrl}/api/knowledge/knowledge-base/status`);
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

  const getApiUrl = () => {
    return process.env.NODE_ENV === 'development' 
      ? 'http://localhost:8000' 
      : window.location.origin.replace(':3000', ':8000');
  };

  const loadCompanies = async () => {
    try {
      const response = await fetch(`${getApiUrl()}/api/knowledge/companies`);
      const data = await response.json();
      if (data.success) {
        // Transform backend array to object format
        const companiesObject = {};
        data.companies.forEach(company => {
          companiesObject[company.id] = {
            name: company.name,
            domain: company.domain,
            emoji: company.id === 'zapier' ? '⚡' : company.id === 'hubspot' ? '🧲' : company.id === 'shopify' ? '🛍️' : '🏢',
            industry: company.id === 'zapier' ? 'Automation' : company.id === 'hubspot' ? 'CRM' : company.id === 'shopify' ? 'E-commerce' : 'Business',
            status: company.status,
            indexed_pages: company.indexed_pages
          };
        });
        setAvailableCompanies(companiesObject);
        setTargetCompany(data.current || Object.keys(companiesObject)[0]);
      }
    } catch (error) {
      console.error('Error loading companies:', error);
    }
  };

  const loadCompanyCrawlUrls = async () => {
    try {
      const response = await fetch(`${getApiUrl()}/api/knowledge/crawl/company-urls`);
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
      const response = await fetch(`${getApiUrl()}/api/knowledge/switch-company`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: companyId })
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
      const response = await fetch(`${getApiUrl()}/api/knowledge/knowledge-base/search`, {
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

  const generateTrainingData = async (count = 50) => {
    setIsLoading(true);
    setOperationType('training');
    setLoadingStatus('Analyzing crawled content...');
    
    try {
      const response = await fetch(`${getApiUrl()}/api/knowledge/training-data/generate?count=${count}`);
      
      setLoadingStatus('Generating training questions from community data...');
      const data = await response.json();
      
      if (data.success) {
        setLoadingStatus('Integrating training data into knowledge base...');
        setTrainingData(data);
        
        // Integrate training data into knowledge base for agent use
        await integrateTrainingDataIntoKB(data.training_data);
        
        setLoadingStatus('Training data generated and integrated successfully!');
        setTimeout(() => setLoadingStatus(''), 2000);
      }
    } catch (error) {
      console.error('Error generating training data:', error);
      setLoadingStatus('Failed to generate training data');
      setTimeout(() => setLoadingStatus(''), 3000);
    } finally {
      setIsLoading(false);
      setOperationType('');
    }
  };

  const integrateTrainingDataIntoKB = async (trainingData) => {
    try {
      // Convert training data into knowledge articles for indexing
      const response = await fetch(`${getApiUrl()}/api/knowledge/training-data/integrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          company: targetCompany,
          training_data: trainingData
        })
      });
      
      if (response.ok) {
        // Refresh knowledge status and company counts to show updated indexed pages
        await loadKnowledgeStatus();
        await loadCompanies();
      }
    } catch (error) {
      console.error('Error integrating training data:', error);
    }
  };

  const startCrawling = async () => {
    if (crawlUrls.length === 0) return;
    
    setIsLoading(true);
    setOperationType('crawl');
    setCrawlStatus('crawling');
    setLoadingStatus(`Starting Firecrawl for ${crawlUrls.length} existing URLs...`);
    
    try {
      const response = await fetch(`${getApiUrl()}/api/knowledge/crawl/urls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          urls: crawlUrls, // Use all existing URLs
          company: targetCompany,
          depth: 1,
          re_crawl: true // Flag to indicate this is a re-crawl operation
        })
      });
      
      setLoadingStatus('Processing re-crawled content with Firecrawl...');
      const data = await response.json();
      
      if (data.success) {
        setCrawlStatus('completed');
        const crawlMethod = data.firecrawl_used ? '🔥 Firecrawl API' : '⚠️ Mock mode';
        const indexedInfo = data.auto_indexed ? 
          ` and automatically indexed ${data.content_indexed || 0} items into vector database` : 
          ' (content not indexed)';
        
        setLoadingStatus(`Successfully re-crawled ${crawlUrls.length} URLs using ${crawlMethod}. Extracted ${data.content_extracted || 0} pieces of content${indexedInfo}.`);
        
        // Refresh the knowledge status, URL list, and company page counts
        await loadKnowledgeStatus();
        await loadCompanyCrawlUrls();
        await loadCompanies();
        
        setTimeout(() => {
          setCrawlStatus('idle');
          setLoadingStatus('');
        }, 5000); // Show longer for detailed message
      } else {
        setCrawlStatus('error');
        setLoadingStatus(`Re-crawl failed: ${data.message || 'Unknown error'}${data.firecrawl_used ? ' (Firecrawl was available)' : ' (Firecrawl unavailable)'}`);
        setTimeout(() => {
          setCrawlStatus('idle');
          setLoadingStatus('');
        }, 4000);
      }
    } catch (error) {
      console.error('Error re-crawling URLs:', error);
      setCrawlStatus('error');
      setLoadingStatus('Failed to re-crawl URLs');
      setTimeout(() => {
        setCrawlStatus('idle');
        setLoadingStatus('');
      }, 3000);
    } finally {
      setIsLoading(false);
      setOperationType('');
    }
  };

  const rebuildKnowledgeBase = async (force = false) => {
    setIsLoading(true);
    setOperationType('rebuild');
    setLoadingStatus(force ? 'Force rebuilding knowledge base...' : 'Rebuilding knowledge base...');
    
    try {
      const response = await fetch(`${getApiUrl()}/api/knowledge/knowledge-base/rebuild`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          company: targetCompany,
          force: force 
        })
      });
      
      setLoadingStatus('Processing crawled content...');
      const data = await response.json();
      
      if (data.success) {
        if (data.integration === 'live') {
          setLoadingStatus(`Successfully indexed ${data.qdrant_indexed} items into vector database`);
        } else {
          setLoadingStatus('Rebuilt in mock mode - connect Qdrant for live search');
        }
        
        await loadKnowledgeStatus();
        await loadCompanyCrawlUrls();
        await loadCompanies();
        
        setTimeout(() => setLoadingStatus(''), 3000);
      } else {
        setLoadingStatus(`Rebuild failed: ${data.message || 'Unknown error'}`);
        setTimeout(() => setLoadingStatus(''), 3000);
      }
    } catch (error) {
      console.error('Error rebuilding knowledge base:', error);
      setLoadingStatus('Failed to rebuild knowledge base');
      setTimeout(() => setLoadingStatus(''), 3000);
    } finally {
      setIsLoading(false);
      setOperationType('');
    }
  };

  const checkServicesStatus = async () => {
    try {
      const response = await fetch(`${getApiUrl()}/api/knowledge/services/test`);
      const data = await response.json();
      setServicesStatus(data);
    } catch (error) {
      console.error('Error checking services status:', error);
    }
  };

  const addNewCompany = async () => {
    if (!newCompanyName.trim()) return;
    
    setIsLoading(true);
    try {
      // First switch to the new company (this will create it in the backend)
      const response = await fetch(`${getApiUrl()}/api/knowledge/switch-company`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company: newCompanyName.toLowerCase().replace(/\s+/g, '') })
      });
      
      if (response.ok) {
        await loadCompanies();
        setNewCompanyName('');
        setShowAddCompany(false);
      }
    } catch (error) {
      console.error('Error adding company:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addUrlsToCrawl = async () => {
    if (!newUrls.trim()) return;
    
    const urls = newUrls.split('\n').map(url => url.trim()).filter(url => url);
    setIsLoading(true);
    setOperationType('crawl');
    setCrawlStatus('crawling');
    setLoadingStatus(`Starting Firecrawl for ${urls.length} URLs...`);
    
    try {
      const response = await fetch(`${getApiUrl()}/api/knowledge/crawl/urls`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          urls: urls,
          company: targetCompany,
          depth: 1
        })
      });
      
      setLoadingStatus('Processing crawled content...');
      const data = await response.json();
      
      if (data.success) {
        setCrawlStatus('completed');
        setLoadingStatus(`Successfully crawled ${urls.length} URLs and added to knowledge base`);
        
        await loadKnowledgeStatus();
        await loadCompanyCrawlUrls();
        await loadCompanies();
        setNewUrls('');
        setShowAddUrls(false);
        
        setTimeout(() => {
          setCrawlStatus('idle');
          setLoadingStatus('');
        }, 3000);
      }
    } catch (error) {
      console.error('Error adding URLs:', error);
      setCrawlStatus('error');
      setLoadingStatus('Failed to crawl URLs');
      setTimeout(() => {
        setCrawlStatus('idle');
        setLoadingStatus('');
      }, 3000);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadTrainingData = () => {
    if (!trainingData) return;
    
    const dataStr = JSON.stringify(trainingData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${targetCompany}-training-data.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
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

        {/* Loading Status Indicator */}
        {(isLoading || loadingStatus) && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-3"></div>
              <div>
                <div className="text-sm font-medium text-blue-900">
                  {operationType === 'training' && '🧠 Training Data Generation'}
                  {operationType === 'rebuild' && '🔄 Knowledge Base Rebuild'}
                  {operationType === 'crawl' && '🌐 Web Crawling'}
                  {!operationType && 'Processing...'}
                </div>
                {loadingStatus && (
                  <div className="text-sm text-blue-700 mt-1">{loadingStatus}</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Company Selection */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              Company Management
            </h2>
            <button
              onClick={() => setShowAddCompany(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center text-sm"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add Company
            </button>
          </div>
          
          <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
            {Object.entries(availableCompanies).map(([id, company]) => (
              <div
                key={id}
                className={`p-4 rounded-lg border-2 transition-all ${
                  targetCompany === id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-2xl mb-2">{company.emoji}</div>
                <div className="font-semibold">{company.name}</div>
                <div className="text-xs text-gray-600 mb-2">{company.industry}</div>
                <div className="text-xs text-green-600 mb-3">
                  {company.indexed_pages || 0} pages indexed
                </div>
                {targetCompany !== id && (
                  <button
                    onClick={() => switchCompany(id)}
                    disabled={isLoading}
                    className="w-full bg-gray-600 text-white px-3 py-1 rounded text-sm hover:bg-gray-700 disabled:opacity-50"
                  >
                    Select
                  </button>
                )}
                {targetCompany === id && (
                  <div className="text-center text-xs text-blue-600 font-medium">
                    ✓ Active
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Add Company Modal */}
          {showAddCompany && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                <h3 className="text-lg font-semibold mb-4">Add New Company</h3>
                <input
                  type="text"
                  value={newCompanyName}
                  onChange={(e) => setNewCompanyName(e.target.value)}
                  placeholder="Company name (e.g., Microsoft, Google)"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500"
                  onKeyPress={(e) => e.key === 'Enter' && addNewCompany()}
                />
                <div className="flex space-x-3">
                  <button
                    onClick={addNewCompany}
                    disabled={isLoading || !newCompanyName.trim()}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    Add Company
                  </button>
                  <button
                    onClick={() => {setShowAddCompany(false); setNewCompanyName('');}}
                    className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
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
                    {knowledgeStatus.status.firecrawl_available ? '✅ Live Mode' : '⚠️ Mock Mode'}
                  </span>
                </div>

                <div className="flex justify-between">
                  <span>Knowledge Base:</span>
                  <span className="text-blue-600">
                    {knowledgeStatus.indexed_pages || 0} pages indexed
                  </span>
                </div>

                <div className="flex justify-between">
                  <span>Current Company:</span>
                  <span className="text-blue-600 font-medium">
                    {availableCompanies[targetCompany]?.name || targetCompany}
                  </span>
                </div>
                
                <div className="border-t pt-3 mt-3 space-y-2">
                  <button
                    onClick={() => rebuildKnowledgeBase(false)}
                    disabled={isLoading}
                    className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Rebuild Knowledge Base
                  </button>
                  <button
                    onClick={() => rebuildKnowledgeBase(true)}
                    disabled={isLoading}
                    className="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center justify-center text-sm"
                  >
                    <AlertCircle className="h-4 w-4 mr-2" />
                    Force Rebuild (Clear All)
                  </button>
                </div>
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
              {!trainingData && crawlUrls.length === 0 && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-4">
                  <div className="text-sm text-orange-800">
                    <div className="font-medium mb-1">💡 Better Training Data Tip:</div>
                    Add community URLs (forums, help centers) to generate training data from real user questions and solutions!
                  </div>
                </div>
              )}

              {/* Quick Generate Buttons */}
              <div className="flex space-x-2 mb-3">
                <button
                  onClick={() => generateTrainingData(25)}
                  disabled={isLoading}
                  className="flex-1 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center text-sm"
                >
                  <FileText className="h-4 w-4 mr-1" />
                  Quick (25)
                </button>
                <button
                  onClick={() => generateTrainingData(100)}
                  disabled={isLoading}
                  className="flex-1 bg-green-700 text-white px-3 py-2 rounded-lg hover:bg-green-800 disabled:opacity-50 flex items-center justify-center text-sm"
                >
                  <FileText className="h-4 w-4 mr-1" />
                  Large (100)
                </button>
              </div>

              {/* Custom Amount Input */}
              <div className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                <div className="flex items-center space-x-2">
                  <label className="text-sm font-medium text-gray-700 whitespace-nowrap">Custom Amount:</label>
                  <input
                    type="number"
                    min="1"
                    max="200"
                    value={customTrainingCount}
                    onChange={(e) => setCustomTrainingCount(Math.max(1, Math.min(200, parseInt(e.target.value) || 50)))}
                    className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-blue-500"
                    placeholder="50"
                  />
                  <button
                    onClick={() => generateTrainingData(customTrainingCount)}
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-4 py-1.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center text-sm"
                  >
                    <FileText className="h-4 w-4 mr-1" />
                    Generate
                  </button>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Generate 1-200 training items (more items = better coverage of crawled content)
                </div>
              </div>
              
              {trainingData && (
                <div className="border-t pt-4">
                  <div className="text-sm space-y-2 mb-4">
                    <div className="flex justify-between">
                      <span>Company:</span>
                      <span className="font-medium">{trainingData.company}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Training Items:</span>
                      <span className="font-medium">{trainingData.count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>From Crawled Data:</span>
                      <span className="font-medium text-green-600">{trainingData.sources?.from_crawled_data || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Community Content:</span>
                      <span className="font-medium text-blue-600">{trainingData.sources?.community_content || 0}</span>
                    </div>
                  </div>

                  {trainingData.url_breakdown && (
                    <div className="mb-4 p-2 bg-gray-50 rounded text-xs">
                      <div className="font-medium mb-1">Content Sources:</div>
                      <div className="grid grid-cols-2 gap-1">
                        {Object.entries(trainingData.url_breakdown).map(([type, count]) => (
                          count > 0 && (
                            <div key={type} className="flex justify-between">
                              <span className="capitalize">{type}:</span>
                              <span className={type === 'community' ? 'text-blue-600 font-medium' : ''}>{count}</span>
                            </div>
                          )
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="space-y-2">
                    <button
                      onClick={downloadTrainingData}
                      className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center justify-center text-sm"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Training Data
                    </button>
                    
                    <div className="max-h-40 overflow-y-auto border rounded p-2 bg-gray-50">
                      <div className="text-xs text-gray-600">
                        <div className="font-medium mb-2">Sample Questions & Sources:</div>
                        {trainingData.training_data.slice(0, 5).map((item, i) => (
                          <div key={i} className="mb-2 pb-2 border-b border-gray-200 last:border-b-0">
                            <div className="font-medium">• {item.question}</div>
                            <div className="text-gray-500 mt-1">
                              <span className={`inline-block px-1 py-0.5 rounded text-xs ${
                                item.content_type === 'community' ? 'bg-blue-100 text-blue-700' :
                                item.content_type === 'support' ? 'bg-green-100 text-green-700' :
                                item.content_type === 'api' ? 'bg-purple-100 text-purple-700' :
                                'bg-gray-100 text-gray-600'
                              }`}>
                                {item.content_type}
                              </span>
                              {item.crawl_source && <span className="ml-1 text-green-600">📄</span>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
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
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Globe className="h-5 w-5 mr-2" />
              Web Crawling - {availableCompanies[targetCompany]?.name || 'Unknown'}
            </h3>
            <button
              onClick={() => setShowAddUrls(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center text-sm"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add URLs
            </button>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-medium text-gray-900">URLs to Crawl ({crawlUrls.length})</h4>
                <div className={`text-xs px-2 py-1 rounded-full ${
                  crawlStatus === 'crawling' ? 'bg-orange-100 text-orange-600' :
                  crawlStatus === 'completed' ? 'bg-green-100 text-green-600' :
                  crawlStatus === 'error' ? 'bg-red-100 text-red-600' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {crawlStatus === 'crawling' ? 'Crawling...' :
                   crawlStatus === 'completed' ? 'Completed' :
                   crawlStatus === 'error' ? 'Error' :
                   'Ready'}
                </div>
              </div>

              <div className="space-y-2 max-h-48 overflow-y-auto border rounded-lg p-3 bg-gray-50">
                {crawlUrls.length === 0 ? (
                  <div className="text-center py-4 text-gray-500 text-sm">
                    No URLs added yet. Click "Add URLs" to start.
                  </div>
                ) : (
                  crawlUrls.map((url, index) => (
                    <div key={index} className="flex items-center space-x-2 text-sm">
                      <ExternalLink className="h-3 w-3 text-gray-400 flex-shrink-0" />
                      <a href={url} target="_blank" rel="noopener noreferrer" 
                         className="text-blue-600 hover:text-blue-800 truncate">
                        {url}
                      </a>
                    </div>
                  ))
                )}
              </div>
              
              <button
                onClick={() => startCrawling()}
                disabled={isLoading || crawlUrls.length === 0}
                className="w-full mt-4 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center justify-center"
              >
                <Globe className="h-4 w-4 mr-2" />
                {crawlUrls.length > 0 ? 'Re-crawl All URLs' : 'Start Crawling'}
              </button>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Service Status</h4>
              
              {servicesStatus && servicesStatus.services ? (
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Qdrant:</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      servicesStatus.services.qdrant?.available 
                        ? 'bg-green-100 text-green-600' 
                        : 'bg-red-100 text-red-600'
                    }`}>
                      {servicesStatus.services.qdrant?.status || 'Unknown'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-sm">Firecrawl:</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      servicesStatus.services.firecrawl?.available 
                        ? 'bg-green-100 text-green-600' 
                        : 'bg-orange-100 text-orange-600'
                    }`}>
                      {servicesStatus.services.firecrawl?.status || 'Unknown'}
                    </span>
                  </div>

                  <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                    <div className="text-xs text-blue-800">
                      <div className="font-medium mb-1">Setup Guide:</div>
                      {!servicesStatus.services.firecrawl?.available && (
                        <div className="mb-1">• Get Firecrawl API key at firecrawl.dev and add FIRECRAWL_API_KEY to .env</div>
                      )}
                      {!servicesStatus.services.qdrant?.available && (
                        <div>• For local: docker run -p 6333:6333 qdrant/qdrant</div>
                      )}
                      {!servicesStatus.services.qdrant?.available && (
                        <div>• For cloud: Add QDRANT_URL and QDRANT_API_KEY to .env</div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-500">Loading service status...</div>
              )}
            </div>
          </div>

          {/* Add URLs Modal */}
          {showAddUrls && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
                <h3 className="text-lg font-semibold mb-4">Add URLs to Crawl</h3>
                
                {/* URL suggestions based on current company */}
                <div className="mb-3">
                  <div className="text-xs font-medium text-gray-700 mb-2">💡 Suggested URLs for {availableCompanies[targetCompany]?.name}:</div>
                  <div className="text-xs text-blue-600 space-y-1">
                    {targetCompany === 'zapier' && (
                      <>
                        <div>• https://community.zapier.com (Community Q&A)</div>
                        <div>• https://zapier.com/help (Help Center)</div>
                        <div>• https://platform.zapier.com/docs (API Docs)</div>
                      </>
                    )}
                    {targetCompany === 'hubspot' && (
                      <>
                        <div>• https://community.hubspot.com (Community Forums)</div>
                        <div>• https://knowledge.hubspot.com (Knowledge Base)</div>
                        <div>• https://developers.hubspot.com/docs (API Docs)</div>
                      </>
                    )}
                    {targetCompany === 'shopify' && (
                      <>
                        <div>• https://community.shopify.com (Community Forums)</div>
                        <div>• https://help.shopify.com (Help Center)</div>
                        <div>• https://shopify.dev/docs (Developer Docs)</div>
                      </>
                    )}
                    {!['zapier', 'hubspot', 'shopify'].includes(targetCompany) && (
                      <>
                        <div>• Add community forums for real user Q&A</div>
                        <div>• Include help/support centers</div>
                        <div>• Add API documentation sites</div>
                      </>
                    )}
                  </div>
                </div>

                <textarea
                  value={newUrls}
                  onChange={(e) => setNewUrls(e.target.value)}
                  placeholder="Enter URLs, one per line (prioritize community forums for better training data):&#10;https://community.example.com&#10;https://help.example.com&#10;https://docs.example.com/api"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500 h-32 resize-none"
                />
                <div className="text-xs text-gray-600 mb-4">
                  🎯 <strong>Best sources for training data:</strong> Community forums, help centers, and Q&A sites contain real user questions and solutions that create high-quality training data.
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={addUrlsToCrawl}
                    disabled={isLoading || !newUrls.trim()}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    {crawlStatus === 'crawling' ? 'Crawling...' : 'Add & Crawl URLs'}
                  </button>
                  <button
                    onClick={() => {setShowAddUrls(false); setNewUrls('');}}
                    className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBaseManager;
