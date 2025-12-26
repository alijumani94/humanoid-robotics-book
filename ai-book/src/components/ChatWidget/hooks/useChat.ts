/**
 * Custom hook for managing chat state
 */

import { useState, useCallback } from 'react';
import { chatApi, ChatMessage, ChatResponse } from '../../../services/chatApi';

interface UseChatReturn {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  sendMessage: (question: string, selectedText?: string) => Promise<void>;
  clearError: () => void;
  clearMessages: () => void;
}

export const useChat = (): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (question: string, selectedText?: string) => {
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage: ChatMessage = {
      question,
      answer: '',
      timestamp: new Date().toISOString(),
      retrieval_mode: selectedText ? 'selected' : 'default',
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response: ChatResponse = await chatApi.sendMessage(question, selectedText);

      // Add assistant response
      const assistantMessage: ChatMessage = {
        question,
        answer: response.answer,
        sources: response.sources,
        timestamp: response.timestamp,
        retrieval_mode: response.retrieval_mode,
      };

      setMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = assistantMessage;
        return newMessages;
      });

    } catch (err: any) {
      setError(err.message || 'Failed to send message. Please try again.');

      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    loading,
    error,
    sendMessage,
    clearError,
    clearMessages,
  };
};
