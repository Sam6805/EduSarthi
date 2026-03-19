export const SAMPLE_QUESTIONS = [
  'Explain photosynthesis in simple words',
  'Why do seasons change on Earth?',
  'What is force in science?',
  'How do plants absorb water?',
  'What are renewable energy sources?',
  'Explain the water cycle',
  'What causes earthquakes?',
  'How do ecosystems work?',
];

// Textbook-specific sample questions
export const SAMPLE_QUESTIONS_BY_TEXTBOOK: Record<string, string[]> = {
  'class6-science': [
    'Explain photosynthesis in simple words',
    'What are the parts of a plant and their functions?',
    'How do plants absorb water?',
    'Why do seasons change on Earth?',
    'What causes earthquakes?',
    'Explain the water cycle',
  ],
  'class8-science': [
    'What is force in science?',
    'What is friction and how does it affect motion?',
    'Explain how levers work',
    'What are the three laws of motion?',
    'How does electricity flow in circuits?',
    'What is the difference between speed and velocity?',
  ],
  'class8-mathematics': [
    'How do I solve linear equations?',
    'What is algebra and why is it important?',
    'What are the properties of triangles?',
    'How do I use variables in equations?',
    'What is the Pythagorean theorem?',
    'How do I calculate the area of a circle?',
    'What are ratios and proportions?',
    'How do I solve systems of equations?',
  ],
};

// Get sample questions for a specific textbook
export function getSampleQuestionsForTextbook(textbookId: string): string[] {
  return SAMPLE_QUESTIONS_BY_TEXTBOOK[textbookId] || SAMPLE_QUESTIONS;
}
