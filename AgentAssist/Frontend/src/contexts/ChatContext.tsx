import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { IMessage, MessageType, IUploadedFile, IConversation } from '../types/chat';
import { v4 as uuidv4 } from '../utils/uuid';
import { mockResponses } from '../utils/mockData';
import { generateChartFromRequest } from '../utils/chartUtils';
import { searchImages } from '../utils/imageUtils';
import { searchWeb } from '../utils/searchUtils';

interface ChatContextType {
  messages: IMessage[];
  isLoading: boolean;
  conversationId: string;
  uploadedFiles: IUploadedFile[];
  chatDocuments: any[];
  sendMessage: (content: string) => Promise<void>;
  uploadFile: (file: File) => Promise<void>;
  resetConversation: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

const API_BASE_URL = 'http://localhost:5000/api';

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(() => uuidv4());
  const [uploadedFiles, setUploadedFiles] = useState<IUploadedFile[]>([]);
  const [chatDocuments, setChatDocuments] = useState<any[]>([]);

  // Initialize with welcome message
  React.useEffect(() => {
    setMessages([
      {
        id: uuidv4(),
        type: 'text',
        content: 'Hello! I\'m your AI assistant. How can I help you today? You can upload PDF files for me to analyze.',
        sender: 'assistant',
        timestamp: new Date().toISOString()
      }
    ]);
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: IMessage = {
      id: uuidv4(),
      type: 'text',
      content,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId
        })
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      
      // Add this line to update chatDocuments
      setChatDocuments(data.documents || []);

      // If images are present, add an image message
      if (data.images && Array.isArray(data.images) && data.images.length > 0) {
        const imageMessages = data.images.map((img: string, idx: number) => ({
          url: `data:image/jpeg;base64,${img}`,
          alt: `Related image ${idx + 1}`,
          caption: '', // Add a caption if available
        }));

        const assistantImageMessage: IMessage = {
          id: uuidv4(),
          type: 'image',
          content: '', // or a summary if you want
          sender: 'assistant',
          timestamp: new Date().toISOString(),
          images: imageMessages,
        };

        setMessages(prev => [...prev, assistantImageMessage]);
      }

      // Always add the text response as well
      const assistantMessage: IMessage = {
        id: uuidv4(),
        type: 'text',
        content: data.response,
        sender: 'assistant',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: IMessage = {
        id: uuidv4(),
        type: 'system',
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}. Please try again.`,
        sender: 'system',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId]);

  const uploadFile = useCallback(async (file: File) => {
    const isPDF = file.type === 'application/pdf';
    const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv');

    if (!isPDF && !isCSV) {
      const errorMessage: IMessage = {
        id: uuidv4(),
        type: 'system',
        content: `${file.name} is not a supported file type. Please upload a PDF or CSV file.`,
        sender: 'system',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    const uploadingMessage: IMessage = {
      id: uuidv4(),
      type: 'system',
      content: `Uploading ${file.name}...`,
      sender: 'system',
      timestamp: new Date().toISOString(),
      fileInfo: {
        name: file.name,
        docId: '',
        status: 'uploading'
      }
    };

    setMessages(prev => [...prev, uploadingMessage]);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('conversation_id', conversationId);

      const endpoint = isPDF ? '/upload-pdf' : '/upload-csv';
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error(`Failed to upload ${file.name}`);

      const data = await response.json();

      const newFile: IUploadedFile = {
        name: file.name,
        docId: data.doc_id,
        timestamp: new Date().toISOString()
      };

      setUploadedFiles(prev => [...prev, newFile]);

      // Update the uploading message to success
      setMessages(prev => prev.map(msg => 
        msg.id === uploadingMessage.id
          ? {
              ...msg,
              content: `Successfully uploaded ${file.name}. ${isPDF ? 'You can now ask questions about this document.' : `The CSV file is now available for analysis. File path: ${data.file_path}`}`,
              fileInfo: {
                ...msg.fileInfo!,
                docId: data.doc_id,
                status: 'success',
                filePath: data.file_path
              }
            }
          : msg
      ));
    } catch (error) {
      // Update the uploading message to error
      setMessages(prev => prev.map(msg => 
        msg.id === uploadingMessage.id
          ? {
              ...msg,
              content: `Error uploading ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`,
              fileInfo: {
                ...msg.fileInfo!,
                status: 'error',
                error: error instanceof Error ? error.message : 'Unknown error'
              }
            }
          : msg
      ));
    }
  }, [conversationId]);

  const resetConversation = useCallback(async () => {
    try {
      await fetch(`${API_BASE_URL}/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: conversationId })
      });

      // Generate new conversation ID
      const newConversationId = uuidv4();
      setConversationId(newConversationId);

      // Keep uploaded files but clear messages except for welcome message
      setMessages([
        {
          id: uuidv4(),
          type: 'text',
          content: 'Conversation has been reset. How can I help you?',
          sender: 'assistant',
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (error) {
      const errorMessage: IMessage = {
        id: uuidv4(),
        type: 'system',
        content: `Error resetting conversation: ${error instanceof Error ? error.message : 'Unknown error'}`,
        sender: 'system',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  }, [conversationId]);

  return (
    <ChatContext.Provider value={{
      messages,
      isLoading,
      conversationId,
      uploadedFiles,
      chatDocuments,
      sendMessage,
      uploadFile,
      resetConversation
    }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};