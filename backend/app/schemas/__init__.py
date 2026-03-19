"""Pydantic schemas for request/response models."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============= Textbook Schemas =============
class TextbookMetadata(BaseModel):
    """Metadata for a textbook."""
    textbook_id: str
    textbook_name: str
    class_level: Optional[str] = None  # e.g., "Class 6", "Class 8"
    subject: Optional[str] = None  # e.g., "Science", "Mathematics"
    chapters: Optional[int] = 0
    uploaded_at: Optional[datetime] = None


class TextbookResponse(BaseModel):
    """Response when listing textbooks."""
    textbook_id: str
    textbook_name: str
    class_level: Optional[str] = None
    subject: Optional[str] = None
    total_chapters: int
    total_chunks: int
    uploaded_at: datetime
    file_size_mb: Optional[float] = None


# ============= Chunk Schemas =============
class ChunkMetadata(BaseModel):
    """Metadata for a text chunk."""
    chunk_id: str
    textbook_id: str
    textbook_name: str
    chapter_number: Optional[int] = None
    chapter_title: Optional[str] = None
    section_title: Optional[str] = None
    page_number: Optional[int] = None
    content_preview: str
    content_length: int


class RetrievedChunk(BaseModel):
    """A retrieved and ranked chunk."""
    chunk_id: str
    textbook_name: str
    chapter_title: Optional[str] = None
    page_number: Optional[int] = None
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    is_pruned: bool = False


# ============= Query/Answer Schemas =============
class QueryRequest(BaseModel):
    """Request to ask a question about textbooks."""
    question: str
    textbook_id: Optional[str] = None  # If specified, search only in this textbook
    language: str = "en"  # "en" or "hi"
    use_pruning: bool = True  # Whether to apply context pruning


class GeneratedAnswer(BaseModel):
    """Generated answer from the LLM."""
    simple_answer: str  # Student-friendly explanation
    detailed_answer: Optional[str] = None  # Detailed explanation if needed
    source_chapter: Optional[str] = None
    source_pages: List[int] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """Complete response to a student question."""
    question: str
    answer: GeneratedAnswer
    
    # Retrieval metrics
    retrieved_chunks_count: int
    retrieved_chunks: List[RetrievedChunk]
    
    # Pruning metrics
    pruned_chunks_count: int
    pruning_applied: bool
    
    # Token usage estimates
    token_estimate_before_pruning: int
    token_estimate_after_pruning: int
    token_reduction_percentage: float
    
    # Latency estimates
    retrieval_latency_ms: float
    pruning_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
    
    # Debug info
    textbook_used: str


# ============= Ingestion Schemas =============
class IngestionRequest(BaseModel):
    """Request to ingest a textbook PDF."""
    textbook_name: str
    class_level: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None


class IngestionResponse(BaseModel):
    """Response after ingesting a textbook."""
    textbook_id: str
    textbook_name: str
    status: str  # "success" or "error"
    message: str
    chapters_extracted: int
    chunks_created: int
    embeddings_generated: int


# ============= Metrics Schemas =============
class PipelineMetrics(BaseModel):
    """Metrics for a single pipeline execution."""
    retrieved_chunks: int
    pruned_chunks: int
    prompt_tokens_baseline: int
    prompt_tokens_pruned: int
    token_reduction_percentage: float
    latency_ms: float


class MetricsResponse(BaseModel):
    """Overall metrics and comparison."""
    total_textbooks: int
    total_chunks: int
    total_questions_processed: int
    
    # Aggregated metrics
    avg_retrieved_chunks: float
    avg_pruned_chunks: float
    avg_token_reduction_percentage: float
    total_tokens_saved: int
    
    # Sample recent metrics
    recent_queries: List[Dict[str, Any]] = Field(default_factory=list)


# ============= Health Check Schemas =============
class HealthResponse(BaseModel):
    """Health check response."""
    status: str  # "healthy" or "unhealthy"
    timestamp: datetime
    version: str
    components: Dict[str, str]  # e.g., {"vector_store": "ready", "llm": "connected"}
