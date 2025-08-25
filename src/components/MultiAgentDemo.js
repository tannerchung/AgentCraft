import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, User, Bot, Brain, AlertTriangle, CheckCircle, 
  Clock, Activity, Terminal, Users, HandMetal, Eye,
  ChevronRight, Loader2, Shield, Database,
  CreditCard, BarChart3, Target, ArrowRight, Copy, Check
} from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

// Custom Message Component with Markdown rendering
const MessageContent = ({ content }) => {
  const [copiedCode, setCopiedCode] = useState(null);

  const copyToClipboard = (code, index) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(index);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  // Process content to handle newlines, HTML entities, and ensure proper markdown
  let processedContent = content
    .replace(/\\n/g, '\n')  // Replace literal \n with actual newlines
    .replace(/\\r\\n/g, '\n')  // Handle Windows-style line breaks
    .replace(/\\t/g, '  ')  // Replace tabs with spaces
    .replace(/&lt;/g, '<')  // Decode HTML entities
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, '\n\n')  // Normalize multiple newlines to double
    .trim();

  // Check if content looks like it has markdown formatting
  const hasMarkdown = /[*_#`[\]]/g.test(processedContent);

  // If no markdown detected and has newlines, convert to basic markdown
  if (!hasMarkdown && processedContent.includes('\n')) {
    processedContent = processedContent
      .split('\n\n')
      .map(paragraph => paragraph.trim())
      .filter(paragraph => paragraph.length > 0)
      .join('\n\n');
  }

  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown
        remarkPlugins={[]}
        rehypePlugins={[]}
        components={{
        // Custom code block rendering
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          const codeString = String(children).replace(/\n$/, '');

          if (!inline && match) {
            const codeIndex = Math.random();
            return (
              <div className="relative group my-3">
                <button
                  onClick={() => copyToClipboard(codeString, codeIndex)}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-300"
                  title="Copy code"
                >
                  {copiedCode === codeIndex ? (
                    <Check className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
                <SyntaxHighlighter
                  style={oneDark}
                  language={match[1]}
                  customStyle={{
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                    margin: 0
                  }}
                >
                  {codeString}
                </SyntaxHighlighter>
              </div>
            );
          } else if (!inline) {
            // Code block without language
            const codeIndex = Math.random();
            return (
              <div className="relative group my-3">
                <button
                  onClick={() => copyToClipboard(codeString, codeIndex)}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-300"
                  title="Copy code"
                >
                  {copiedCode === codeIndex ? (
                    <Check className="w-4 h-4 text-green-400" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                  <code>{codeString}</code>
                </pre>
              </div>
            );
          } else {
            // Inline code
            return (
              <code className="bg-gray-200 text-red-600 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                {children}
              </code>
            );
          }
        },
        // Custom paragraph styling with proper line break handling
        p: ({ children }) => (
          <p className="mb-3 text-gray-800 leading-relaxed whitespace-pre-wrap">
            {children}
          </p>
        ),
        // Custom list styling
        ul: ({ children }) => <ul className="list-disc pl-5 mb-3 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-5 mb-3 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="text-gray-800">{children}</li>,
        // Custom heading styling
        h1: ({ children }) => <h1 className="text-xl font-bold mb-3 text-gray-900">{children}</h1>,
        h2: ({ children }) => <h2 className="text-lg font-bold mb-2 text-gray-900">{children}</h2>,
        h3: ({ children }) => <h3 className="text-base font-bold mb-2 text-gray-900">{children}</h3>,
        // Custom strong/bold text
        strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
        // Custom emphasis/italic text
        em: ({ children }) => <em className="italic text-gray-800">{children}</em>,
        // Custom blockquote
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-3 bg-blue-50 rounded-r">
            {children}
          </blockquote>
        ),
        // Custom horizontal rule
        hr: () => <hr className="my-4 border-gray-300" />,
        // Custom link styling
        a: ({href, children}) => (
          <a href={href} className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">
            {children}
          </a>
        ),
        // Custom table styling
        table: ({ children }) => (
          <div className="overflow-x-auto my-3">
            <table className="min-w-full divide-y divide-gray-300 border border-gray-300 rounded-lg">
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => <thead className="bg-gray-50">{children}</thead>,
        tbody: ({ children }) => <tbody className="bg-white divide-y divide-gray-200">{children}</tbody>,
        tr: ({ children }) => <tr>{children}</tr>,
        th: ({ children }) => <th className="px-3 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">{children}</th>,
        td: ({ children }) => <td className="px-3 py-2 text-sm text-gray-900">{children}</td>,
      }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
};

const MultiAgentDemo = () => {
  // Chat state (customer view)
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your AgentCraft assistant. I can demonstrate multi-agent collaboration with specialized knowledge routing. Try asking about webhooks, competitive analysis, or technical integrations!',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Target Company Selection State
  const [targetCompany, setTargetCompany] = useState('zapier');
  const [availableCompanies, setAvailableCompanies] = useState({
    zapier: { name: 'Zapier', emoji: '⚡', color: 'orange' },
    hubspot: { name: 'HubSpot', emoji: '🧲', color: 'orange' },
    shopify: { name: 'Shopify', emoji: '🛍️', color: 'green' }
  });

  // Debug console state
  const [debugLogs, setDebugLogs] = useState([]);
  const [activeAgents, setActiveAgents] = useState([]);
  const [agentAnalysis, setAgentAnalysis] = useState({});

  // HITL state
  const [hitlRequest, setHitlRequest] = useState(null);
  const [hitlResponse, setHitlResponse] = useState('');
  const [showHitl, setShowHitl] = useState(false);

  // UI state
  const [showDebugConsole, setShowDebugConsole] = useState(true);
  const [conversationActive, setConversationActive] = useState(false);
  const [currentQueryAgents, setCurrentQueryAgents] = useState([]); // Agents used in current query

  // Feedback state
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  // WebSocket and real-time tracking state
  const [websocket, setWebsocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [realTimeSession, setRealTimeSession] = useState(null);
  const [liveAgentStates, setLiveAgentStates] = useState({});

  const debugConsoleRef = useRef(null);
  const chatEndRef = useRef(null);
  const clientId = useRef(`client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  // Agent library - loaded from database API
  const [agentLibrary, setAgentLibrary] = useState({});
  const [agentLibraryLoading, setAgentLibraryLoading] = useState(true);
  const [agentLibraryError, setAgentLibraryError] = useState(null);

  // Load agent library from database API
  useEffect(() => {
    const fetchAgentLibrary = async () => {
      setAgentLibraryLoading(true);
      setAgentLibraryError(null);

      try {
        const response = await axios.get('http://localhost:8000/api/agents/list');

        if (response.data.success) {
          setAgentLibrary(response.data.agents);
          addDebugLog('system', 'info', `Loaded ${response.data.total_count} agents from database`);
        } else {
          throw new Error(response.data.error || 'Failed to load agents');
        }
      } catch (error) {
        console.error('Error loading agent library:', error);
        setAgentLibraryError(error.message);
        addDebugLog('system', 'error', `Failed to load agent library: ${error.message}`);
      } finally {
        setAgentLibraryLoading(false);
      }
    };

    fetchAgentLibrary();
  }, []);

  // WebSocket connection for real-time agent tracking
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://localhost:8000/api/ws/agent-tracking/${clientId.current}`);

        ws.onopen = () => {
          setConnectionStatus('connected');
          setWebsocket(ws);
          addDebugLog('websocket', 'system', 'Connected to real-time agent tracking');
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };

        ws.onclose = () => {
          setConnectionStatus('disconnected');
          setWebsocket(null);
          addDebugLog('websocket', 'system', 'Disconnected from real-time tracking');

          // Attempt to reconnect after 3 seconds
          setTimeout(() => {
            if (connectionStatus !== 'connected') {
              connectWebSocket();
            }
          }, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('error');
          addDebugLog('websocket', 'system', 'WebSocket connection error');
        };

      } catch (err) {
        console.error('Failed to create WebSocket connection:', err);
        setConnectionStatus('error');
      }
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle WebSocket messages for real-time updates
  const handleWebSocketMessage = (message) => {
    const { type, data, timestamp, session_id } = message;

    switch (type) {
      case 'session_started':
        setRealTimeSession(session_id);
        setLiveAgentStates({});
        setCurrentQueryAgents(data.agent_names || []);
        addDebugLog('crewai', 'realtime', `Session started: ${session_id}`);
        addDebugLog('crewai', 'realtime', `Agents: ${(data.agent_names || []).join(', ')}`);
        break;

      case 'agent_status_update':
        if (data.session_id === realTimeSession || !realTimeSession) {
          const agentName = data.agent_name;
          const status = data.status;
          const progress = data.progress || 0;

          setLiveAgentStates(prev => ({
            ...prev,
            [agentName]: {
              status,
              progress,
              current_task: data.current_task || '',
              details: data.details || '',
              updated_at: timestamp
            }
          }));

          // Update active agents list
          if (status === 'ANALYZING' || status === 'PROCESSING' || status === 'COLLABORATING') {
            setActiveAgents(prev => {
              if (!prev.includes(agentName)) {
                return [...prev, agentName];
              }
              return prev;
            });
          } else if (status === 'FINISHED' || status === 'ERROR') {
            setActiveAgents(prev => prev.filter(name => name !== agentName));
          }

          const statusText = status.toLowerCase().replace('_', ' ');
          addDebugLog('crewai', 'agent_update', 
            `${agentName}: ${statusText} (${progress}%) - ${data.details || data.current_task || ''}`
          );
        }
        break;

      case 'crew_output':
        if (data.session_id === realTimeSession || !realTimeSession) {
          const outputType = data.output_type || 'general';
          const content = data.content || '';
          const agentName = data.agent_name || 'system';

          addDebugLog('crewai', agentName, `[${outputType}] ${content}`);
        }
        break;

      case 'phase_update':
        if (data.session_id === realTimeSession || !realTimeSession) {
          addDebugLog('crewai', 'orchestrator', `Phase: ${data.phase}`);
        }
        break;

      case 'session_complete':
        if (data.session_id === realTimeSession || !realTimeSession) {
          setActiveAgents([]);
          addDebugLog('crewai', 'realtime', 'Session completed');
          setRealTimeSession(null);
        }
        break;

      case 'session_error':
        if (data.session_id === realTimeSession || !realTimeSession) {
          setActiveAgents([]);
          addDebugLog('error', 'crewai', `Session error: ${data.error}`);
          setRealTimeSession(null);
        }
        break;

      case 'crewai_log':
        // Handle CrewAI log streaming
        if (message.log) {
          const log = message.log;
          const logLevel = log.level || 'INFO';
          const logMessage = log.message || log.raw_message || '';

          // Format log message for debug console
          let displayMessage = logMessage;
          if (log.agent_info && log.agent_info.agent_name) {
            displayMessage = `[${log.agent_info.agent_name}] ${logMessage}`;
          }

          // Add to debug logs with appropriate level
          const debugLevel = logLevel.toLowerCase() === 'error' ? 'error' : 
                           logLevel.toLowerCase() === 'warning' ? 'warning' : 'info';

          addDebugLog('crewai', debugLevel, displayMessage);

          // If it's an agent-specific event, update live agent states
          if (log.event_type && log.agent_info && log.agent_info.agent_name) {
            const agentName = log.agent_info.agent_name;
            setLiveAgentStates(prev => ({
              ...prev,
              [agentName]: {
                ...prev[agentName],
                last_log: displayMessage,
                last_event: log.event_type,
                updated_at: log.timestamp
              }
            }));
          }
        }
        break;

      case 'log_streaming_started':
        addDebugLog('websocket', 'system', `CrewAI log streaming started for session: ${message.session_id}`);
        break;

      case 'log_streaming_stopped':
        addDebugLog('websocket', 'system', 'CrewAI log streaming stopped');
        break;

      case 'ping':
        // Send pong response to keep connection alive
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          websocket.send(JSON.stringify({ type: 'pong' }));
        }
        break;

      default:
        console.log('Unknown WebSocket message type:', type, message);
    }
  };

  // Scroll to bottom helpers
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (debugConsoleRef.current) {
      debugConsoleRef.current.scrollTop = debugConsoleRef.current.scrollHeight;
    }
  }, [debugLogs]);

  // Add debug log
  const addDebugLog = (type, agent, message, data = null) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugLogs(prev => [...prev, {
      timestamp,
      type,
      agent,
      message,
      data,
      id: Date.now()
    }]);
  };

  // Simulate agent selection based on query
  const selectAgents = (query) => {
    const queryLower = query.toLowerCase();
    const selectedAgents = [];

    // Always include orchestrator
    selectedAgents.push('orchestrator');

    // Score each agent based on keyword matching
    Object.entries(agentLibrary).forEach(([agentId, agent]) => {
      if (agentId === 'orchestrator') return;

      const score = agent.keywords.reduce((acc, keyword) => {
        return queryLower.includes(keyword) ? acc + 1 : acc;
      }, 0);

      if (score > 0) {
        selectedAgents.push(agentId);
      }
    });

    // If no specific agents selected, use technical as default
    if (selectedAgents.length === 1) {
      selectedAgents.push('technical');
    }

    return selectedAgents;
  };

  // Simulate CrewAI agent processing
  const processWithAgent = async (agentId, query, context) => {
    const agent = agentLibrary[agentId];

    addDebugLog('processing', agentId, `${agent.name} analyzing query...`);

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    // Generate agent-specific analysis
    const analysis = {
      agent: agent.name,
      confidence: 0.85 + Math.random() * 0.14,
      findings: [],
      recommendations: [],
      requiresEscalation: false
    };

    // Agent-specific analysis logic
    switch(agentId) {
      case 'technical':
        analysis.findings = [
          "Webhook endpoint returning 403 Forbidden",
          "SSL certificate chain validation failure",
          "HMAC signature mismatch in payload verification"
        ];
        analysis.recommendations = [
          "Update SSL certificate chain",
          "Verify webhook secret configuration",
          "Implement retry logic with exponential backoff"
        ];
        break;

      case 'billing':
        analysis.findings = [
          "Subscription proration calculation issue",
          "Failed payment retry scheduled",
          "Credit balance available for application"
        ];
        analysis.recommendations = [
          "Apply credit to outstanding balance",
          "Update payment method",
          "Review subscription terms"
        ];
        break;

      case 'security':
        analysis.findings = [
          "API key exposed in client-side code",
          "Missing rate limiting on endpoints",
          "Outdated TLS version detected"
        ];
        analysis.recommendations = [
          "Rotate compromised API keys immediately",
          "Implement rate limiting middleware",
          "Upgrade to TLS 1.3"
        ];
        analysis.requiresEscalation = true;
        break;

      case 'competitive':
        analysis.findings = [
          "Cost savings of 67% vs competitor platforms",
          "95% faster implementation time",
          "Superior customization capabilities"
        ];
        analysis.recommendations = [
          "Emphasize ROI in decision matrix",
          "Highlight technical superiority",
          "Provide migration path documentation"
        ];
        break;

      default:
        analysis.findings = ["Query analyzed successfully"];
        analysis.recommendations = ["No specific action required"];
    }

    addDebugLog('analysis', agentId, `Analysis complete (confidence: ${(analysis.confidence * 100).toFixed(1)}%)`, analysis);

    return analysis;
  };

  // Simulate HITL escalation
  const triggerHitlEscalation = (reason, context) => {
    setShowHitl(true);
    setHitlRequest({
      reason,
      context,
      timestamp: new Date().toLocaleTimeString(),
      agentRecommendation: "Human intervention recommended for optimal resolution"
    });

    addDebugLog('escalation', 'system', `HITL escalation triggered: ${reason}`);
  };

  // Handle HITL response
  const submitHitlResponse = () => {
    if (!hitlResponse.trim()) return;

    addDebugLog('hitl', 'human', `Human expert provided input: "${hitlResponse}"`);

    // Add human response to context with formatted header
    const formattedResponse = `## 👨‍💼 Human Expert Response\n\n${hitlResponse}\n\n---\n*This response was provided by a human expert after HITL escalation.*`;

    const humanMessage = {
      id: Date.now(),
      type: 'assistant',
      content: formattedResponse,
      timestamp: new Date().toLocaleTimeString(),
      metadata: {
        source: 'human_expert',
        escalation_resolved: true
      }
    };

    setMessages(prev => [...prev, humanMessage]);
    setHitlResponse('');
    setShowHitl(false);
    setHitlRequest(null);

    // Continue processing with human input
    setTimeout(() => {
      addDebugLog('system', 'orchestrator', 'Incorporating human expertise into response synthesis');
    }, 500);
  };

  // Main message handler
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isProcessing) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsProcessing(true);
    setConversationActive(true);

    // Clear previous analysis
    setAgentAnalysis({});
    setCurrentQueryAgents([]);

    try {
      // Log query receipt
      addDebugLog('received', 'system', `Query received: "${userMessage.content}"`);

      // ALWAYS USE REAL CREWAI - No more simulation
      addDebugLog('routing', 'system', 'Processing with CrewAI agents via backend API');

      // Start log streaming for this session
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        const sessionId = `chat_${Date.now()}`;
        websocket.send(JSON.stringify({ 
          type: 'start_log_streaming',
          session_id: sessionId 
        }));
        addDebugLog('websocket', 'system', `Started CrewAI log streaming for session: ${sessionId}`);
      }

      try {
        // Generate session ID for tracking
        const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Make API call to backend with company context
        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: userMessage.content,
            agent_type: 'orchestrator',
            target_company: targetCompany,
            company_context: availableCompanies[targetCompany]
          })
        });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const result = await response.json();


          // Log backend agent activity
          if (result.agent_info) {
            addDebugLog('backend', 'crewai', `Agent: ${result.agent_info.role || 'Technical Support'}`);
            addDebugLog('processing', 'crewai', `Processing time: ${result.agent_info.processing_time || 'N/A'}`);
          }

          // Extract agent analysis from response
          if (result.query_analysis) {
            Object.entries(result.query_analysis).forEach(([key, value]) => {
              addDebugLog('analysis', 'crewai', `${key}: ${JSON.stringify(value)}`);
            });
          }

          // Check if HITL escalation is needed
          if (result.escalation_required) {
            triggerHitlEscalation(
              result.escalation_reason || "Complex issue requiring human expertise",
              result
            );
            setIsProcessing(false);
            return;
          }

          // Format the response content
          let responseContent = result.response?.content || result.response?.response || "Response received from CrewAI";

          const assistantMessage = {
            id: Date.now() + 1,
            type: 'assistant',
            content: responseContent,
            timestamp: new Date().toLocaleTimeString(),
            metadata: {
              source: 'crewai_backend',
              ai_powered: result.ai_powered || false,
              processing_time: result.agent_info?.processing_time || 'N/A',
              confidence: result.query_analysis?.ai_confidence || 'High',
              llms_used: result.agent_info?.llms_used || {},
              real_crewai: true,
              agents_used: result.agent_info?.agents_used || [] // Add agents_used
            }
          };

          setMessages(prev => [...prev, assistantMessage]);

          addDebugLog('complete', 'crewai', 
            `Real CrewAI response delivered (${result.agent_info?.processing_time || 'N/A'})`
          );

          // If Galileo is enabled, log that traces were sent
          if (result.galileo_logged) {
            addDebugLog('observability', 'galileo', 'Conversation traced to Galileo dashboard');
          }

        } catch (apiError) {
          console.error('Backend API error:', apiError);
          addDebugLog('error', 'backend', `API Error: ${apiError.message}`);

          // Show error message instead of simulation
          setMessages(prev => [...prev, {
            id: Date.now(),
            type: 'assistant',
            content: '⚠️ Backend service is not available. Please ensure the backend is running:\n\n```bash\nuv run python backend/main.py\n```\n\nThen try your message again.',
            timestamp: new Date().toLocaleTimeString(),
            metadata: {
              source: 'system',
              error: true
            }
          }]);
        }


    } catch (error) {
      console.error('Error processing message:', error);
      addDebugLog('error', 'system', `Error: ${error.message}`);

      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'assistant',
        content: "I encountered an error processing your request. Please try again.",
        timestamp: new Date().toLocaleTimeString(),
        error: true
      }]);
    } finally {
      setIsProcessing(false);
      setActiveAgents([]);
    }
  };

  // Generate customer service response from agent analyses
  const generateCustomerResponse = (analysisMap) => {
    const customerAgents = Object.entries(analysisMap)
      .filter(([agentId, _]) => agentId !== 'orchestrator')
      .map(([_, analysis]) => analysis);

    if (customerAgents.length === 0) {
      return "I've reviewed your request and I'm working to identify the best solution for you. Could you provide a few more details about what you're experiencing?";
    }

    // Log technical details to debug console for support agents
    customerAgents.forEach((analysis, index) => {
      addDebugLog('technical', 'support_view', 
        `Agent ${index + 1} Technical Analysis:`, {
          findings: analysis.findings,
          recommendations: analysis.recommendations,
          confidence: analysis.confidence
        }
      );
    });

    // Generate natural customer service response based on analysis
    const allFindings = [];
    customerAgents.forEach(analysis => {
      allFindings.push(...analysis.findings);
    });

    let customerResponse = "";

    // Detect the type of issue for personalized response
    const hasWebhookIssues = allFindings.some(f => 
      f.toLowerCase().includes('webhook') || f.toLowerCase().includes('403') || f.toLowerCase().includes('ssl')
    );
    const hasBillingIssues = allFindings.some(f => 
      f.toLowerCase().includes('billing') || f.toLowerCase().includes('payment') || f.toLowerCase().includes('subscription')
    );
    const hasSecurityIssues = allFindings.some(f => 
      f.toLowerCase().includes('security') || f.toLowerCase().includes('api key') || f.toLowerCase().includes('vulnerability')
    );

    if (hasWebhookIssues) {
      customerResponse = "I've identified some technical issues with your webhook integration that are causing the connectivity problems you're experiencing. ";
      customerResponse += "Our technical team is prepared to help you resolve these SSL certificate and authentication issues. ";
      customerResponse += "We'll work with you to implement the necessary fixes to get your integration running smoothly again.\n\n";
      customerResponse += "**Next Steps:**\n";
      customerResponse += "• I'll coordinate with our technical team to address the certificate configuration\n";
      customerResponse += "• We'll verify your webhook settings and provide updated configurations\n";
      customerResponse += "• I'll follow up with you once the fixes are implemented to ensure everything is working properly\n\n";
    } else if (hasBillingIssues) {
      customerResponse = "I've reviewed your billing inquiry and identified the issue with your account charges. ";
      customerResponse += "It appears there was a calculation error in your subscription proration that resulted in the discrepancy you noticed.\n\n";
      customerResponse += "**What I'm doing for you:**\n";
      customerResponse += "• Processing the appropriate credit adjustment to your account\n";
      customerResponse += "• Reviewing your payment method to prevent future issues\n";
      customerResponse += "• I'll send you a detailed breakdown of the corrected charges within the next hour\n\n";
    } else if (hasSecurityIssues) {
      customerResponse = "Thank you for bringing this security concern to our attention. I've immediately escalated this to our security team for priority handling. ";
      customerResponse += "We take security issues very seriously and will work quickly to address this.\n\n";
      customerResponse += "**Immediate Actions:**\n";
      customerResponse += "• Our security team has been notified and is reviewing your account\n";
      customerResponse += "• We're implementing additional security measures as a precaution\n";
      customerResponse += "• You'll receive a security update within 2 hours with next steps\n\n";
    } else {
      customerResponse = "I've thoroughly reviewed your request and our team has prepared a solution for you. ";
      customerResponse += "We've identified the root cause and have the necessary steps to resolve this efficiently.\n\n";
      customerResponse += "**How we'll help:**\n";
      customerResponse += "• Implementing the technical fixes needed for your specific situation\n";
      customerResponse += "• Coordinating with the relevant teams to ensure a smooth resolution\n";
      customerResponse += "• Following up to confirm everything is working as expected\n\n";
    }

    customerResponse += "*Is there anything specific you'd like me to prioritize or any questions about these next steps?*";

    return customerResponse;
  };

  // End conversation handler
  const endConversation = () => {
    if (messages.length > 0) {
      // Show feedback if there were actual messages exchanged
      setShowFeedback(true);
    } else {
      // No messages, just reset directly
      resetConversation();
    }
  };

  // Reset conversation state
  const resetConversation = () => {
    setConversationActive(false);
    setCurrentQueryAgents([]);
    setActiveAgents([]);
    setMessages([
        {
          id: 1,
          type: 'assistant',
          content: 'Hello! I\'m your AgentCraft assistant. I can demonstrate multi-agent collaboration with specialized knowledge routing. Try asking about webhooks, competitive analysis, or technical integrations!',
          timestamp: new Date().toLocaleTimeString()
        }
      ]); // Reset to initial greeting
    setAgentAnalysis({});
    setDebugLogs([]);
    setShowHitl(false);
    setHitlRequest(null);
    setHitlResponse('');
    setShowFeedback(false);
    setFeedbackRating(0);
    setFeedbackComment('');
    setFeedbackSubmitted(false);
    setRealTimeSession(null);
    setLiveAgentStates({});
    addDebugLog('system', 'conversation', 'Conversation ended - session reset');
  };

  // Submit feedback
  const submitFeedback = () => {
    const feedbackData = {
      timestamp: new Date().toISOString(),
      rating: feedbackRating,
      comment: feedbackComment.trim(),
      conversationLength: messages.length,
      agentsUsed: currentQueryAgents,
      resolutionTime: 'N/A', // Could calculate from first to last message
      crewaiMode: true // Always using CrewAI now
    };

    // Log to debug console for demo purposes
    addDebugLog('feedback', 'customer', 
      `Feedback submitted: ${feedbackRating}/5 stars`, feedbackData
    );

    // In production, this would send to analytics/CRM system
    console.log('Customer Feedback:', feedbackData);

    setFeedbackSubmitted(true);

    // Close feedback after brief delay
    setTimeout(() => {
      resetConversation();
    }, 2000);
  };

  // Skip feedback
  const skipFeedback = () => {
    addDebugLog('feedback', 'system', 'Customer skipped feedback');
    resetConversation();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Users className="w-8 h-8 mr-3 text-blue-600" />
                Multi-Agent Orchestration Demo
                <div className={`ml-4 flex items-center text-sm px-3 py-1 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-100 text-green-700' :
                  connectionStatus === 'error' ? 'bg-red-100 text-red-700' :
                  'bg-yellow-100 text-yellow-700'
                }`}>
                  <div className={`w-2 h-2 rounded-full mr-2 ${
                    connectionStatus === 'connected' ? 'bg-green-500' :
                    connectionStatus === 'error' ? 'bg-red-500' :
                    'bg-yellow-500'
                  }`}></div>
                  Real-time {connectionStatus}
                </div>
              </h1>
              <p className="text-gray-600 mt-2">
                Experience CrewAI-powered agent coordination with live WebSocket updates, debug transparency and HITL capabilities
              </p>
            </div>

            {/* Target Company Selection */}
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700">Target Company:</label>
              <select
                value={targetCompany}
                onChange={(e) => setTargetCompany(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {Object.entries(availableCompanies).map(([id, company]) => (
                  <option key={id} value={id}>
                    {company.emoji} {company.name}
                  </option>
                ))}
              </select>
              <div className="text-xs text-gray-500">
                Context: {availableCompanies[targetCompany].name} Integration Platform
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Chat Interface (Customer View) */}
          <div className="lg:col-span-2">
            {/* Chat Window */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="border-b px-6 py-4">
                <h3 className="font-semibold text-gray-900 flex items-center">
                  <User className="w-5 h-5 mr-2 text-blue-600" />
                  Customer Chat Interface
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  This is what the customer sees - clean, professional responses
                </p>
              </div>

              {/* Real-time Agent Activity Display */}
              {realTimeSession && Object.values(liveAgentStates).some(agent => agent && agent.status && agent.status !== 'idle') && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mx-6 mb-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <Activity className="w-4 h-4 text-blue-600 mr-2 animate-pulse" />
                      <h4 className="font-medium text-blue-900">Active Agents</h4>
                      <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                        {Object.values(liveAgentStates).filter(agent => agent && agent.status && agent.status !== 'idle' && agent.status !== 'finished').length} working
                      </span>
                    </div>
                    <div className="text-xs text-blue-600">
                      {realTimeSession.overall_progress?.toFixed(1)}% complete
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {Object.values(liveAgentStates)
                      .filter(agent => agent && agent.status !== 'idle')
                      .map(agent => (
                        <div key={agent.agent_id} className="bg-white rounded-lg p-3 border border-blue-100">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start min-w-0 flex-1">
                              {/* Agent Avatar from database */}
                              <div className="text-lg mr-2 flex-shrink-0">
                                {(agent.agent_name && agentLibrary[agent.agent_name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')]?.avatar) || '🤖'}
                              </div>
                              <div className="min-w-0 flex-1">
                                <div className="flex items-center">
                                  <h5 className="font-medium text-gray-900 text-sm truncate">
                                    {agent.agent_name || 'Unknown Agent'}
                                  </h5>
                                  <div className={`ml-2 w-2 h-2 rounded-full flex-shrink-0 ${
                                    agent.status === 'ANALYZING' ? 'bg-yellow-400 animate-pulse' :
                                    agent.status === 'PROCESSING' ? 'bg-blue-500 animate-pulse' :
                                    agent.status === 'COLLABORATING' ? 'bg-purple-500 animate-pulse' :
                                    agent.status === 'COMPLETING' ? 'bg-orange-500 animate-pulse' :
                                    agent.status === 'FINISHED' ? 'bg-green-500' :
                                    agent.status === 'ERROR' ? 'bg-red-500' : 'bg-gray-400'
                                  }`}></div>
                                </div>

                                <div className="text-xs text-gray-600 mt-1 capitalize">
                                  {agent.status.replace('_', ' ')}
                                  {agent.current_task && (
                                    <span className="block mt-1 text-gray-500 truncate">
                                      {agent.current_task}
                                    </span>
                                  )}
                                </div>

                                {/* Progress bar */}
                                {agent.progress > 0 && (
                                  <div className="mt-2">
                                    <div className="flex justify-between items-center mb-1">
                                      <span className="text-xs text-gray-500">Progress</span>
                                      <span className="text-xs text-gray-600">{agent.progress.toFixed(0)}%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                                      <div 
                                        className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                                        style={{ width: `${agent.progress}%` }}
                                      ></div>
                                    </div>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>

                  {/* Current Phase Indicator */}
                  {realTimeSession.current_phase && (
                    <div className="mt-3 pt-3 border-t border-blue-100">
                      <div className="flex items-center text-xs text-blue-700">
                        <Clock className="w-3 h-3 mr-1" />
                        <span className="capitalize">Phase: {realTimeSession.current_phase.replace('_', ' ')}</span>
                        {realTimeSession.estimated_completion && (
                          <span className="ml-2 text-blue-600">
                            • ETA: {new Date(realTimeSession.estimated_completion * 1000).toLocaleTimeString()}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="h-96 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <Bot className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                    <p className="mb-4">Start a conversation to see multi-agent orchestration in action</p>

                    {/* Preset Query Buttons */}
                    <div className="space-y-2">
                      <p className="text-xs text-gray-600 mb-2">Quick test scenarios:</p>
                      <div className="flex flex-wrap gap-2 justify-center">
                        <button
                          onClick={() => {
                            setInputMessage("My webhooks are failing with 403 errors and SSL certificate issues");
                          }}
                          className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 text-sm transition-colors"
                        >
                          🔧 Webhook Issues
                        </button>
                        <button
                          onClick={() => {
                            setInputMessage("I have billing discrepancies and need to process a refund");
                          }}
                          className="px-3 py-1.5 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 text-sm transition-colors"
                        >
                          💳 Billing Problem
                        </button>
                        <button
                          onClick={() => {
                            setInputMessage("API keys may be exposed, need security audit immediately");
                          }}
                          className="px-3 py-1.5 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 text-sm transition-colors"
                        >
                          🛡️ Security Alert
                        </button>
                        <button
                          onClick={() => {
                            setInputMessage("Need competitive analysis comparing us to Salesforce AgentForce");
                          }}
                          className="px-3 py-1.5 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 text-sm transition-colors"
                        >
                          🎯 Competitive Intel
                        </button>
                        <button
                          onClick={() => {
                            setInputMessage("Database queries are slow, getting timeout errors, and we have a compliance audit tomorrow");
                          }}
                          className="px-3 py-1.5 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 text-sm transition-colors"
                        >
                          🔥 Complex Multi-Issue
                        </button>
                      </div>
                    </div>
                  </div>
                ) : (
                  messages.map(message => (
                    <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-2xl ${message.type === 'user' ? 'order-2' : ''}`}>
                        <div className="flex items-start space-x-2">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                            message.type === 'user' ? 'bg-blue-100 order-2' : 'bg-gray-100'
                          }`}>
                            {message.type === 'user' ? <User className="w-5 h-5 text-blue-600" /> : <Bot className="w-5 h-5 text-gray-600" />}
                          </div>
                          <div className={`px-4 py-3 rounded-lg ${
                            message.type === 'user' 
                              ? 'bg-blue-600 text-white' 
                              : message.error 
                                ? 'bg-red-50 text-red-900 border border-red-200'
                                : 'bg-white border border-gray-200 shadow-sm'
                          }`}>
                            {message.type === 'user' ? (
                              <div className="text-white">{message.content}</div>
                            ) : (
                              <MessageContent content={message.content} />
                            )}
                            <div className={`text-xs mt-2 flex items-center space-x-2 ${
                              message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
                            }`}>
                              <span>{message.timestamp}</span>
                              {message.metadata?.processing_time && (
                                <>
                                  <span>•</span>
                                  <span>{message.metadata.processing_time}</span>
                                </>
                              )}
                              {message.metadata?.source && (
                                <>
                                  <span>•</span>
                                  <span className={`capitalize ${message.metadata.real_crewai ? 'text-green-600 font-semibold' : ''}`}>
                                    {message.metadata.real_crewai ? '🤖 ' : ''}
                                    {message.metadata.source.replace('_', ' ')}
                                  </span>
                                </>
                              )}
                              {message.metadata?.confidence && (
                                <>
                                  <span>•</span>
                                  <span>
                                    {typeof message.metadata.confidence === 'number' 
                                      ? `${(message.metadata.confidence * 100).toFixed(0)}% confidence`
                                      : message.metadata.confidence}
                                  </span>
                                </>
                              )}
                              {/* Show which agents were involved */}
                              {message.metadata?.agents_used && message.metadata.agents_used.length > 0 && (
                                <>
                                  <span>•</span>
                                  <span className="text-blue-600 font-medium">
                                    {message.metadata.agents_used.map(agentId => {
                                      const agent = agentLibrary[agentId];
                                      return agent ? `${agent.avatar} ${agent.name}` : agentId;
                                    }).join(', ')}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input */}
              <div className="border-t px-6 py-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your message..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    disabled={isProcessing}
                  />
                  {conversationActive && (
                    <button
                      onClick={endConversation}
                      className="px-4 py-2 bg-red-100 text-red-700 border border-red-300 rounded-lg hover:bg-red-200 transition-colors flex items-center"
                      title="End conversation and reset"
                    >
                      <AlertTriangle className="w-4 h-4 mr-1" />
                      End
                    </button>
                  )}
                  <button
                    onClick={handleSendMessage}
                    disabled={isProcessing || !inputMessage.trim()}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
                  >
                    {isProcessing ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Panel */}
          <div className="space-y-4">
            {/* HITL Interface */}
            {showHitl && (
              <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg shadow-sm">
                <div className="px-4 py-3 border-b border-yellow-300 bg-yellow-100">
                  <h3 className="font-semibold text-gray-900 flex items-center">
                    <HandMetal className="w-5 h-5 mr-2 text-yellow-600" />
                    Human-in-the-Loop Required
                  </h3>
                </div>
                <div className="p-4">
                  {hitlRequest && (
                    <div className="space-y-3">
                      <div className="text-sm">
                        <p className="font-medium text-gray-900">Escalation Reason:</p>
                        <p className="text-gray-700 mt-1">{hitlRequest.reason}</p>
                      </div>

                      <div className="text-sm">
                        <p className="font-medium text-gray-900">Agent Recommendation:</p>
                        <p className="text-gray-700 mt-1">{hitlRequest.agentRecommendation}</p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-900 mb-2">
                          Your Expert Input:
                        </label>
                        <textarea
                          value={hitlResponse}
                          onChange={(e) => setHitlResponse(e.target.value)}
                          placeholder="Provide expert guidance..."
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 text-sm"
                          rows={3}
                        />
                      </div>

                      <button
                        onClick={submitHitlResponse}
                        disabled={!hitlResponse.trim()}
                        className="w-full px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 flex items-center justify-center"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Submit Expert Response
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}


            {/* Agent Library */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-4 py-3 border-b">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">Agent Library</h3>
                  {agentLibraryLoading ? (
                    <div className="flex items-center text-xs text-blue-600">
                      <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                      Loading...
                    </div>
                  ) : agentLibraryError ? (
                    <span className="text-xs text-red-600">Error loading</span>
                  ) : (
                    <span className="text-xs text-gray-500">{Object.keys(agentLibrary).length} agents</span>
                  )}
                </div>
                {currentQueryAgents.length > 0 && (
                  <div className="flex items-center text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                    <Activity className="w-3 h-3 mr-1" />
                    <span className="font-medium">Current Query:</span>
                    <span className="ml-1">{currentQueryAgents.length} agents active</span>
                  </div>
                )}
              </div>
              <div className="p-4 space-y-2 max-h-80 overflow-y-auto">
                {agentLibraryLoading ? (
                  <div className="text-center py-8">
                    <Loader2 className="w-6 h-6 mx-auto mb-2 text-blue-600 animate-spin" />
                    <p className="text-sm text-gray-500">Loading agents from database...</p>
                  </div>
                ) : agentLibraryError ? (
                  <div className="text-center py-8">
                    <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-red-600" />
                    <p className="text-sm text-red-600 mb-2">Failed to load agents</p>
                    <p className="text-xs text-gray-500">{agentLibraryError}</p>
                    <button 
                      onClick={() => window.location.reload()} 
                      className="mt-2 text-xs text-blue-600 hover:text-blue-800"
                    >
                      Retry
                    </button>
                  </div>
                ) : Object.keys(agentLibrary).length === 0 ? (
                  <div className="text-center py-8">
                    <Users className="w-6 h-6 mx-auto mb-2 text-gray-400" />
                    <p className="text-sm text-gray-500">No agents available</p>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {Object.entries(agentLibrary)
                    .sort(([idA, agentA], [idB, agentB]) => {
                      const isActiveA = activeAgents.includes(idA) || currentQueryAgents.includes(idA);
                      const isActiveB = activeAgents.includes(idB) || currentQueryAgents.includes(idB);
                      const hasAnalysisA = agentAnalysis[idA];
                      const hasAnalysisB = agentAnalysis[idB];
                      const hasLiveStateA = liveAgentStates[agentA.name] || liveAgentStates[idA];
                      const hasLiveStateB = liveAgentStates[agentB.name] || liveAgentStates[idB];

                      // Sort by: currently active > completed analysis > has live state > inactive
                      if (activeAgents.includes(idA) && !activeAgents.includes(idB)) return -1;
                      if (activeAgents.includes(idB) && !activeAgents.includes(idA)) return 1;
                      if (hasLiveStateA && !hasLiveStateB) return -1;
                      if (hasLiveStateB && !hasLiveStateA) return 1;
                      if (hasAnalysisA && !hasAnalysisB) return -1;
                      if (hasAnalysisB && !hasAnalysisA) return 1;
                      if (isActiveA && !isActiveB) return -1;
                      if (isActiveB && !isActiveA) return 1;
                      return 0;
                    })
                    .map(([id, agent]) => {
                      const isCurrentlyActive = activeAgents.includes(id);
                      const wasUsedInQuery = currentQueryAgents.includes(id);
                      const hasAnalysis = agentAnalysis[id];
                      const liveState = liveAgentStates[agent.name] || liveAgentStates[id];
                      const isLiveActive = liveState && ['ANALYZING', 'PROCESSING', 'COLLABORATING'].includes(liveState.status);
                      const isLiveFinished = liveState && liveState.status === 'FINISHED';

                      return (
                        <div 
                          key={id} 
                          className={`flex items-center space-x-2 text-sm py-2 px-2 rounded transition-all ${
                            isCurrentlyActive || isLiveActive
                              ? 'bg-blue-100 border border-blue-300 shadow-sm' 
                              : isLiveFinished || (wasUsedInQuery && hasAnalysis)
                                ? 'bg-green-50 border border-green-200'
                                : liveState
                                  ? 'bg-gray-50 border border-gray-200'
                                  : 'hover:bg-gray-50'
                          }`}
                        >
                          <div className="relative">
                            <span className="text-lg">{agent.avatar}</span>
                            {(isCurrentlyActive || isLiveActive) && (
                              <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                            )}
                            {(!isCurrentlyActive && !isLiveActive) && (isLiveFinished || hasAnalysis) && (
                              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"></div>
                            )}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center">
                              <span className={`font-medium ${
                                isCurrentlyActive || isLiveActive ? 'text-blue-900' : 
                                isLiveFinished || (wasUsedInQuery && hasAnalysis) ? 'text-green-900' : 
                                liveState ? 'text-gray-800' : 'text-gray-700'
                              }`}>
                                {agent.name}
                              </span>
                              {(isCurrentlyActive || isLiveActive) && (
                                <Loader2 className="w-3 h-3 ml-2 text-blue-500 animate-spin" />
                              )}
                              {(!isCurrentlyActive && !isLiveActive) && (isLiveFinished || hasAnalysis) && (
                                <CheckCircle className="w-3 h-3 ml-2 text-green-500" />
                              )}
                            </div>
                            <p className="text-xs text-gray-500">{agent.role}</p>

                            {/* Show live state info */}
                            {liveState && (
                              <div className="text-xs mt-1">
                                <div className={`${
                                  isLiveActive ? 'text-blue-600' : 
                                  isLiveFinished ? 'text-green-600' : 
                                  'text-gray-600'
                                }`}>
                                  {liveState.status.replace('_', ' ').toLowerCase()} ({liveState.progress}%)
                                </div>
                                {liveState.current_task && (
                                  <div className="text-gray-500 truncate" title={liveState.current_task}>
                                    {liveState.current_task.substring(0, 50)}...
                                  </div>
                                )}
                              </div>
                            )}

                            {/* Fallback to simulation analysis if no live state */}
                            {!liveState && hasAnalysis && !isCurrentlyActive && (
                              <p className="text-xs text-green-600 mt-1">
                                ✓ {hasAnalysis.findings.length} findings • {(hasAnalysis.confidence * 100).toFixed(0)}% confidence
                              </p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Debug Console - Full Width Below */}
        <div className="mt-6 bg-gray-900 rounded-lg shadow-sm border border-gray-800">
          <div className="border-b border-gray-800 px-4 py-3 flex items-center justify-between">
            <h3 className="font-semibold text-gray-100 flex items-center">
              <Terminal className="w-5 h-5 mr-2 text-green-400" />
              Debug Console (Backend View)
            </h3>
            <button
              onClick={() => setShowDebugConsole(!showDebugConsole)}
              className="text-gray-400 hover:text-gray-200"
            >
              <Eye className="w-5 h-5" />
            </button>
          </div>

          {showDebugConsole && (
            <div 
              ref={debugConsoleRef}
              className="h-64 overflow-y-auto p-4 font-mono text-sm"
            >
              {debugLogs.length === 0 ? (
                <div className="text-gray-500">
                  <p>$ Waiting for agent activity...</p>
                </div>
              ) : (
                debugLogs.map(log => (
                  <div key={log.id} className="mb-2">
                    <div className={`flex items-start space-x-2 ${
                      log.type === 'error' ? 'text-red-400' :
                      log.type === 'escalation' ? 'text-yellow-400' :
                      log.type === 'complete' ? 'text-green-400' :
                      log.type === 'feedback' ? 'text-purple-400' :
                      'text-gray-300'
                    }`}>
                      <span className="text-gray-500">[{log.timestamp}]</span>
                      <span className="text-cyan-400">{log.agent}:</span>
                      <span className="flex-1">{log.message}</span>
                    </div>
                    {log.data && (
                      <div className="ml-20 mt-1 text-gray-500 text-xs">
                        {log.data.findings && (
                          <div>
                            Findings: {log.data.findings.length} issues detected
                          </div>
                        )}
                        {log.data.confidence && (
                          <div>
                            Confidence: {(log.data.confidence * 100).toFixed(1)}%
                          </div>
                        )}
                        {log.data.rating && (
                          <div>
                            Rating: {log.data.rating}/5 stars • Agents: {log.data.agentsUsed?.length || 0} • Mode: CrewAI
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Feedback Modal */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
            {!feedbackSubmitted ? (
              <>
                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    How was your experience?
                  </h3>
                  <p className="text-gray-600 text-sm">
                    Your feedback helps us improve our agent performance
                  </p>
                </div>

                {/* Star Rating */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Overall Satisfaction
                  </label>
                  <div className="flex justify-center space-x-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        onClick={() => setFeedbackRating(star)}
                        className={`text-2xl transition-colors ${
                          star <= feedbackRating 
                            ? 'text-yellow-400 hover:text-yellow-500' 
                            : 'text-gray-300 hover:text-gray-400'
                        }`}
                      >
                        ★
                      </button>
                    ))}
                  </div>
                  <div className="text-center mt-2">
                    <span className="text-sm text-gray-500">
                      {feedbackRating === 0 && 'Click to rate'}
                      {feedbackRating === 1 && 'Poor'}
                      {feedbackRating === 2 && 'Fair'}
                      {feedbackRating === 3 && 'Good'}
                      {feedbackRating === 4 && 'Very Good'}
                      {feedbackRating === 5 && 'Excellent'}
                    </span>
                  </div>
                </div>

                {/* Comment */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Additional Comments (Optional)
                  </label>
                  <textarea
                    value={feedbackComment}
                    onChange={(e) => setFeedbackComment(e.target.value)}
                    placeholder="Tell us what worked well or what could be improved..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 resize-none"
                    rows={3}
                  />
                </div>

                {/* Buttons */}
                <div className="flex space-x-3">
                  <button
                    onClick={skipFeedback}
                    className="flex-1 px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Skip
                  </button>
                  <button
                    onClick={submitFeedback}
                    disabled={feedbackRating === 0}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Submit Feedback
                  </button>
                </div>
              </>
            ) : (
              /* Thank You Message */
              <div className="text-center py-6">
                <div className="text-green-600 mb-4">
                  <CheckCircle className="w-16 h-16 mx-auto" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Thank You!
                </h3>
                <p className="text-gray-600">
                  Your feedback helps us improve our AI agents and customer service.
                </p>
                <div className="mt-4 text-sm text-gray-500">
                  Resetting conversation...
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiAgentDemo;