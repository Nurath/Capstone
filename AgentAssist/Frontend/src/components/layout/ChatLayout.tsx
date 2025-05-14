import React from 'react';
import { FileText, FileSpreadsheet } from 'lucide-react';
import Header from './Header';
import ChatWindow from '../chat/ChatWindow';
import InputPanel from '../chat/InputPanel';
import { useTheme } from '../../contexts/ThemeContext';
import { useChat } from '../../contexts/ChatContext';
import { formatDistanceToNow } from 'date-fns';

const ChatLayout: React.FC = () => {
  const { isDark } = useTheme();
  const { uploadedFiles } = useChat();
  
  const getFileIcon = (fileName: string) => {
    return fileName.toLowerCase().endsWith('.csv') ? (
      <FileSpreadsheet className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
    ) : (
      <FileText className="h-4 w-4 text-primary-500 mt-0.5 flex-shrink-0" />
    );
  };

  return (
    <div className={`min-h-screen flex flex-col ${isDark ? 'dark' : ''}`}>
      <Header />
      <main className="flex-1 container mx-auto px-4 md:px-6 py-4 flex flex-col">
        <div className="flex-1 flex bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          {/* Sidebar with uploaded files */}
          <div className="w-64 border-r border-gray-200 dark:border-gray-700 p-4 overflow-y-auto">
            <h2 className="font-semibold text-gray-700 dark:text-gray-300 mb-4">Uploaded Files</h2>
            {uploadedFiles.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">No files uploaded yet</p>
            ) : (
              <ul className="space-y-2">
                {uploadedFiles.map((file) => (
                  <li 
                    key={file.docId}
                    className="p-2 rounded-lg bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-start gap-2">
                      {getFileIcon(file.name)}
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatDistanceToNow(new Date(file.timestamp), { addSuffix: true })}
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Main chat area */}
          <div className="flex-1 flex flex-col">
            <ChatWindow />
            <InputPanel />
          </div>
        </div>
      </main>
      <footer className="py-4 text-center text-sm text-gray-500 dark:text-gray-400">
        <p>© {new Date().getFullYear()} AI Chat Assistant. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default ChatLayout;