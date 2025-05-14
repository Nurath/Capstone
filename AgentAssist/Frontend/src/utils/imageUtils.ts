import { sampleImages } from './mockData';

// Fetch images based on query (mock implementation)
export async function searchImages(query: string): Promise<Array<{ url: string; alt: string; caption?: string }>> {
  // This is a mock implementation - in a real app, you would call an actual API
  console.log(`Searching for images related to: ${query}`);
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return sample images for any query
  // In a real implementation, this would make API calls to image search services
  return sampleImages;
}