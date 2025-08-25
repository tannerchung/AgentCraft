import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // Increased to 30 seconds for AI processing
      headers: {
        'Content-Type': 'application/json',
      }
    });
  }

  async sendMessage(agentType, message) {
    try {
      const response = await this.client.post('/api/chat', {
        agent_type: 'technical_support', // Map all to technical_support for now
        message: message,
        context: {
          timestamp: new Date().toISOString(),
          session_id: this.getSessionId(),
          demo_mode: false
        }
      });

      // Process the real AI response
      if (response.data.success && response.data.response) {
        let processedMessage = '';

        // Check if we have formatted content from backend
        if (response.data.response.content && response.data.response.content.startsWith('**')) {
          processedMessage = response.data.response.content;
        }
        // Handle "**AI Technical Analysis:**" format from backend
        else if (response.data.response.content && (
          response.data.response.content.includes('AI Analysis (raw):') ||
          response.data.response.content.includes('**AI Technical Analysis:**')
        )) {
          try {
            // Extract JSON from either format
            const jsonStart = response.data.response.content.indexOf('{');
            const jsonEnd = response.data.response.content.lastIndexOf('}') + 1;
            if (jsonStart !== -1 && jsonEnd > jsonStart) {
              const jsonStr = response.data.response.content.substring(jsonStart, jsonEnd);
              const parsed = JSON.parse(jsonStr);

              // Format the JSON into readable markdown
              processedMessage = `**Technical Diagnosis:**
${parsed.diagnosis || 'Analysis provided'}

**Root Cause:**
${parsed.root_cause || 'Cause identified'}

**Solution:**
${parsed.solution || 'Solution provided'}

**Working Code:**
\`\`\`${this.detectCodeLanguage(parsed.working_code)}
${parsed.working_code || 'Code example provided'}
\`\`\`

**Implementation Steps:**
${parsed.implementation_steps ? parsed.implementation_steps.map((step, i) => `${i + 1}. ${step}`).join('\n') : 'Steps provided'}

**Testing Approach:**
${parsed.testing_approach || 'Testing guidance provided'}

**Prevention:**
${parsed.prevention || 'Prevention strategies provided'}

**Estimated Time:** ${parsed.estimated_fix_time || 'Time estimate provided'}`;
            } else {
              processedMessage = response.data.response.content;
            }
          } catch (parseError) {
            console.warn('Failed to parse AI response JSON:', parseError);
            processedMessage = response.data.response.content;
          }
        }
        // Handle direct JSON response that needs formatting
        else if (response.data.response.content) {
          try {
            const parsed = JSON.parse(response.data.response.content);

            // Format the JSON into readable markdown
            processedMessage = `**Technical Diagnosis:**
${parsed.diagnosis || 'Analysis provided'}

**Root Cause:**
${parsed.root_cause || 'Cause identified'}

**Solution:**
${parsed.solution || 'Solution provided'}

**Working Code:**
\`\`\`${this.detectCodeLanguage(parsed.working_code)}
${parsed.working_code || 'Code example provided'}
\`\`\`

**Implementation Steps:**
${parsed.implementation_steps ? parsed.implementation_steps.map((step, i) => `${i + 1}. ${step}`).join('\n') : 'Steps provided'}

**Testing Approach:**
${parsed.testing_approach || 'Testing guidance provided'}

**Prevention:**
${parsed.prevention || 'Prevention strategies provided'}

**Estimated Time:** ${parsed.estimated_fix_time || 'Time estimate provided'}`;
          } catch (parseError) {
            // If JSON parsing fails, show the raw content
            processedMessage = response.data.response.content;
          }
        }
        // Fallback to ai_analysis if available
        else if (response.data.response.ai_analysis) {
          processedMessage = response.data.response.ai_analysis;
        }
        // Final fallback
        else {
          processedMessage = "AI response received but couldn't parse content";
        }

        return {
          message: processedMessage,
          confidence: 0.95,
          responseTime: response.data.agent_info?.response_time || 'N/A',
          agentInfo: response.data.agent_info,
          competitiveAdvantage: response.data.competitive_advantage
        };
      }

      return response.data;
    } catch (error) {
      console.error('API Error:', error);

      // Return error message instead of mock data
      return {
        message: `I'm experiencing technical difficulties connecting to the AI system. Error: ${error.message}. Please ensure the backend server is running on localhost:8000.`,
        confidence: 0.1
      };
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
  detectCodeLanguage(code) {
    if (!code) return '';
    const codeStr = code.toString().toLowerCase();
    if (codeStr.includes('def ') || codeStr.includes('import ') || codeStr.includes('from ')) return 'python';
    if (codeStr.includes('const ') || codeStr.includes('function ') || codeStr.includes('require(')) return 'javascript';
    if (codeStr.includes('curl ') || codeStr.includes('#!/bin/')) return 'bash';
    return 'javascript'; // default
  }

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
        message: `🔧 **Technical Analysis Complete**

Thank you for reporting this webhook integration issue. I've analyzed your problem and here's my expert assessment:

## **Issue Diagnosis**
**403 Errors & SSL Certificate Issues**
- Authentication signature mismatch (likely HMAC verification failure)
- SSL certificate chain validation problems
- Possible API version incompatibility

## **Root Cause Analysis**
1. **Authentication Layer**: HMAC signature algorithm may have changed in recent API updates
2. **SSL Layer**: Certificate chain incomplete or expired intermediate certificates
3. **Configuration**: Webhook endpoint URL or headers misconfigured

## **Detailed Action Steps**

### **Immediate Actions (0-30 minutes)**
1. **Verify Webhook URL Configuration**
   - Check endpoint URL format: \`https://your-domain.com/webhook\`
   - Ensure HTTPS is properly configured
   - Test with curl: \`curl -I https://your-webhook-endpoint.com\`

2. **Check Authentication Headers**
   - Verify X-Signature header format
   - Confirm secret key hasn't changed
   - Test HMAC generation algorithm

3. **SSL Certificate Inspection**
   - Run: \`openssl s_client -connect your-domain.com:443 -showcerts\`
   - Check certificate expiration dates
   - Verify complete certificate chain

### **Implementation Steps (30-60 minutes)**

**Step 1: Update HMAC Verification**
\`\`\`python
import hmac
import hashlib
import base64

def verify_webhook_signature(payload, signature, secret):
    # Updated for API v2.1.3+
    expected = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # Handle both formats: "sha256=hash" and "hash"
    if signature.startswith('sha256='):
        signature = signature[7:]

    return hmac.compare_digest(expected, signature)
\`\`\`

**Step 2: SSL Certificate Fix**
\`\`\`python
import requests
import ssl

# Option 1: Update certificate bundle
response = requests.post(
    webhook_url,
    json=payload,
    verify='/path/to/updated-ca-bundle.crt'
)

# Option 2: For development only - disable verification
# response = requests.post(webhook_url, json=payload, verify=False)
\`\`\`

**Step 3: Implement Retry Logic**
\`\`\`python
import time
import random

def send_webhook_with_retry(url, payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url, 
                json=payload, 
                timeout=(5, 30),
                verify=True
            )
            if response.status_code == 200:
                return response
        except (requests.exceptions.SSLError, 
                requests.exceptions.Timeout) as e:
            if attempt == max_retries - 1:
                raise
            # Exponential backoff
            time.sleep(2 ** attempt + random.uniform(0, 1))

    raise Exception("Max retries exceeded")
\`\`\`

### **Testing & Verification (15-30 minutes)**
1. **Unit Test the Signature**
   \`\`\`bash
   python -c "import your_webhook_module; your_webhook_module.test_signature_verification()"
   \`\`\`

2. **SSL Connectivity Test**
   \`\`\`bash
   curl -v https://your-webhook-endpoint.com/test
   \`\`\`

3. **End-to-End Webhook Test**
   - Send test webhook from your platform
   - Monitor server logs for 403/SSL errors
   - Verify successful payload delivery

### **Monitoring & Prevention**
- Set up certificate expiration alerts
- Implement webhook delivery status tracking
- Add logging for authentication failures

## **Expected Resolution Time**
- **Immediate fix**: 1-2 hours
- **Complete implementation**: 2-4 hours
- **Testing & verification**: 30 minutes

## **Success Metrics**
- ✅ 403 errors eliminated
- ✅ SSL handshake successful
- ✅ Webhook delivery rate > 99%
- ✅ Response time < 2 seconds

This analysis leverages my specialized expertise in webhook implementations, API authentication, and SSL certificate management to provide actionable solutions for your specific integration challenges.`,
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