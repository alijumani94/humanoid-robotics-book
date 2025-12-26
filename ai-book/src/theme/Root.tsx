/**
 * Root theme wrapper to include ChatWidget globally
 */

import React from 'react';
import ChatWidget from '../components/ChatWidget';

export default function Root({ children }) {
  return (
    <>
      {children}
      <ChatWidget />
    </>
  );
}
