import { TutorAnswer } from '@/types';
import { generateId } from './utils';

// Mock API functions - replace with real backend calls later

// Different answer sets based on textbook
const answersByTextbook: Record<string, Record<string, Partial<TutorAnswer>>> = {
  'class6-science': {
    photosynthesis: {
      question: 'Explain photosynthesis in simple words',
      simpleExplanation:
        'Photosynthesis is the process where plants make their own food using sunlight. Plants take in water, sunlight, and a gas from the air called carbon dioxide. Using these, they make food (glucose) and release oxygen that we breathe.',
      detailedExplanation:
        'Photosynthesis occurs in two stages: the light-dependent reactions and the Calvin cycle. In the thylakoid membranes, light energy is absorbed by chlorophyll, splitting water molecules and producing oxygen. The light reactions also generate ATP and NADPH. These energy carriers then power the Calvin cycle, where carbon dioxide is fixed into glucose using the enzyme RuBisCO. This process is essential for converting solar energy into chemical energy stored in organic molecules, supporting virtually all life on Earth.',
      sourceChapter: 'Chapter 5: Life Processes',
      pageNumber: 78,
    },
    plant: {
      question: 'What are the different parts of a plant and their functions?',
      simpleExplanation:
        'Plants have many parts: roots take in water and nutrients, stems carry water up, leaves make food, flowers make seeds, and fruits protect and spread seeds.',
      detailedExplanation:
        'Plant anatomy consists of several organ systems. Roots absorb water and dissolved minerals, and can store nutrients. The root system is either a taproot or fibrous. Stems transport water and nutrients, provide structural support, and can photosynthesize in some species. Leaves are the primary photosynthetic organs with a waxy cuticle, stomata for gas exchange, and internal mesophyll tissue. Flowers contain reproductive structures (stamens and carpels). Fruits develop from the ovary and aid in seed dispersal.',
      sourceChapter: 'Chapter 3: Plant Structure',
      pageNumber: 45,
    },
  },
  'class8-science': {
    force: {
      question: 'What is force in science?',
      simpleExplanation:
        'A force is a push or a pull. It can make something move, stop moving, or change direction. For example, kicking a ball is a force. The weight pulling you down is also a force.',
      detailedExplanation:
        'In physics, a force is an interaction that causes a change in motion of an object. Forces are vector quantities, meaning they have both magnitude and direction. Newtons three laws of motion describe force behavior: first, an object at rest stays at rest unless acted upon by a force. Second, force equals mass times acceleration (F=ma). Third, for every action, there is an equal and opposite reaction. Forces include gravity, friction, tension, and applied forces. They can be contact forces or action-at-a-distance forces.',
      sourceChapter: 'Chapter 9: Force and Motion',
      pageNumber: 134,
    },
    friction: {
      question: 'What is friction?',
      simpleExplanation:
        'Friction is a force that opposes motion. When objects slide against each other, friction causes them to slow down. Rougher surfaces have more friction than smooth surfaces.',
      detailedExplanation:
        'Friction is the resistive force that results from the interaction between two surfaces in contact. There are several types: static friction prevents motion when forces are applied, kinetic friction acts during sliding, rolling friction occurs when objects roll, and fluid friction acts on objects moving through liquids or gases. The magnitude of friction depends on the normal force and the coefficient of friction between the surfaces. Friction converts mechanical energy into heat, which is why friction generates warmth.',
      sourceChapter: 'Chapter 9: Force and Motion',
      pageNumber: 142,
    },
  },
  'class8-mathematics': {
    algebra: {
      question: 'What is algebra and why is it important?',
      simpleExplanation:
        'Algebra is the part of mathematics that uses letters (like x and y) to represent unknown numbers. It helps us solve problems by writing equations and finding what the unknown numbers are.',
      detailedExplanation:
        'Algebra is a branch of mathematics that deals with symbols and the rules for manipulating those symbols. Variables represent unknown quantities, and algebraic expressions combine variables and constants using operations. Linear equations are statements of equality involving variables. Systems of equations can be solved using substitution or elimination methods. Algebraic concepts form the foundation for higher mathematics including polynomials, factorization, quadratic equations, and eventually calculus.',
      sourceChapter: 'Chapter 7: Introduction to Algebra',
      pageNumber: 98,
    },
    geometry: {
      question: 'What are the properties of triangles?',
      simpleExplanation:
        'Triangles are shapes with three sides and three angles. The sum of all angles in any triangle is always 180 degrees. Triangles can be classified as equilateral, isosceles, or scalene.',
      detailedExplanation:
        'Triangles are polygons with three vertices and three edges. The sum of interior angles equals 180°. Classification by sides: equilateral (all equal), isosceles (two equal), scalene (all different). Classification by angles: acute (all < 90°), right (one = 90°), obtuse (one > 90°). The area formula is ½ × base × height. The Pythagorean theorem applies to right triangles: a² + b² = c². Congruence and similarity theorems help identify when triangles are equal or proportional.',
      sourceChapter: 'Chapter 12: Geometry - Triangles',
      pageNumber: 167,
    },
  },
};

