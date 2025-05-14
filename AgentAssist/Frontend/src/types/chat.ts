export interface IMessage {
  id: string;
  type: 'text' | 'image' | 'chart' | 'search' | 'system';
  content: string;
  sender: 'user' | 'assistant' | 'system';
  timestamp: string;
  images?: Array<{
    url: string;
    alt: string;
    caption?: string;
  }>;
  chartData?: IChartData;
  searchResults?: Array<{
    title: string;
    snippet: string;
    url: string;
  }>;
  fileInfo?: {
    name: string;
    docId: string;
    status: 'uploading' | 'success' | 'error';
    error?: string;
    filePath?: string;
  };
}

export type MessageType = 'text' | 'image' | 'chart' | 'search';

export interface IChartData {
  type: 'bar' | 'line' | 'pie' | 'area';
  data: Array<Record<string, any>>;
  title: string;
  xAxisKey?: string;
  dataKeys: string[];
}

export interface IUploadedFile {
  name: string;
  docId: string;
  timestamp: string;
}

export interface IConversation {
  id: string;
  messages: IMessage[];
  uploadedFiles: IUploadedFile[];
  createdAt: string;
  updatedAt: string;
}