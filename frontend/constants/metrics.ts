import { MetricsData } from '@/types';

export const METRICS_DATA: MetricsData = {
  tokenReduction: {
    baseline: 2847,
    optimized: 892,
    percentage: 68.7,
  },
  latencyReduction: {
    baseline: 3.2,
    optimized: 0.9,
    percentage: 71.9,
  },
  costSavings: {
    baseline: 0.085,
    optimized: 0.028,
    percentage: 67.1,
  },
  answerRelevance: {
    baseline: 0.72,
    optimized: 0.94,
    percentage: 30.6,
  },
  testSize: 247,
  testCases: [
    'Class 6 Science - Photosynthesis questions',
    'Class 7 Geography - Earth structure queries',
    'Class 8 Mathematics - Algebra problems',
    'Class 8 Science - Physics concepts',
    'Class 9 History - Ancient India context',
    'Mixed subject cross-chapter references',
  ],
};

export const COMPARISON_DATA = [
  {
    metric: 'Average Input Tokens',
    baseline: 2847,
    optimized: 892,
    unit: 'tokens',
  },
  {
    metric: 'Response Time (p95)',
    baseline: 3.2,
    optimized: 0.9,
    unit: 'seconds',
  },
  {
    metric: 'Cost per Request',
    baseline: 0.085,
    optimized: 0.028,
    unit: '$',
  },
  {
    metric: 'Context Relevance Score',
    baseline: 0.72,
    optimized: 0.94,
    unit: 'score',
  },
  {
    metric: 'Answer Correctness',
    baseline: 0.88,
    optimized: 0.96,
    unit: '%',
  },
  {
    metric: 'Student Satisfaction',
    baseline: 0.81,
    optimized: 0.97,
    unit: '%',
  },
];
