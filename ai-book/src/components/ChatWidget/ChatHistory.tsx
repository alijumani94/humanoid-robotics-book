/**
 * Chat history/message list component
 */

import React, { useEffect, useRef } from 'react';
import { ChatMessage as ChatMessageType } from '../../services/chatApi';
import { ChatMessage } from './ChatMessage';
import styles from './styles.module.css';

interface ChatHistoryProps {
  messages: ChatMessageType[];
  loading?: boolean;
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({ messages, loading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0 && !loading) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyStateIcon}>💬</div>
        <div className={styles.emptyStateText}>
          Ask a question about the robotics textbook!
        </div>
        <div className={styles.emptyStateHint}>
          You can also select text from the book and ask questions about it.
        </div>
      </div>
    );
  }

  return (
    <div className={styles.history}>
      {messages.map((message, idx) => (
        <ChatMessage key={idx} message={message} />
      ))}

      {loading && (
        <div className={styles.loadingMessage}>
          <div className={styles.loadingDots}>
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span>Thinking...</span>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};
