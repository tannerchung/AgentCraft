# AgentCraft Frontend Architecture

Complete guide to the React frontend architecture of AgentCraft.

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Components](#components)
5. [State Management](#state-management)
6. [Custom Hooks](#custom-hooks)
7. [API Integration](#api-integration)
8. [WebSocket Integration](#websocket-integration)
9. [Styling](#styling)
10. [Performance Optimization](#performance-optimization)

---

## Overview

The AgentCraft frontend is a React-based single-page application (SPA) that provides an interactive interface for:
- Multi-agent conversations
- Agent configuration and management
- Knowledge base management
- Real-time agent status tracking
- Performance analytics and A/B testing

**Key Features:**
- Real-time WebSocket updates
- Component-based architecture
- Responsive design
- Interactive agent selection
- Citation display and source attribution

---

## Technology Stack

### Core Technologies

```json
{
  "runtime": "React 18",
  "language": "JavaScript (ES6+)",
  "styling": "Tailwind CSS",
  "icons": "Lucide React",
  "state_management": "React Hooks (useState, useEffect, useCallback)",
  "http_client": "Fetch API",
  "websocket": "Native WebSocket API",
  "build_tool": "Create React App / Vite"
}
```

### Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "lucide-react": "^0.263.1",
  "tailwindcss": "^3.3.0"
}
```

---

## Project Structure

```
src/
├── App.js                      # Main application component
├── index.js                    # Application entry point
├── index.css                   # Global styles
├── components/                 # React components
│   ├── MultiAgentDemo.js      # Multi-agent chat interface
│   ├── AgentChat.js           # Single agent chat
│   ├── AgentConfiguration.js  # Agent CRUD interface
│   ├── AgentDemo.js           # Agent demonstration
│   ├── KnowledgeBaseManager.js # Knowledge management
│   ├── CompetitiveAnalysis.js # Competitive intelligence
│   ├── QueryAnalyzer.js       # Query analysis dashboard
│   ├── RealPerformanceAnalytics.js # Analytics dashboard
│   └── ABTestingDashboard.js  # A/B testing interface
├── hooks/                      # Custom React hooks
│   └── useAgentChat.js        # Agent chat functionality
├── services/                   # API and service layer
│   └── api.js                 # API client
└── tools/                      # Utility functions
```

---

## Components

### App.js

Main application component with tabbed navigation.

**Features:**
- Tab-based navigation
- Component routing
- Global header
- Live status indicator

**Code Structure:**
```javascript
function App() {
  const [activeTab, setActiveTab] = useState('performance');

  const tabs = [
    { id: 'performance', name: 'Performance Analytics', icon: BarChart3 },
    { id: 'multi-agent', name: 'Agent Chat', icon: MessageSquare },
    { id: 'knowledge', name: 'Knowledge Base', icon: Database },
    { id: 'config', name: 'Agent Configuration', icon: Settings },
    { id: 'ab-testing', name: 'A/B Testing', icon: Zap }
  ];

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'performance': return <RealPerformanceAnalytics />;
      case 'multi-agent': return <MultiAgentDemo />;
      case 'knowledge': return <KnowledgeBaseManager />;
      case 'config': return <AgentConfiguration />;
      case 'ab-testing': return <ABTestingDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Navigation tabs={tabs} activeTab={activeTab} setActiveTab={setActiveTab} />
      <main>{renderActiveComponent()}</main>
    </div>
  );
}
```

### MultiAgentDemo.js

Primary multi-agent conversation interface.

**Features:**
- Agent selection with avatars
- Real-time conversation
- Citation display
- Agent status indicators
- WebSocket integration

**State Management:**
```javascript
const [messages, setMessages] = useState([]);
const [input, setInput] = useState('');
const [selectedAgents, setSelectedAgents] = useState([]);
const [isProcessing, setIsProcessing] = useState(false);
const [agentStatuses, setAgentStatuses] = useState({});
const [sessionId, setSessionId] = useState(generateSessionId());
const [citations, setCitations] = useState([]);
```

**Key Functions:**

**1. Send Message**
```javascript
const handleSendMessage = async () => {
  if (!input.trim()) return;

  const userMessage = {
    id: Date.now(),
    role: 'user',
    content: input,
    timestamp: new Date().toISOString()
  };

  setMessages(prev => [...prev, userMessage]);
  setInput('');
  setIsProcessing(true);

  try {
    const response = await fetch('http://localhost:8000/api/multi-agent/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: input,
        session_id: sessionId,
        context: { selected_agents: selectedAgents }
      })
    });

    const data = await response.json();

    const assistantMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: data.response,
      agents_used: data.agents_used,
      citations: data.citations,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, assistantMessage]);
    setCitations(data.citations || []);
  } catch (error) {
    console.error('Error sending message:', error);
  } finally {
    setIsProcessing(false);
  }
};
```

**2. WebSocket Connection**
```javascript
useEffect(() => {
  const ws = new WebSocket(`ws://localhost:8000/ws/agent-tracking/${sessionId}`);

  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === 'agent_status') {
      setAgentStatuses(prev => ({
        ...prev,
        [message.agent_id]: {
          name: message.agent_name,
          status: message.status,
          progress: message.progress,
          message: message.message
        }
      }));
    }
  };

  return () => ws.close();
}, [sessionId]);
```

**Component Structure:**
```jsx
<div className="multi-agent-demo">
  <AgentSelector
    agents={availableAgents}
    selectedAgents={selectedAgents}
    onAgentSelect={handleAgentSelect}
  />

  <MessageList messages={messages} />

  <AgentStatusPanel statuses={agentStatuses} />

  <CitationList citations={citations} />

  <MessageInput
    value={input}
    onChange={setInput}
    onSend={handleSendMessage}
    disabled={isProcessing}
  />
