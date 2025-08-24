
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export const useAgentChat = (agentType) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [agentStatus, setAgentStatus] = useState({
    confidence: 94,
    avgResponseTime: 1.2,
    isOnline: true
  });

  useEffect(() => {
    // Reset messages when agent changes
    setMessages([]);
    
    // Update agent status with slight variations
    setAgentStatus(prev => ({
      ...prev,
      confidence: Math.floor(Math.random() * 10) + 90,
      avgResponseTime: Math.random() * 0.5 + 1.0
    }));
  }, [agentType]);

  const sendMessage = async (content) => {
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
      
      const response = await apiService.sendMessage(agentType, content);
      
      const agentMessage = {
        id: Date.now() + 1,
        sender: 'agent',
        content: response.message,
        timestamp: new Date().toISOString(),
        confidence: response.confidence
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Fallback response
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'agent',
        content: "I apologize, but I'm experiencing some technical difficulties. This would normally connect to our specialized agent system for real-time responses.",
        timestamp: new Date().toISOString(),
        confidence: 0.5
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    sendMessage,
    isLoading,
    agentStatus
  };
};
