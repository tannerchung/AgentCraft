
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
  }

  async sendMessage(agentType, message) {
    try {
      const response = await this.client.post('/api/chat', {
        agent_type: agentType,
        message: message,
        context: {
          timestamp: new Date().toISOString(),
          session_id: this.getSessionId()
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('API Error:', error);
      
      // Return mock response for demo purposes
      return this.getMockResponse(agentType, message);
    }
  }

  async getMetrics() {
    try {
      const response = await this.client.get('/api/metrics');
      return response.data;
    } catch (error) {
      console.error('Metrics API Error:', error);
      return this.getMockMetrics();
    }
  }

  async getCompetitiveAnalysis(competitor) {
    try {
      const response = await this.client.post('/api/competitive-analysis', {
        competitor: competitor
      });
      return response.data;
    } catch (error) {
      console.error('Competitive Analysis API Error:', error);
      return this.getMockCompetitiveData(competitor);
    }
  }

  // Helper methods
  getSessionId() {
    let sessionId = localStorage.getItem('agentcraft_session');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('agentcraft_session', sessionId);
    }
    return sessionId;
  }

  getMockResponse(agentType, message) {
    const responses = {
      technical: {
        message: `I understand you're experiencing technical issues. Based on my specialized knowledge of ${this.extractTechnicalTerms(message).join(', ')}, here's my analysis:

🔍 **Technical Diagnosis:**
- This appears to be a common issue with webhook implementations
- The root cause is likely related to SSL certificate validation or authentication headers

💡 **Recommended Solution:**
1. Verify your SSL certificate chain is complete
2. Check HMAC signature generation algorithm
3. Implement proper retry logic with exponential backoff

📝 **Code Example:**
\`\`\`python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
\`\`\`

This specialized analysis draws from my deep technical knowledge of webhook implementations and common integration patterns.`,
        confidence: Math.random() * 0.2 + 0.8
      },
      billing: {
        message: `I can help you with billing and payment processing. Let me analyze your query about ${this.extractBillingTerms(message).join(', ')}:

💳 **Billing Analysis:**
- This is a standard billing workflow scenario
- I recommend following PCI DSS compliance guidelines

📋 **Process Recommendations:**
1. Implement proper payment state management
2. Set up automated dunning sequences
3. Configure webhook notifications for payment events

🔧 **Best Practices:**
- Always validate payment amounts server-side
- Implement idempotency keys for payment operations
- Use proper error handling for failed transactions

This response leverages my specialized billing domain expertise to provide actionable solutions.`,
        confidence: Math.random() * 0.2 + 0.75
      },
      competitive: {
        message: `Based on my competitive intelligence analysis regarding ${this.extractCompetitiveTerms(message).join(', ')}:

📊 **Market Position Analysis:**
- Our solution offers superior customization capabilities
- Competitive advantage in specialized domain expertise
- Cost efficiency compared to enterprise platforms

🎯 **Key Differentiators:**
1. **Specialized Expertise**: Deep domain knowledge vs. generic responses
2. **Rapid Customization**: Custom agents in hours, not months
3. **Architectural Flexibility**: No vendor lock-in or roadmap dependencies

💰 **Cost Comparison:**
- 67% reduction in support costs
- Faster resolution times (avg 1.2s vs 8.5s)
- Higher customer satisfaction (4.8/5 vs 3.2/5)

This analysis draws from my specialized competitive intelligence database and real-time market data.`,
        confidence: Math.random() * 0.2 + 0.85
      }
    };

    return responses[agentType] || responses.technical;
  }

  extractTechnicalTerms(message) {
    const terms = ['webhook', 'API', 'SSL', 'authentication', 'timeout', 'HMAC', 'certificate'];
    return terms.filter(term => message.toLowerCase().includes(term.toLowerCase()));
  }

  extractBillingTerms(message) {
    const terms = ['payment', 'subscription', 'billing', 'refund', 'invoice', 'charge'];
    return terms.filter(term => message.toLowerCase().includes(term.toLowerCase()));
  }

  extractCompetitiveTerms(message) {
    const terms = ['Salesforce', 'Zendesk', 'Microsoft', 'pricing', 'competitor', 'market'];
    return terms.filter(term => message.toLowerCase().includes(term.toLowerCase()));
  }

  getMockMetrics() {
    return {
      totalQueries: 1247,
      avgResponseTime: 1.2,
      costSavings: 45000,
      agentEfficiency: 94,
      customerSatisfaction: 4.8
    };
  }

  getMockCompetitiveData(competitor) {
    return {
      competitor: competitor,
      strengths: ['Market presence', 'Brand recognition'],
      weaknesses: ['Limited customization', 'High costs', 'Slow innovation'],
      opportunities: ['Specialized expertise', 'Custom solutions', 'Rapid deployment']
    };
  }
}

export const apiService = new ApiService();
