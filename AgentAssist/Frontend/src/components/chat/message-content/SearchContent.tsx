import React from 'react';
import { ExternalLink } from 'lucide-react';

interface SearchResult {
  title: string;
  snippet: string;
  url: string;
}

interface SearchContentProps {
  searchResults: SearchResult[];
}

const SearchContent: React.FC<SearchContentProps> = ({ searchResults }) => {
  if (!searchResults.length) {
    return <p>No search results found.</p>;
  }

  return (
    <div>
      <h3 className="text-base font-medium mb-2">Search Results</h3>
      <div className="space-y-3">
        {searchResults.map((result, index) => (
          <div key={index} className="bg-white dark:bg-gray-800 p-3 rounded shadow-sm">
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1"
            >
              {result.title}
              <ExternalLink className="h-3 w-3" />
            </a>
            <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">{result.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchContent;