// Types for the Education Tutor app

export interface Textbook {
  id: string;
  name: string;
  class: string;
  subject: string;
  chapters: number;
}

export interface UploadedFile {
  id: string;
  filename: string;
  uploadedAt: Date;
  size: number;
  chapters: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  textbookId?: string;
}

export interface TutorAnswer {
  id: string;
  question: string;
  simpleExplanation: string;
  detailedExplanation: string;
  sourceChapter: string;
  pageNumber?: number;
  language: 'en' | 'hi';
}

export interface MetricsData {
  tokenReduction: {
    baseline: number;
    optimized: number;
    percentage: number;
  };
  latencyReduction: {
    baseline: number;
    optimized: number;
    percentage: number;
  };
  costSavings: {
    baseline: number;
    optimized: number;
    percentage: number;
  };
  answerRelevance: {
    baseline: number;
    optimized: number;
    percentage: number;
  };
  testSize: number;
  testCases: string[];
}

export interface UploadedTextbook {
  id: string;
  filename: string;
  uploadedAt: Date;
  size: number;
  chapters: number;
}
