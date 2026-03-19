"""Configuration management for the Education Tutor backend."""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_PDFS_DIR = DATA_DIR / "raw_pdfs"
EXTRACTED_TEXT_DIR = DATA_DIR / "extracted_text"
PROCESSED_CHUNKS_DIR = DATA_DIR / "processed_chunks"
VECTOR_INDEX_DIR = DATA_DIR / "vector_index"

# Create directories if they don't exist
for directory in [RAW_PDFS_DIR, EXTRACTED_TEXT_DIR, PROCESSED_CHUNKS_DIR, VECTOR_INDEX_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# PDF Processing
PDF_MIN_CHUNK_SIZE = 300  # Minimum characters per chunk
PDF_MAX_CHUNK_SIZE = 1000  # Maximum characters per chunk
PDF_CHUNK_OVERLAP = 100  # Overlap between chunks for context

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight model
EMBEDDING_DIM = 384  # Dimension of embeddings

# Vector Store
VECTOR_STORE_TYPE = "faiss"  # Can be "faiss" or "chroma"
VECTOR_INDEX_PATH = VECTOR_INDEX_DIR / "textbook_index.faiss"
CHUNKS_METADATA_PATH = PROCESSED_CHUNKS_DIR / "chunks_metadata.json"

# Retrieval
TOP_K_CHUNKS = 10  # Initial retrieval count
SIMILARITY_THRESHOLD = 0.3  # Minimum similarity score

# Context Pruning
MAX_CONTEXT_TOKENS = 2000  # Maximum tokens to include in context
PRUNING_THRESHOLD = 0.5  # Relevance threshold for keeping chunks
MIN_CHUNKS_REQUIRED = 3  # Minimum chunks to include even if below threshold

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")  # "openai", "gemini", or "mock"
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 1000

# API Settings
API_TITLE = "Education Tutor Backend"
API_VERSION = "1.0.0"
API_DESCRIPTION = "AI tutoring system for students in rural India"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Demo mode (use mock data for testing without real PDFs)
DEMO_MODE = True
