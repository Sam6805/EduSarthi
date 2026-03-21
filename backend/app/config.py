"""Configuration management for the EduSarthi backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env (safe to call multiple times)
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# ── Base paths ────────────────────────────────────────────
PROJECT_ROOT        = Path(__file__).parent.parent
DATA_DIR            = PROJECT_ROOT / "data"
RAW_PDFS_DIR        = DATA_DIR / "raw_pdfs"
EXTRACTED_TEXT_DIR  = DATA_DIR / "extracted_text"
PROCESSED_CHUNKS_DIR= DATA_DIR / "processed_chunks"
VECTOR_INDEX_DIR    = DATA_DIR / "vector_index"

for directory in [RAW_PDFS_DIR, EXTRACTED_TEXT_DIR, PROCESSED_CHUNKS_DIR, VECTOR_INDEX_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ── PDF Processing ────────────────────────────────────────
PDF_MIN_CHUNK_SIZE  = 300
PDF_MAX_CHUNK_SIZE  = 1000
PDF_CHUNK_OVERLAP   = 100

# ── Embedding Model ───────────────────────────────────────
EMBEDDING_MODEL     = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM       = 384

# ── Vector Store ──────────────────────────────────────────
VECTOR_STORE_TYPE   = "faiss"
VECTOR_INDEX_PATH   = VECTOR_INDEX_DIR / "textbook_index.faiss"
CHUNKS_METADATA_PATH= PROCESSED_CHUNKS_DIR / "chunks_metadata.json"

# ── Retrieval ─────────────────────────────────────────────
TOP_K_CHUNKS        = 10
SIMILARITY_THRESHOLD= 0.3

# ── Context Pruning (key innovation) ─────────────────────
MAX_CONTEXT_TOKENS  = 2000
PRUNING_THRESHOLD   = 0.5
MIN_CHUNKS_REQUIRED = 3

# ── LLM Configuration ─────────────────────────────────────
# Priority: Gemini → Claude → OpenAI → Offline KB
#
# Your .env has:
#   LLM_PROVIDER=gemini
#   LLM_API_KEY=AIzaSy...
#   LLM_MODEL=gemini-pro

CLAUDE_API_KEY  = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY", "")
LLM_PROVIDER    = os.getenv("LLM_PROVIDER", "gemini")
LLM_API_KEY     = os.getenv("LLM_API_KEY", "")
LLM_MODEL       = os.getenv("LLM_MODEL", "gemini-pro")
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS  = 600

# ── API Settings ──────────────────────────────────────────
API_TITLE       = "EduSarthi Backend"
API_VERSION     = "1.1.0"
API_DESCRIPTION = "AI tutoring for students in rural India – works online & offline"

# ── Logging ───────────────────────────────────────────────
LOG_LEVEL       = os.getenv("LOG_LEVEL", "INFO")

DEMO_MODE       = True
