/**
 * Chat input component
 */

import React, { useState, KeyboardEvent } from 'react';
import styles from './styles.module.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  selectedText?: string;
}

const MAX_LENGTH = 500;

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  selectedText,
}) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const remainingChars = MAX_LENGTH - input.length;

  return (
    <div className={styles.inputContainer}>
      {selectedText && (
        <div className={styles.selectedTextIndicator}>
          📌 Question will be answered from selected text
          <span className={styles.selectedTextPreview}>
            "{selectedText.substring(0, 100)}..."
          </span>
        </div>
      )}

      <div className={styles.inputWrapper}>
        <textarea
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about the book..."
          disabled={disabled}
          maxLength={MAX_LENGTH}
          rows={2}
        />

        <div className={styles.inputFooter}>
          <span className={`${styles.charCounter} ${remainingChars < 50 ? styles.warning : ''}`}>
            {remainingChars} characters remaining
          </span>

          <button
            className={styles.sendButton}
            onClick={handleSend}
            disabled={disabled || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};