</div>
```

### AgentChat.js

Single agent conversation interface.

**Features:**
- Focused single-agent interaction
- Agent-specific styling and avatar
- Message history
- Typing indicators

**Usage:**
```javascript
const AgentChat = ({ agentType = 'technical' }) => {
  const { messages, sendMessage, isLoading, agentStatus } = useAgentChat(agentType);

  return (
    <div className="agent-chat">
      <AgentHeader agent={agentType} status={agentStatus} />
      <MessageThread messages={messages} />
      {isLoading && <TypingIndicator />}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
};
```

### AgentConfiguration.js

Agent management and configuration interface.

**Features:**
- Agent CRUD operations
- Form validation
- Real-time agent status
- Bulk operations

**State:**
```javascript
const [agents, setAgents] = useState([]);
const [editingAgent, setEditingAgent] = useState(null);
const [isCreating, setIsCreating] = useState(false);
const [formData, setFormData] = useState({
  name: '',
  role: '',
  domain: 'custom',
  backstory: '',
  goal: '',
  keywords: [],
  avatar: '🤖',
  color: 'blue',
  llm_config: { model: 'claude-3-5-sonnet', temperature: 0.2 }
});
```

**CRUD Functions:**

**Create Agent:**
```javascript
const handleCreateAgent = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/agents/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    });

    const data = await response.json();

    if (data.success) {
      setAgents(prev => [...prev, data.agent]);
      setIsCreating(false);
      resetForm();
    }
  } catch (error) {
    console.error('Error creating agent:', error);
  }
};
```

**Update Agent:**
```javascript
const handleUpdateAgent = async (agentId, updates) => {
  try {
    const response = await fetch(`http://localhost:8000/api/agents/${agentId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });

    const data = await response.json();

    if (data.success) {
      setAgents(prev => prev.map(a =>
        a.id === agentId ? { ...a, ...updates } : a
      ));
    }
  } catch (error) {
    console.error('Error updating agent:', error);
  }
};
```

**Delete Agent:**
```javascript
const handleDeleteAgent = async (agentId) => {
  if (!confirm('Are you sure you want to delete this agent?')) return;

  try {
    const response = await fetch(`http://localhost:8000/api/agents/${agentId}`, {
      method: 'DELETE'
    });

    const data = await response.json();

    if (data.success) {
      setAgents(prev => prev.filter(a => a.id !== agentId));
    }
  } catch (error) {
    console.error('Error deleting agent:', error);
  }
};
```

### KnowledgeBaseManager.js

Knowledge base and URL management interface.

**Features:**
- Company management
- URL crawl configuration
- Firecrawl job monitoring
- Qdrant collection stats
- Search testing

**State:**
```javascript
const [companies, setCompanies] = useState([]);
const [currentCompany, setCurrentCompany] = useState('');
const [crawlUrls, setCrawlUrls] = useState([]);
const [newUrl, setNewUrl] = useState('');
const [crawlJobs, setCrawlJobs] = useState([]);
const [searchQuery, setSearchQuery] = useState('');
const [searchResults, setSearchResults] = useState([]);
```

**Key Functions:**

**Add Crawl URL:**
```javascript
const handleAddUrl = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/knowledge/urls', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_name: currentCompany,
        url: newUrl
      })
    });

    const data = await response.json();

    if (data.success) {
      setCrawlUrls(prev => [...prev, { url: newUrl, id: data.url_id }]);
      setNewUrl('');
    }
  } catch (error) {
    console.error('Error adding URL:', error);
  }
};
```

**Trigger Crawl:**
```javascript
const handleTriggerCrawl = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/knowledge/crawl', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        company_name: currentCompany,
        max_pages: 50
      })
    });

    const data = await response.json();

    if (data.success) {
      setCrawlJobs(prev => [...prev, {
        id: data.job_id,
        status: 'started',
        company: currentCompany
      }]);

      // Poll for status
      pollCrawlStatus(data.job_id);
    }
  } catch (error) {
    console.error('Error triggering crawl:', error);
  }
};
```

**Search Knowledge:**
```javascript
const handleSearch = async () => {
  try {
    const response = await fetch(
      `http://localhost:8000/api/knowledge/search?q=${encodeURIComponent(searchQuery)}&limit=10`
    );

    const data = await response.json();

    if (data.success) {
      setSearchResults(data.results);
    }
  } catch (error) {
    console.error('Error searching:', error);
  }
};
```

### RealPerformanceAnalytics.js

Performance analytics and metrics dashboard.

**Features:**
- Real-time metrics
- Performance charts
- Agent performance breakdown
- System health indicators

**Metrics Displayed:**
- Total queries processed
- Average response time
- Success rate
- User satisfaction
- Cost per query
- Agent utilization

### CompetitiveAnalysis.js

Competitive intelligence dashboard.

**Features:**
- Competitor analysis queries
- Market positioning
- Cost comparison
- Strategic recommendations

---

## State Management

AgentCraft uses React Hooks for state management without external libraries like Redux.

### Local Component State

```javascript
const [state, setState] = useState(initialValue);
```

**Example:**
```javascript
const [messages, setMessages] = useState([]);
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);
```

### Computed State with useMemo

```javascript
const filteredAgents = useMemo(() => {
  return agents.filter(agent =>
    agent.domain === selectedDomain
  );
}, [agents, selectedDomain]);
```

### Effect Management

```javascript
useEffect(() => {
  // Setup
  const subscription = subscribeToUpdates();

  // Cleanup
  return () => subscription.unsubscribe();
}, [dependencies]);
```

### State Update Patterns

**Immutable Updates:**
```javascript
// Array append
setMessages(prev => [...prev, newMessage]);

