import React from 'react';
import ReactMarkdown from 'react-markdown';

interface TextContentProps {
  content: string;
}

const TextContent: React.FC<TextContentProps> = ({ content }) => {
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
};

export default TextContent;