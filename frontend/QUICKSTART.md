# Quick Start Guide - EduTutor Frontend

## ⚡ Setup (5 minutes)

### Prerequisites
- Node.js 16+ and npm installed
- Code editor (VS Code recommended)

### Installation

```bash
# Navigate to frontend folder
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🎯 Tour the App

1. **Landing Page** (`/`) - Overview and marketing
2. **Tutor Page** (`/tutor`) - Main learning interface
3. **Upload Page** (`/upload`) - Textbook management
4. **Metrics Page** (`/metrics`) - Impact demonstration

## 📝 Important Files to Know

### Pages
- `app/page.tsx` - Landing page
- `app/tutor/page.tsx` - Main interface
- `app/upload/page.tsx` - Upload management
- `app/metrics/page.tsx` - Metrics dashboard

### Components
- `components/tutor/ChatBox.tsx` - Question input
- `components/tutor/AnswerCard.tsx` - Answer display
- `components/landing/HeroSection.tsx` - Hero banner

### Logic
- `hooks/useTutorChat.ts` - State management
- `lib/mockApi.ts` - API functions (replace these!)
- `constants/` - Mock data

## 🔌 Connecting to Backend

1. Open `lib/mockApi.ts`
2. Replace mock functions with actual API calls:

```typescript
export async function askQuestion(question: string, textbookId: string, language: 'en' | 'hi') {
  // Replace this with your FastAPI endpoint
  const response = await fetch('http://your-backend/api/ask', {
    method: 'POST',
    body: JSON.stringify({ question, textbookId, language }),
  });
  return response.json();
}
```

3. Update URLs for uploadTextbook() and getMetrics() similarly
4. **No component changes needed!** They're fully decoupled

## 🚀 Building for Production

```bash
npm run build
npm start
```

## 📱 Device Testing

Open DevTools (F12) → Toggle device toolbar to test on:
- Desktop
- Tablet
- iPhone
- Android

All pages are mobile-responsive.

## 🎨 Customization

### Change Colors
Edit `tailwind.config.ts` - change primary color from `#2563eb`

### Update Content
- Mock data: `constants/` folder
- Page text: Individual `app/*/page.tsx` files
- UI text: Individual component files

### Add Features
New components go in `components/` with same structure

## 📊 Mock Data

### Textbooks
`constants/textbooks.ts` - Class 6-10 subjects

### Questions
`constants/sampleQuestions.ts` - Sample learning topics

### Metrics
`constants/metrics.ts` - Performance comparison data

## ❓ Troubleshooting

**Port 3000 already in use?**
```bash
npm run dev -- -p 3001
```

**Module errors?**
```bash
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors?**
Check your TypeScript version: `npm list typescript`

## 📚 Key Technologies

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **React Hooks** - State management

## 📞 For the Hackathon

- All UI is responsive and works on mobile ✅
- Mock data makes it demo-ready ✅
- Code is clean and production-ready ✅
- Easy to integrate real backend ✅
- Professional educational design ✅

Good luck! 🚀
