import React, { useState, useRef, useEffect } from 'react';
import { Send, Image, Search, BarChart3, X, FileText, FileSpreadsheet } from 'lucide-react';
import { useChat } from '../../contexts/ChatContext';

const InputPanel: React.FC = () => {
  const [message, setMessage] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const { sendMessage, isLoading, uploadFile } = useChat();
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const csvInputRef = useRef<HTMLInputElement>(null);
  
  // Auto-resize textarea based on content
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      sendMessage(message);
      setMessage('');
      
      // Reset textarea height
      if (inputRef.current) {
        inputRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadFile(file);
    }
    // Reset the input value so the same file can be uploaded again if needed
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (csvInputRef.current) {
      csvInputRef.current.value = '';
    }
  };

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 p-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className={`relative flex items-end rounded-lg border ${
          isFocused 
            ? 'border-primary-500 shadow-sm ring-1 ring-primary-500' 
            : 'border-gray-300 dark:border-gray-600'
        } transition-all overflow-hidden`}>
          <textarea
            ref={inputRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Type your message..."
            className="flex-1 max-h-32 py-3 pl-4 pr-12 bg-transparent resize-none focus:outline-none"
            rows={1}
          />
          
          {message && (
            <button
              type="button"
              onClick={() => setMessage('')}
              className="absolute right-14 bottom-3 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              aria-label="Clear message"
            >
              <X className="h-5 w-5" />
            </button>
          )}
          
          <button
            type="submit"
            disabled={!message.trim() || isLoading}
            className="absolute right-3 bottom-2.5 p-1.5 rounded-full bg-primary-500 text-white hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Send message"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
        
        <div className="mt-2 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              type="button"
              className="p-1.5 rounded text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Search the web"
              title="Search the web"
            >
              <Search className="h-4 w-4" />
            </button>
            <button
              type="button"
              className="p-1.5 rounded text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Add images"
              title="Add images"
            >
              <Image className="h-4 w-4" />
            </button>
            <button
              type="button"
              className="p-1.5 rounded text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Create charts"
              title="Create charts"
            >
              <BarChart3 className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-1.5 rounded text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Upload PDF"
              title="Upload PDF"
            >
              <FileText className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() => csvInputRef.current?.click()}
              className="p-1.5 rounded text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Upload CSV"
              title="Upload CSV"
            >
              <FileSpreadsheet className="h-4 w-4" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
            />
            <input
              ref={csvInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
          
          <div className="text-xs text-gray-500 dark:text-gray-400">
            {isLoading ? 'Assistant is thinking...' : 'Press Enter to send'}
          </div>
        </div>
      </form>
    </div>
  );
};

export default InputPanel;