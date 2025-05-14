import React, { useEffect, useRef } from 'react';
import { Bot } from 'lucide-react';
import MessageItem from './MessageItem';
import { useChat } from '../../contexts/ChatContext';

const ChatWindow: React.FC = () => {
  const { messages, isLoading, chatDocuments } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-center p-8">
          <Bot className="h-12 w-12 text-primary-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Welcome to AI Chat Assistant
          </h2>
          <p className="text-gray-500 dark:text-gray-400 max-w-md">
            Ask me anything! I can search the web, analyze data, display charts, and show images.
          </p>
        </div>
      ) : (
        <>
          {chatDocuments.length > 0 && (
            <div className="mb-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <strong className="text-gray-700 dark:text-gray-300">Uploaded Files:</strong>
              <ul className="mt-2 space-y-1">
                {chatDocuments.map(doc => (
                  <li key={doc.doc_id} className="text-sm">
                    <span className="text-gray-600 dark:text-gray-400">{doc.filename}:</span>
                    <span className="ml-2 text-xs text-gray-500 dark:text-gray-500">{doc.file_path}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="flex items-start gap-3 animate-fade-in">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div className="p-3 max-w-[80%] bg-gray-100 dark:bg-gray-700 rounded-lg">
                <div className="flex space-x-2">
                  <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '200ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce" style={{ animationDelay: '400ms' }}></div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default ChatWindow;