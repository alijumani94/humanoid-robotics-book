/**
 * API client for chat backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export interface ChatMessage {
  question: string;
  answer: string;
  sources?: ChunkReference[];
  timestamp: string;
  retrieval_mode: string;
}

export interface ChunkReference {
  chunk_id: string;
  chapter_title: string;
  section_title?: string;
  score: number;
  text_preview: string;
}

export interface ChatRequest {
  question: string;
  selected_text?: string;
  user_id?: string;
}

export interface ChatResponse {
  chat_id: string;
  answer: string;
  sources: ChunkReference[];
  retrieval_mode: string;
  timestamp: string;
}

export const chatApi = {
  /**
   * Send a message to the chatbot
   */
  async sendMessage(question: string, selectedText?: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        selected_text: selectedText,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }

    return response.json();
  },

  /**
   * Get chat history for a user
   */
  async getHistory(userId: string, limit: number = 10): Promise<ChatMessage[]> {
    const response = await fetch(
      `${API_BASE_URL}/chat/history?user_id=${userId}&limit=${limit}`
    );

    if (!response.ok) {
      throw new Error('Failed to fetch history');
    }

    const data = await response.json();
    return data.history;
  },

  /**
   * Submit feedback for a chat response
   */
  async submitFeedback(chatId: string, rating: number, comment?: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        chat_id: chatId,
        rating,
        comment,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to submit feedback');
    }
  },

  /**
   * Check API health
   */
  async checkHealth(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },
};
