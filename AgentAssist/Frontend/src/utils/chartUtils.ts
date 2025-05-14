import { IChartData } from '../types/chat';
import { sampleChartData } from './mockData';

// Generate appropriate chart based on user request
export function generateChartFromRequest(request: string): IChartData {
  const lowerRequest = request.toLowerCase();
  
  // Return appropriate sample chart based on keywords in request
  if (lowerRequest.includes('sales') || lowerRequest.includes('revenue') || lowerRequest.includes('profit')) {
    return sampleChartData.salesData;
  }
  
  if (lowerRequest.includes('users') || lowerRequest.includes('growth') || lowerRequest.includes('user growth')) {
    return sampleChartData.userGrowth;
  }
  
  if (lowerRequest.includes('market share') || lowerRequest.includes('products') || lowerRequest.includes('distribution')) {
    return sampleChartData.marketShare;
  }
  
  if (lowerRequest.includes('traffic') || lowerRequest.includes('website') || lowerRequest.includes('sources')) {
    return sampleChartData.websiteTraffic;
  }
  
  // Default to sales data if no specific match
  return sampleChartData.salesData;
}

// Helper function to generate random chart data (for demo purposes)
export function generateRandomData(dataPoints: number, keys: string[]): Record<string, any>[] {
  const data: Record<string, any>[] = [];
  
  for (let i = 0; i < dataPoints; i++) {
    const item: Record<string, any> = {
      name: `Item ${i + 1}`,
    };
    
    keys.forEach(key => {
      item[key] = Math.floor(Math.random() * 1000) + 100;
    });
    
    data.push(item);
  }
  
  return data;
}