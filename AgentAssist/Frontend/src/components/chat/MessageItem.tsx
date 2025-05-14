import React from 'react';
import { User, Bot, Upload, CheckCircle, XCircle } from 'lucide-react';
import { IMessage } from '../../types/chat';
import TextContent from './message-content/TextContent';
import ImageContent from './message-content/ImageContent';
import ChartContent from './message-content/ChartContent';
import SearchContent from './message-content/SearchContent';
import { formatDistanceToNow } from 'date-fns';

interface MessageItemProps {
  message: IMessage;
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const isSystem = message.sender === 'system';
  
  const renderContent = () => {
    switch (message.type) {
      case 'text':
        return <TextContent content={message.content} />;
      case 'image':
        return <ImageContent images={message.images || []} />;
      case 'chart':
        return <ChartContent chartData={message.chartData || {
          type: 'bar',
          data: [],
          title: 'No Data Available',
          dataKeys: []
        }} />;
      case 'search':
        return <SearchContent searchResults={message.searchResults || []} />;
      case 'system':
        if (message.fileInfo) {
          return (
            <div className="flex items-center gap-2">
              {message.fileInfo.status === 'uploading' && (
                <Upload className="h-4 w-4 text-blue-500 animate-pulse" />
              )}
              {message.fileInfo.status === 'success' && (
                <CheckCircle className="h-4 w-4 text-green-500" />
              )}
              {message.fileInfo.status === 'error' && (
                <XCircle className="h-4 w-4 text-red-500" />
              )}
              <TextContent content={message.content} />
            </div>
          );
        }
        return <TextContent content={message.content} />;
      default:
        return <TextContent content={message.content} />;
    }
  };

  const getIcon = () => {
    if (isSystem) {
      if (message.fileInfo) {
        switch (message.fileInfo.status) {
          case 'uploading':
            return <Upload className="h-5 w-5 text-blue-500" />;
          case 'success':
            return <CheckCircle className="h-5 w-5 text-green-500" />;
          case 'error':
            return <XCircle className="h-5 w-5 text-red-500" />;
        }
      }
      return <Bot className="h-5 w-5 text-gray-500" />;
    }
    return isUser ? (
      <User className="h-5 w-5 text-white" />
    ) : (
      <Bot className="h-5 w-5 text-white" />
    );
  };

  const getBackgroundColor = () => {
    if (isSystem) {
      if (message.fileInfo) {
        switch (message.fileInfo.status) {
          case 'uploading':
            return 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300';
          case 'success':
            return 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300';
          case 'error':
            return 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300';
        }
      }
      return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
    }
    return isUser
      ? 'bg-accent-500 text-white'
      : 'bg-primary-500 text-white';
  };

  return (
    <div className={`flex items-start gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isSystem ? 'bg-transparent' : isUser ? 'bg-accent-500' : 'bg-primary-500'
      }`}>
        {getIcon()}
      </div>
      
      <div className={`p-3 max-w-[80%] rounded-lg ${getBackgroundColor()}`}>
        {renderContent()}
        <div className={`text-xs mt-1 ${
          isSystem 
            ? message.fileInfo?.status === 'error' 
              ? 'text-red-500 dark:text-red-400'
              : 'text-gray-500 dark:text-gray-400'
            : isUser 
              ? 'text-accent-50' 
              : 'text-primary-50'
        }`}>
          {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
        </div>
      </div>
    </div>
  );
};

export default MessageItem;