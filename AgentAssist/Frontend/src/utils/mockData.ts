import { IChartData } from '../types/chat';

export const mockResponses = [
  "I'm an AI assistant designed to help answer your questions and provide information. What else would you like to know?",
  "That's an interesting question. Based on my knowledge, I can provide you with some information on this topic.",
  "I found several relevant pieces of information that might help answer your question.",
  "Here's what I know about this subject. Would you like me to elaborate on any specific aspect?",
  "I'd be happy to help with that! Let me provide some useful information on this topic.",
  "Great question! There are multiple perspectives on this topic. Let me share what I know.",
  "I've analyzed your question and here's what I can tell you based on my knowledge.",
  "While I don't have personal opinions, I can offer factual information that might help you with this question.",
  "Let me break this down for you. There are several important points to consider about your question.",
  "I understand what you're asking. Here's some information that should help clarify things."
];

export const sampleSearchResults = [
  {
    title: "What is Artificial Intelligence? How Does AI Work? | Built In",
    snippet: "Artificial intelligence is a wide-ranging branch of computer science concerned with building smart machines capable of performing tasks that typically require...",
    url: "https://builtin.com/artificial-intelligence"
  },
  {
    title: "Artificial intelligence - Wikipedia",
    snippet: "Artificial intelligence (AI) is the intelligence of machines or software, as opposed to the intelligence of human beings or animals. AI applications include...",
    url: "https://en.wikipedia.org/wiki/Artificial_intelligence"
  },
  {
    title: "What is AI (Artificial Intelligence)? | IBM",
    snippet: "Artificial intelligence is the science of training machines to perform human tasks. The term was coined in 1956, and advances in computing have since enabled...",
    url: "https://www.ibm.com/topics/artificial-intelligence"
  }
];

export const sampleImages = [
  {
    url: "https://images.pexels.com/photos/2582937/pexels-photo-2582937.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    alt: "Eiffel Tower during daytime",
    caption: "The Eiffel Tower in Paris, France"
  },
  {
    url: "https://images.pexels.com/photos/699466/pexels-photo-699466.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    alt: "Eiffel Tower at night",
    caption: "Night view of the Eiffel Tower with lights"
  },
  {
    url: "https://images.pexels.com/photos/1308940/pexels-photo-1308940.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    alt: "Eiffel Tower from distance",
    caption: "Panoramic view of Paris with the Eiffel Tower"
  },
  {
    url: "https://images.pexels.com/photos/161853/eiffel-tower-paris-france-tower-161853.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    alt: "Eiffel Tower closeup",
    caption: "Close-up view of the Eiffel Tower's structure"
  }
];

export const sampleChartData: Record<string, IChartData> = {
  salesData: {
    type: 'bar' as const,
    title: 'Quarterly Sales Performance',
    xAxisKey: 'quarter',
    dataKeys: ['revenue', 'profit'],
    data: [
      { quarter: 'Q1', revenue: 12000, profit: 5000, units: 400 },
      { quarter: 'Q2', revenue: 19000, profit: 8000, units: 600 },
      { quarter: 'Q3', revenue: 15000, profit: 6500, units: 500 },
      { quarter: 'Q4', revenue: 22000, profit: 9000, units: 700 }
    ]
  },
  userGrowth: {
    type: 'line' as const,
    title: 'User Growth Over Time',
    xAxisKey: 'month',
    dataKeys: ['users', 'activeUsers'],
    data: [
      { month: 'Jan', users: 1000, activeUsers: 800 },
      { month: 'Feb', users: 1500, activeUsers: 1200 },
      { month: 'Mar', users: 2000, activeUsers: 1600 },
      { month: 'Apr', users: 2500, activeUsers: 2100 },
      { month: 'May', users: 3000, activeUsers: 2400 },
      { month: 'Jun', users: 3800, activeUsers: 3000 }
    ]
  },
  marketShare: {
    type: 'pie' as const,
    title: 'Market Share by Product',
    xAxisKey: 'name',
    dataKeys: ['value'],
    data: [
      { name: 'Product A', value: 35 },
      { name: 'Product B', value: 25 },
      { name: 'Product C', value: 20 },
      { name: 'Product D', value: 15 },
      { name: 'Others', value: 5 }
    ]
  },
  websiteTraffic: {
    type: 'area' as const,
    title: 'Website Traffic Sources',
    xAxisKey: 'month',
    dataKeys: ['organic', 'direct', 'referral'],
    data: [
      { month: 'Jan', organic: 4000, direct: 2400, referral: 1800 },
      { month: 'Feb', organic: 4500, direct: 2600, referral: 2000 },
      { month: 'Mar', organic: 5000, direct: 2800, referral: 2200 },
      { month: 'Apr', organic: 4800, direct: 3000, referral: 2400 },
      { month: 'May', organic: 5500, direct: 3200, referral: 2600 },
      { month: 'Jun', organic: 6000, direct: 3500, referral: 3000 }
    ]
  }
};