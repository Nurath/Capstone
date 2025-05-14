import React from 'react';
import ChatLayout from './components/layout/ChatLayout';
import { ThemeProvider } from './contexts/ThemeContext';
import { ChatProvider } from './contexts/ChatContext';

function App() {
  return (
    <ThemeProvider>
      <ChatProvider>
        <ChatLayout />
      </ChatProvider>
    </ThemeProvider>
  );
}

export default App;