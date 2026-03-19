# Frontend Integration Guide

## Connecting Your Next.js Frontend to The Backend

This guide shows how to integrate the Education Tutor backend with your existing Next.js frontend.

---

## Backend Service Layer

Create a new file: `frontend/lib/backendApi.ts`

```typescript
/**
 * Backend API service for Education Tutor
 * Communicates with FastAPI backend at localhost:8000 (dev) or production URL
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

interface QueryRequest {
  question: string;
  textbook_id?: string;
  language: 'en' | 'hi';
  use_pruning?: boolean;
}

interface QueryResponse {
  question: string;
  answer: {
    simple_answer: string;
    detailed_answer?: string;
    source_chapter?: string;
    source_pages?: number[];
  };
  retrieved_chunks_count: number;
  pruned_chunks_count: number;
  token_estimate_before_pruning: number;
  token_estimate_after_pruning: number;
  token_reduction_percentage: number;
  retrieval_latency_ms: number;
  pruning_latency_ms: number;
  generation_latency_ms: number;
  total_latency_ms: number;
  textbook_used: string;
}

// Query API
export async function askQuestion(request: QueryRequest): Promise<QueryResponse> {
  const response = await fetch(`${BACKEND_URL}/api/query/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.statusText}`);
  }

  return response.json();
}

// Get metrics
export async function getMetrics() {
  const response = await fetch(`${BACKEND_URL}/api/query/metrics`);
  return response.json();
}

// Get vector store stats
export async function getVectorStoreStats() {
  const response = await fetch(`${BACKEND_URL}/api/query/vector-store-stats`);
  return response.json();
}

// Health check
export async function healthCheck() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`, {
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

// Ingest textbook (file upload)
export async function uploadTextbook(
  file: File,
  textbookName: string,
  classLevel?: string,
  subject?: string
) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('textbook_name', textbookName);
  if (classLevel) formData.append('class_level', classLevel);
  if (subject) formData.append('subject', subject);

  const response = await fetch(`${BACKEND_URL}/api/ingest/textbook`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
}

// Ingest demo textbook
export async function ingestDemo() {
  const response = await fetch(`${BACKEND_URL}/api/ingest/demo-textbook`, {
    method: 'POST',
  });
  return response.json();
}

// Get list of textbooks
export async function listTextbooks() {
  const response = await fetch(`${BACKEND_URL}/api/ingest/textbooks`);
  return response.json();
}
```

---

## Update Your Tutor Page Hook

Modify: `frontend/hooks/useTutorChat.ts`

```typescript
'use client';

import { useState, useCallback, useEffect } from 'react';
import { ChatMessage, TutorAnswer } from '@/types';
import { askQuestion } from '@/lib/backendApi';  // Use backend instead of mockApi
import { generateId } from '@/lib/utils';

export function useTutorChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [answers, setAnswers] = useState<TutorAnswer[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTextbook, setSelectedTextbook] = useState<string>('class6-science');
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [backendConnected, setBackendConnected] = useState(false);

  // Check backend connection on mount
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/health');
        setBackendConnected(response.ok);
      } catch {
        setBackendConnected(false);
      }
    };
    checkBackend();
  }, []);

  const sendQuestion = useCallback(
    async (question: string) => {
      if (!question.trim()) return;

      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: question,
        timestamp: new Date(),
        textbookId: selectedTextbook,
      };

      setMessages((prev) => [...prev, userMessage]);
      setLoading(true);

      try {
        // Call backend API
        const response = await askQuestion({
          question,
          textbook_id: selectedTextbook,
          language,
          use_pruning: true, // Enable context pruning
        });

        // Extract answer
        const answer: TutorAnswer = {
          id: generateId(),
          question: response.question,
          simpleExplanation: response.answer.simple_answer,
          detailedExplanation: response.answer.detailed_answer || undefined,
          sourceChapter: response.answer.source_chapter || '',
          pageNumber: response.answer.source_pages?.[0],
          language: language,
        };

        setAnswers((prev) => [...prev, answer]);

        // Add assistant message
        const assistantMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: answer.simpleExplanation,
          timestamp: new Date(),
          textbookId: selectedTextbook,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        console.error('Error asking question:', error);
        setMessages((prev) => [
          ...prev,
          {
            id: generateId(),
            role: 'assistant',
            content: 'Sorry, I encountered an error. Please try again.',
            timestamp: new Date(),
            textbookId: selectedTextbook,
          },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [selectedTextbook, language]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setAnswers([]);
  }, []);

  return {
    messages,
    answers,
    loading,
    selectedTextbook,
    setSelectedTextbook,
    language,
    setLanguage,
    sendQuestion,
    clearChat,
    backendConnected,
  };
}
```

---

## Environment Configuration

Create: `frontend/.env.local`

```bash
# Backend URL (adjust for production)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

---

## Update Answer Card Component

Modify: `frontend/components/tutor/AnswerCard.tsx`

```typescript
'use client';

import { TutorAnswer } from '@/types';
import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface AnswerCardProps {
  answer: TutorAnswer;
  onToggleDetail?: () => void;
  showDetailed?: boolean;
}

export function AnswerCard({ answer, onToggleDetail, showDetailed = false }: AnswerCardProps) {
  return (
    <Card className="bg-gradient-to-br from-green-50 to-teal-50 border-green-200">
      <CardContent className="pt-6 space-y-4">
        {/* Simple Answer */}
        <div>
          <p className="text-sm font-semibold text-green-900 mb-2">📖 Answer</p>
          <p className="text-gray-700 leading-relaxed">{answer.simpleExplanation}</p>
        </div>

        {/* Detailed Answer */}
        {answer.detailedExplanation && (
          <>
            {showDetailed && (
              <div className="border-t border-green-200 pt-4">
                <p className="text-sm font-semibold text-green-900 mb-2">🔍 More Details</p>
                <p className="text-gray-700 leading-relaxed text-sm">
                  {answer.detailedExplanation}
                </p>
              </div>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleDetail}
              className="text-green-700 hover:text-green-900"
            >
              {showDetailed ? 'Show Less' : 'Show More'} Details →
            </Button>
          </>
        )}

        {/* Source Information */}
        {(answer.sourceChapter || answer.pageNumber) && (
          <div className="border-t border-green-200 pt-3">
            <p className="text-xs text-gray-600">
              📍 Source: {answer.sourceChapter}
              {answer.pageNumber && ` • Page ${answer.pageNumber}`}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## Update Upload Page for Backend Integration

```typescript
'use client';

import { useState } from 'react';
import { uploadTextbook, ingestDemo } from '@/lib/backendApi';
import { UploadTextbook } from '@/components/upload/UploadTextbook';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<any>(null);

  const handleFileSelect = async (file: File) => {
    setUploading(true);
    setUploadStatus(null);
    try {
      const result = await uploadTextbook(
        file,
        file.name.replace('.pdf', ''),
        undefined,
        'Science'
      );
      setUploadStatus({
        success: true,
        message: `Successfully ingested! Created ${result.chunks_created} chunks.`,
        details: result,
      });
    } catch (error: any) {
      setUploadStatus({
        success: false,
        message: error.message,
      });
    } finally {
      setUploading(false);
    }
  };

  const loadDemo = async () => {
    setUploading(true);
    try {
      const result = await ingestDemo();
      setUploadStatus({
        success: true,
        message: `Demo textbook loaded! Created ${result.chunks_created} chunks.`,
      });
    } catch (error: any) {
      setUploadStatus({
        success: false,
        message: error.message,
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <h1 className="text-gray-900 mb-8">Upload Your Textbooks</h1>

        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          <div className="lg:col-span-2">
            <UploadTextbook onFileSelect={handleFileSelect} loading={uploading} />
            
            <Button
              onClick={loadDemo}
              disabled={uploading}
              className="mt-4"
            >
              {uploading ? 'Processing...' : 'Try Demo Textbook'}
            </Button>
          </div>
        </div>

        {uploadStatus && (
          <Card className={uploadStatus.success ? 'bg-green-50' : 'bg-red-50'}>
            <CardContent className="pt-6">
              <p className={uploadStatus.success ? 'text-green-900' : 'text-red-900'}>
                {uploadStatus.message}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
```

---

## Development Setup

1. **Start Backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

---

## Production Deployment

### Deploy Backend to Cloud

**Option 1: Heroku**
```bash
cd backend
heroku create your-app-name
heroku config:set LLM_PROVIDER=openai LLM_API_KEY=sk-...
git push heroku main
```

**Option 2: Docker**
```bash
cd backend
docker build -t tutor-backend .
docker run -p 8000:8000 -e LLM_PROVIDER=openai tutor-backend
```

### Deploy Frontend to Vercel

```bash
cd frontend
vercel
```

Set environment variable:
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend-domain.com
```

---

## Troubleshooting

### Backend not responding
- Check: http://localhost:8000/api/health
- Ensure backend is running on correct port
- Check firewall/CORS settings

### Uploads exceeding timeout
- Increase timeout in `useTutorChat.ts`:
  ```typescript
  signal: AbortSignal.timeout(30000) // 30 seconds
  ```

### Queries returning mock answers
- Backend using mock LLM provider
- Set real API key: `export LLM_API_KEY=sk-...`

---

## Performance Tips

1. **Enable Caching:**
   ```typescript
   // Cache frequently asked questions
   const cache = new Map<string, QueryResponse>();
   ```

2. **Optimize Chunk Display:**
   - Don't fetch all retrieved chunks
   - Use pagination

3. **Batch Requests:**
   - Group multiple questions
   - Use request debouncing

---

## API Reference

See `backend/README.md` for complete API documentation.

Key endpoints for frontend:
- `POST /api/query/ask` - Ask question
- `GET /api/ingest/textbooks` - List textbooks
- `POST /api/ingest/textbook` - Upload textbook
- `GET /api/health` - Check backend status

---

**That's it! Your frontend is now connected to the intelligent backend.** 🚀
