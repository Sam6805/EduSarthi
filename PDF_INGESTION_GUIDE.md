# PDF-Based Answer Extraction - Complete Setup Guide

## Current Status

✅ **Frontend Changes Implemented:**
- Sample questions now change based on selected textbook
- Sample questions hidden for uploaded files
- Backend API properly integrated
- Language translation working (English ↔ Hindi)

❌ **Missing Component:**
- Backend server not running
- PDFs not being ingested into vector index
- Answers still coming from mock data instead of PDF content

## The Problem You're Experiencing

When you upload a PDF (like "eesa103"), the frontend:
1. ✅ Detects it in the textbook selector  
2. ✅ Allows you to select it
3. ❌ **BUT** the answers don't come from the PDF because:
   - Backend is not running
   - PDF is not indexed in FAISS
   - System falls back to generic mock answers

## How to Fix This: Step-by-Step

### Step 1: Set Up Backend Python Environment

```bash
cd "e:\sam\gen ai for genz\educatioanl tutor\backend"

# Install dependencies
pip install fastapi uvicorn pydantic PyPDF2 pdfplumber sentence-transformers python-multipart python-dotenv

# For FAISS (vector store), try installing pre-built wheel
pip install --only-binary :all: faiss-cpu
```

If FAISS installation fails, try:
```bash
pip install faiss-cpu==1.7.4.post1
# Or use the latest version
pip install faiss-cpu --upgrade
```

### Step 2: Start the Backend Server

```bash
cd "e:\sam\gen ai for genz\educatioanl tutor\backend"

# Run the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 3: Upload and Ingest PDFs

Once backend is running, when you upload a PDF:

1. **Frontend uploads to backend**: `POST /api/ingest/textbook`
2. **Backend processes**: Extracts text, creates chunks, generates embeddings
3. **Backend indexes**: Stores in FAISS vector index
4. **Backend saves**: Metadata saved for retrieval

The file "eesa103" will be indexed with its chapters and content.

### Step 4: Ask Questions from Uploaded Files

When you select "eesa103" and ask a question:

**Flow:**
```
User Question
    ↓
Frontend sends to Backend (with textbook_id="eesa103")
    ↓
Backend retrieves from FAISS index for "eesa103"
    ↓
Context pruning (keeps most relevant chunks)
    ↓
LLM generates answer from extracted context
    ↓
Answer translated to Hindi if requested
    ↓
User sees PDF-based answer
```

## Current Frontend Implementation

### Dynamic Sample Questions

**For default textbooks (e.g., Class 6 Science):**
```
- Explain photosynthesis in simple words
- What are the parts of a plant and their functions?
- How do plants absorb water?
[Shows suggestions]
```

**For uploaded files (e.g., eesa103):**
```
"You have selected an uploaded textbook. Ask me anything from it, 
and I'll find answers directly from your file."
[No suggestions - answers come from file]
```

### Code Changes Made

1. **`frontend/constants/sampleQuestions.ts`**
   - Added `getSampleQuestionsForTextbook()` function
   - Database of questions per subject

2. **`frontend/app/tutor/page.tsx`**
   - Detects if selected textbook is uploaded: `isUploadedFile = selectedTextbook.startsWith('uploaded-')`
   - Shows different UI for uploaded files
   - Passes correct sample questions

3. **`frontend/lib/mockApi.ts`**
   - Improved backend API calls
   - Sends `textbook_id` to backend
   - Better error logging with `[API]`, `[FALLBACK]` prefixes
   - Falls back to mock answers if backend unavailable

## Testing Checklist

When backend is running:

- [ ] Upload a PDF from your computer
- [ ] Go to tutor page
- [ ] Select the uploaded PDF from dropdown
- [ ] Verify sample questions are NOT shown (says "Ask me anything from it")
- [ ] Ask a question from the PDF content
- [ ] Answer comes from PDF (not generic defaults)
- [ ] Switch language to Hindi
- [ ] Answer appears in Hindi

When backend is NOT running:

- [ ] Select uploaded PDF
- [ ] Ask a question
- [ ] See fallback generic answer (but in selected language)
- [ ] Check browser console for: `[FALLBACK] Using mock answers`

## Files Modified

```
frontend/
├── constants/sampleQuestions.ts    [NEW: Dynamic questions]
├── app/tutor/page.tsx              [UPDATED: Show/hide samples]
├── lib/mockApi.ts                  [UPDATED: Better API handling]
└── components/tutor/TextbookSelector.tsx  [OK: Already supports uploads]

backend/
└── app.main.py, core/, services/   [Ready to use when running]
```

## Environment Variables

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend (.env):**
```
LLM_PROVIDER=mock              # or "openai", "gemini"
LLM_API_KEY=                   # Only if using real LLM
DEMO_MODE=True                 # Use mock embeddings if no GPU
```

## Troubleshooting

### Backend won't start
```
Error: "ModuleNotFoundError: No module named 'fastapi'"
→ Solution: pip install fastapi uvicorn
```

### FAISS installation fails
```
Error: "Could not find a version that satisfies the requirement faiss-cpu==1.7.4"
→ Solution: pip install --upgrade faiss-cpu
```

### PDF not indexing
```
Check backend logs for:
- PDF extraction errors
- Chunk creation errors  
- Embedding generation issues

Admin endpoint: http://localhost:8000/docs
```

### Answers still generic after upload
```
1. Check backend is running (http://localhost:8000/docs should load)
2. Check browser console for "[API]" vs "[FALLBACK]" messages
3. Verify PDF uploaded successfully (check backend logs)
4. Try asking a very specific question from PDF
```

## Next Features to Add

1. **Real LLM Support**: Replace mock LLM with OpenAI/Gemini
2. **Progress Indicator**: Show PDF processing status
3. **Multi-PDF Search**: Search across multiple uploaded files
4. **Export Answers**: Save QA pairs for revision
5. **Detailed Metrics**: Show token reduction, retrieval score

---

**Current Version**: Frontend Ready ✅ | Backend Ready (not running) ⏸️

Connect backend, ingest PDFs, and you'll have a fully functional AI tutor! 🎓
