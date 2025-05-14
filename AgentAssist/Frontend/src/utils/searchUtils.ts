import { sampleSearchResults } from './mockData';

// Search the web based on query (mock implementation)
export async function searchWeb(query: string): Promise<Array<{ title: string; snippet: string; url: string }>> {
  // This is a mock implementation - in a real app, you would call an actual search API
  console.log(`Searching the web for: ${query}`);
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1200));
  
  // Return sample search results for any query
  // In a real implementation, this would make API calls to search engines
  return sampleSearchResults;
}