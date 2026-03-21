# EduSarthi - Branch README (README1)

This file documents the **current branch implementation** and is intentionally different from the main branch README.

## What Is Different From Main Branch

Main branch README focuses primarily on frontend. This branch includes:

- Full backend service using FastAPI
- PDF ingestion and chunking pipeline
- Vector search with FAISS
- Retrieval + context pruning for answers
- Frontend integration with backend APIs
- Dynamic sample questions by textbook
- Uploaded file behavior (no static samples)

## Project Overview

EduSarthi is an AI tutoring platform designed for students, including low-bandwidth scenarios.

- Frontend: Next.js + TypeScript + Tailwind
- Backend: FastAPI (Python)
- Retrieval: Embeddings + FAISS vector index
- Features: Upload textbook PDFs, ask questions, receive contextual answers, language toggle support

## Repository Structure

- `frontend/` Next.js application
- `backend/` FastAPI APIs and ingestion/query pipeline
- `PDF_INGESTION_GUIDE.md` setup for PDF-based answer extraction
- `STATUS_REPORT.md` branch status and feature progress

## Backend APIs (High Level)

- Health check endpoint
- Textbook/PDF ingest endpoint
- Query endpoint for question answering

Core backend modules:

- `backend/app/core/ingestion_pipeline.py`
- `backend/app/core/query_handler.py`
- `backend/app/services/vector_store.py`
- `backend/app/services/retriever.py`
- `backend/app/services/chunker.py`

## Run Instructions

### 1) Start Backend

From `backend/`:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 2) Start Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`, backend at `http://localhost:8000`.

## Current Branch Behavior

- For default textbooks: sample questions are shown and vary by selected textbook.
- For uploaded textbooks: static sample suggestions are hidden; user is prompted to ask directly from the uploaded file.
- If backend is unavailable: frontend falls back to mock answers.
- If backend is running and ingestion completes: answers come from indexed PDF content.

## Suggested Validation Flow

1. Start backend server.
2. Start frontend server.
3. Upload a PDF from Upload page.
4. Open Tutor page and select uploaded file.
5. Ask specific questions from uploaded content.
6. Verify answers reflect uploaded material.

## Notes

- This README1 is branch-specific documentation.
- Keep root `README.md` as baseline/main-branch style documentation.
