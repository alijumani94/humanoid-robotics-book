/**
 * Main ChatWidget component
 */

import React, { useState, useEffect } from 'react';
import { ChatHistory } from './ChatHistory';
import { ChatInput } from './ChatInput';
import { useChat } from './hooks/useChat';
import styles from './styles.module.css';

export const ChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedText, setSelectedText] = useState<string | null>(null);

  const { messages, loading, error, sendMessage, clearError, clearMessages } = useChat();

  useEffect(() => {
    // Listen for text selection
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();

      if (text && text.length > 0 && text.length < 5000) {
        setSelectedText(text);
        setIsOpen(true);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('touchend', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('touchend', handleSelection);
    };
  }, []);

  const handleSend = async (message: string) => {
    await sendMessage(message, selectedText || undefined);

    // Clear selected text after sending
    if (selectedText) {
      setSelectedText(null);
    }
  };

  const handleClearSelection = () => {
    setSelectedText(null);
  };

  const toggleWidget = () => {
    setIsOpen(!isOpen);
    clearError();
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        className={styles.toggleButton}
        onClick={toggleWidget}
        aria-label="Toggle chat widget"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat Widget */}
      {isOpen && (
        <div className={styles.widget}>
          {/* Header */}
          <div className={styles.header}>
            <div className={styles.headerTitle}>
              <span className={styles.headerIcon}>🤖</span>
              <span>Robotics Book Assistant</span>
            </div>

            <div className={styles.headerActions}>
              {messages.length > 0 && (
                <button
                  className={styles.clearButton}
                  onClick={clearMessages}
                  title="Clear chat"
                >
                  🗑️
                </button>
              )}
              <button
                className={styles.closeButton}
                onClick={toggleWidget}
                aria-label="Close chat"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Error Banner */}
          {error && (
            <div className={styles.errorBanner}>
              <span>{error}</span>
              <button onClick={clearError} className={styles.errorClose}>
                ✕
              </button>
            </div>
          )}

          {/* Selected Text Banner */}
          {selectedText && (
            <div className={styles.selectedBanner}>
              <span>📌 Selected text mode active</span>
              <button onClick={handleClearSelection} className={styles.clearSelectionButton}>
                Clear
              </button>
            </div>
          )}

          {/* Messages */}
          <div className={styles.body}>
            <ChatHistory messages={messages} loading={loading} />
          </div>

          {/* Input */}
          <div className={styles.footer}>
            <ChatInput
              onSend={handleSend}
              disabled={loading}
              selectedText={selectedText || undefined}
            />
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;