// Array filter
setAgents(prev => prev.filter(a => a.id !== deleteId));

// Array map
setAgents(prev => prev.map(a =>
  a.id === updateId ? { ...a, ...updates } : a
));

// Object spread
setFormData(prev => ({ ...prev, name: newName }));
```

---

## Custom Hooks

### useAgentChat

Reusable hook for agent chat functionality.

**Location:** `src/hooks/useAgentChat.js`

**Usage:**
```javascript
const { messages, sendMessage, isLoading, agentStatus } = useAgentChat('technical');
```

**Implementation:**
```javascript
export const useAgentChat = (agentType) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatus, setAgentStatus] = useState({
    confidence: 94,
    avgResponseTime: 1.2,
    isOnline: true
  });

  useEffect(() => {
    // Reset on agent change
    setMessages([]);
  }, [agentType]);

  const sendMessage = async (content) => {
    setIsLoading(true);

    try {
      const response = await apiService.sendMessage(agentType, content);

      setMessages(prev => [...prev, {
        role: 'user',
        content
      }, {
        role: 'agent',
        content: response.message,
        confidence: response.confidence
      }]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, sendMessage, isLoading, agentStatus };
};
```

### Custom Hooks Best Practices

1. **Naming:** Always prefix with `use`
2. **Separation of Concerns:** One hook per logical feature
3. **Dependencies:** Properly list all dependencies
4. **Cleanup:** Return cleanup functions
5. **Error Handling:** Handle errors gracefully

---

## API Integration

### API Service Layer

**Location:** `src/services/api.js`

**Base Configuration:**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor(baseURL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Agent methods
  async getAgents() {
    return this.request('/api/agents/list');
  }

  async createAgent(agentData) {
    return this.request('/api/agents/create', {
      method: 'POST',
      body: JSON.stringify(agentData)
    });
  }

  async updateAgent(agentId, updates) {
    return this.request(`/api/agents/${agentId}`, {
      method: 'PUT',
      body: JSON.stringify(updates)
    });
  }

  async deleteAgent(agentId) {
    return this.request(`/api/agents/${agentId}`, {
      method: 'DELETE'
    });
  }

  // Query methods
  async processQuery(query, context = {}) {
    return this.request('/api/multi-agent/query', {
      method: 'POST',
      body: JSON.stringify({ query, context })
    });
  }

  // Knowledge methods
  async searchKnowledge(query, limit = 10) {
    return this.request(`/api/knowledge/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  }

  async addCrawlUrl(companyName, url) {
    return this.request('/api/knowledge/urls', {
      method: 'POST',
      body: JSON.stringify({ company_name: companyName, url })
    });
  }

  async triggerCrawl(companyName, maxPages = 50) {
    return this.request('/api/knowledge/crawl', {
      method: 'POST',
      body: JSON.stringify({ company_name: companyName, max_pages: maxPages })
    });
  }

  // Feedback methods
  async submitFeedback(sessionId, rating, comment = '') {
    return this.request('/api/agents/feedback', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, rating, comment })
    });
  }
}

