/**
 * Individual chat message component
 */

import React from 'react';
import { ChatMessage as ChatMessageType } from '../../services/chatApi';
import styles from './styles.module.css';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = !message.answer;

  return (
    <div className={`${styles.message} ${isUser ? styles.userMessage : styles.assistantMessage}`}>
      <div className={styles.messageHeader}>
        <span className={styles.messageRole}>
          {isUser ? 'You' : 'Assistant'}
        </span>
        <span className={styles.messageTime}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
      </div>

      <div className={styles.messageContent}>
        {isUser ? message.question : message.answer}
      </div>

      {!isUser && message.sources && message.sources.length > 0 && (
        <div className={styles.sources}>
          <div className={styles.sourcesHeader}>Sources:</div>
          {message.sources.map((source, idx) => (
            <div key={source.chunk_id} className={styles.source}>
              <span className={styles.sourceTitle}>
                {source.chapter_title}
                {source.section_title && ` - ${source.section_title}`}
              </span>
              <span className={styles.sourceScore}>
                (relevance: {(source.score * 100).toFixed(0)}%)
              </span>
            </div>
          ))}
        </div>
      )}

      {!isUser && message.retrieval_mode === 'selected' && (
        <div className={styles.modeIndicator}>
          📌 Answer based on selected text
        </div>
      )}
    </div>
  );
};
