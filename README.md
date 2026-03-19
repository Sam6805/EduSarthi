# EduTutor Frontend

AI-powered tutoring for students in remote India.

## Overview

This is a **frontend-only** project for The Education Tutor - an AI tutoring platform designed specifically for students in rural and remote India. Students can learn from school textbooks through an intelligent interface that provides simple, context-aware explanations.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **APIs**: Mock functions (easily replaceable with Backend calls)

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout with navbar/footer
│   ├── globals.css              # Global styles
│   ├── page.tsx                 # Landing page
│   ├── tutor/page.tsx          # Main tutoring interface
│   ├── upload/page.tsx         # Textbook upload page
│   └── metrics/page.tsx        # Performance metrics page
├── components/
│   ├── layout/                  # Navbar, Footer
│   ├── landing/                 # Hero, Features, Workflow, CTA
│   ├── tutor/                   # Chat, Answers, Controls
│   ├── upload/                  # Upload widget, File list
│   ├── metrics/                 # Cards, Comparison table
│   └── ui/                      # Button, Card, Badge, Input
├── hooks/
│   └── useTutorChat.ts         # Chat state management
├── lib/
│   ├── mockApi.ts              # Mock API functions
│   └── utils.ts                # Utilities (cn, format, etc)
├── constants/
│   ├── textbooks.ts            # Mock textbook data
│   ├── sampleQuestions.ts      # Sample questions
│   └── metrics.ts              # Mock metrics data
├── types/
│   └── index.ts                # TypeScript interfaces
├── public/                       # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.ts
```

## Pages

### 1. Landing Page (`/`)
- Hero section with clear value proposition
- Feature cards explaining the product
- Workflow visualization
- CTA buttons to start learning

### 2. Tutor Page (`/tutor`)
- **Core interface** for learning
- Textbook selector dropdown
- Chat interface with messages
- Sample questions for quick start
- Answer cards with simple + detailed explanations
- Language toggle (English/Hindi)
- Low data mode toggle
- Empty state for new users
- Loading states while generating answers

### 3. Upload Page (`/upload`)
- Drag-and-drop PDF upload
- Guidelines for best results
- List of uploaded textbooks
- Mock data showing previously uploaded files

### 4. Metrics Page (`/metrics`)
- Key performance indicators
- Comparison table (baseline vs optimized)
- Real-world impact section
- Test dataset details

## Getting Started

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

## Features

✅ **Responsive Design** - Mobile-first, works on all devices
✅ **Type-Safe** - Full TypeScript support
✅ **Mock Data** - Realistic demo content
✅ **Easy Backend Integration** - Replace mock API calls with real endpoints
✅ **Clean Architecture** - Organized, scalable structure
✅ **Hackathon Ready** - Professional UI for impressive demos

## Key Components

### Reusable UI Components
- `Button` - Variants: primary, secondary, outline
- `Card` - CardHeader, CardContent, CardFooter
- `Badge` - Variants: primary, secondary, success, warning
- `Input` - Text input with label and error support

### Feature Components
- `TextbookSelector` - Dropdown for selecting active textbook
- `ChatBox` - Question input area
- `AnswerCard` - Answer display with source tracking
- `MessageBubble` - Chat message display
- `SampleQuestions` - Quick question chips
- `UploadTextbook` - Drag-drop upload area
- `MetricsCard` - Key metric display
- `ComparisonTable` - Performance comparison

### Custom Hooks
- `useTutorChat()` - Manage chat state, messages, and API interactions

## Mock API Functions

Located in `lib/mockApi.ts`:

```typescript
askQuestion(question: string, textbookId: string, language: 'en' | 'hi')
uploadTextbook(file: File)
getMetrics()
```

**To connect to real backend:**
1. Replace mock implementations in `lib/mockApi.ts`
2. Update endpoint URLs when backend is ready
3. No changes needed in components - they're fully decoupled

## Styling

- **Framework**: Tailwind CSS
- **Design System**: Minimal, educational feel
- **Colors**: Blue primary (#2563eb), clean grays
- **Spacing**: Consistent padding/margins throughout
- **Typography**: System fonts for performance

## Type Definitions

Main types in `types/index.ts`:

```typescript
- Textbook
- ChatMessage
- TutorAnswer
- MetricsData
- UploadedTextbook
```

## Performance Optimizations

- Code splitting with Next.js
- Image optimization
- CSS tree-shaking with Tailwind
- Production build optimization
- No unnecessary dependencies

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Future Enhancements

- Real backend integration with FastAPI
- User authentication
- Progress tracking
- Offline mode
- Multi-language support beyond English/Hindi
- Advanced analytics

## Development Notes

- All API calls are currently mocked with realistic delays
- Mock data reflects real Indian textbook curriculum
- Component structure allows easy feature additions
- CSS is utility-first (Tailwind) for maintainability

## File Size & Performance

- Zero external UI library dependencies
- Minimal bundle size with Next.js
- Fast loading on slow networks
- Optimized for educational use case

---

Built for the **Education Tutor Hackathon** 🎓