export const apiService = new ApiService(API_BASE_URL);
```

### Error Handling

```javascript
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    console.error('API Error:', error.response.data);
    return error.response.data.detail || 'Server error';
  } else if (error.request) {
    // Request made but no response
    console.error('Network Error:', error.request);
    return 'Network error - please check your connection';
  } else {
    // Something else happened
    console.error('Error:', error.message);
    return 'An unexpected error occurred';
  }
};
```

---

## WebSocket Integration

### WebSocket Connection Management

```javascript
class WebSocketManager {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.messageHandlers = new Map();
  }

  connect(clientId) {
    this.ws = new WebSocket(`${this.url}/${clientId}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.attemptReconnect(clientId);
    };
  }

  handleMessage(message) {
    const handlers = this.messageHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => handler(message));
    }
  }

  on(messageType, handler) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, []);
    }
    this.messageHandlers.get(messageType).push(handler);
  }

  off(messageType, handler) {
    const handlers = this.messageHandlers.get(messageType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  attemptReconnect(clientId) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

      setTimeout(() => {
        this.connect(clientId);
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsManager = new WebSocketManager('ws://localhost:8000/ws/agent-tracking');
```

### Using WebSocket in Components

```javascript
useEffect(() => {
  const sessionId = generateSessionId();

  wsManager.connect(sessionId);

  wsManager.on('agent_status', (message) => {
    setAgentStatuses(prev => ({
      ...prev,
      [message.agent_id]: {
        name: message.agent_name,
        status: message.status,
        progress: message.progress,
        message: message.message
      }
    }));
  });

  wsManager.on('agent_collaboration', (message) => {
    console.log('Collaboration:', message);
  });

  return () => {
    wsManager.disconnect();
  };
}, []);
```

---

## Styling

### Tailwind CSS Configuration

**File:** `tailwind.config.js`

```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'salesforce-blue': '#0176D3',
        'agentforce-purple': '#7B68EE'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
```

### Global Styles

**File:** `src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom gradient background */
.gradient-bg {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Message bubble styles */
.message-user {
  @apply bg-blue-500 text-white rounded-lg p-3 max-w-md ml-auto;
}

.message-agent {
  @apply bg-gray-100 text-gray-900 rounded-lg p-3 max-w-md mr-auto;
}

/* Agent avatar styles */
.agent-avatar {
  @apply w-10 h-10 rounded-full flex items-center justify-center text-2xl;
}

/* Status indicator */
.status-online {
  @apply w-3 h-3 bg-green-400 rounded-full animate-pulse;
}

.status-offline {
  @apply w-3 h-3 bg-gray-400 rounded-full;
}
```

### Component-Level Styling

**Inline Tailwind Classes:**
```jsx
<div className="container mx-auto px-4 py-8">
  <h1 className="text-3xl font-bold text-gray-900 mb-6">
    Agent Configuration
  </h1>

  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {agents.map(agent => (
      <AgentCard key={agent.id} agent={agent} />
    ))}
  </div>
</div>
```

---

## Performance Optimization

### Memoization

**React.memo for Components:**
```javascript
const AgentCard = React.memo(({ agent, onSelect }) => {
  return (
    <div onClick={() => onSelect(agent.id)}>
      <h3>{agent.name}</h3>
      <p>{agent.role}</p>
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.agent.id === nextProps.agent.id;
});
```

**useMemo for Expensive Calculations:**
```javascript
const sortedAgents = useMemo(() => {
  return agents.sort((a, b) =>
    b.specialization_score - a.specialization_score
  );
}, [agents]);
```

**useCallback for Function References:**
```javascript
const handleAgentSelect = useCallback((agentId) => {
  setSelectedAgents(prev => [...prev, agentId]);
}, []);
```

### Code Splitting

```javascript
import { lazy, Suspense } from 'react';

const MultiAgentDemo = lazy(() => import('./components/MultiAgentDemo'));
const AgentConfiguration = lazy(() => import('./components/AgentConfiguration'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <MultiAgentDemo />
    </Suspense>
  );
}
```

### Virtual Scrolling for Long Lists

```javascript
const MessageList = ({ messages }) => {
  const listRef = useRef(null);

  useEffect(() => {
    // Scroll to bottom on new message
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div ref={listRef} className="overflow-y-auto max-h-96">
      {messages.slice(-100).map(message => (
        <MessageBubble key={message.id} message={message} />
      ))}
    </div>
  );
};
```

---

## Development Workflow

### Running the Application

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Environment Variables

Create `.env` file:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Building for Production

```bash
npm run build
```

Output: `build/` directory with optimized static files

---

## Best Practices

1. **Component Organization:**
   - One component per file
   - Keep components focused and small
   - Extract reusable logic to hooks

2. **State Management:**
   - Keep state as local as possible
   - Lift state only when necessary
   - Use context for deeply nested props

3. **Performance:**
   - Memoize expensive calculations
   - Use React.memo for pure components
   - Implement virtual scrolling for long lists

4. **Error Handling:**
   - Always handle API errors
   - Show user-friendly error messages
   - Implement error boundaries

5. **Accessibility:**
   - Use semantic HTML
   - Include ARIA labels
   - Ensure keyboard navigation

6. **Code Quality:**
   - Use ESLint for linting
   - Follow consistent naming conventions
   - Write meaningful comments

---

For more information, see:
- [API.md](API.md) - API documentation
- [WEBSOCKET.md](WEBSOCKET.md) - WebSocket protocol
- [agents.md](agents.md) - Agent system architecture