// Generic answers for any textbook
const genericAnswers: Record<string, Partial<TutorAnswer>> = {
  photosynthesis: {
    question: 'Explain photosynthesis',
    simpleExplanation:
      'Photosynthesis is the process where plants make their own food using sunlight, water, and carbon dioxide from the air. During this process, plants release oxygen which we breathe.',
    detailedExplanation:
      'Photosynthesis is the biochemical process that converts light energy into chemical energy in glucose. It occurs in two main stages: light reactions in the thylakoid membranes and the Calvin cycle in the stroma. Chlorophyll and accessory pigments absorb photons, exciting electrons to higher energy states. These electrons are used to reduce NADP⁺ to NADPH and generate ATP through chemiosmosis. The Calvin cycle uses these energy carriers to fix CO₂ into 3-phosphoglycerate, which is reduced to G3P and either exported or regenerates RuBP.',
    sourceChapter: 'Photosynthesis Unit',
    pageNumber: 1,
  },
  seasons: {
    question: 'Why do seasons change on Earth?',
    simpleExplanation:
      'Seasons change because of the tilt of Earth. As Earth moves around the sun, different parts get different amounts of sunlight. When your part tilts towards the sun, it gets more heat and light, making it summer.',
    detailedExplanation:
      "Earth's rotational axis is tilted at approximately 23.5 degrees relative to the plane of its orbit around the sun. As Earth orbits the sun over a year, this tilt causes different hemispheres to receive varying amounts of solar radiation. During summer solstice, the Northern Hemisphere is maximally tilted toward the sun, resulting in longer days and more direct sunlight. During winter solstice, it's tilted away, causing shorter days and less intense solar radiation.",
    sourceChapter: 'Earth Systems',
    pageNumber: 1,
  },
  force: {
    question: 'What is force?',
    simpleExplanation:
      'A force is a push or pull that can change how something moves. Forces act on objects to accelerate them, stop them, or change their direction.',
    detailedExplanation:
      'Force is defined as any interaction that, when unopposed, will change the motion of an object. Forces are vectors with both magnitude and direction. The SI unit is the Newton (N). Forces can be classified as contact forces (friction, tension, applied force) or field forces (gravity, electromagnetic). Newtons laws of motion provide the framework for understanding how forces affect objects motion.',
    sourceChapter: 'Force and Motion',
    pageNumber: 1,
  },
};

export async function askQuestion(
  question: string,
  textbookId: string,
  language: 'en' | 'hi' = 'en'
): Promise<TutorAnswer> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1500));

  const questionLower = question.toLowerCase();
  
  // Get textbook-specific answers if available, otherwise use generic
  const textbookAnswers = answersByTextbook[textbookId] || {};
  let answer: Partial<TutorAnswer> = genericAnswers.photosynthesis;

  // Try to find a matching answer based on keywords
  for (const [keyword, answerObj] of Object.entries(textbookAnswers)) {
    if (questionLower.includes(keyword)) {
      answer = answerObj;
      break;
    }
  }

  // If no textbook-specific answer, try generic
  if (answer === genericAnswers.photosynthesis) {
    if (questionLower.includes('season')) answer = genericAnswers.seasons;
    else if (questionLower.includes('force')) answer = genericAnswers.force;
    else if (questionLower.includes('photosynth')) answer = genericAnswers.photosynthesis;
  }

  return {
    id: generateId(),
    ...answer,
    language,
  } as TutorAnswer;
}

export async function uploadTextbook(
  file: File
): Promise<{ success: boolean; filename: string; chapters: number }> {
  // Simulate upload delay
  await new Promise((resolve) => setTimeout(resolve, 2000));

  return {
    success: true,
    filename: file.name,
    chapters: Math.floor(Math.random() * 20) + 10,
  };
}

export async function getMetrics() {
  // Simulate API call
  await new Promise((resolve) => setTimeout(resolve, 800));

  return {
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
  };
}
