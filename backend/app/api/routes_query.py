"""API routes for querying."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.core.query_handler import QueryHandler
from app.schemas import QueryRequest, QueryResponse
from app.utils.helpers import setup_logger

router = APIRouter(prefix="/api/query", tags=["query"])
logger = setup_logger(__name__)
query_handler = QueryHandler()


@router.post("/ask", response_model=dict)
async def ask_question(request: QueryRequest) -> dict:
    """
    Ask a question about textbook content.
    
    This endpoint:
    1. Retrieves relevant chunks from FAISS
    2. Reranks by relevance
    3. Prunes context to reduce tokens
    4. Generates student-friendly answer using LLM
    5. Returns detailed response with metrics
    
    Query parameters:
    - question: The student's question
    - textbook_id: (Optional) Specific textbook to search in
    - language: "en" or "hi"
    - use_pruning: Whether to apply context pruning (default: true)
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Check vector store is loaded
        stats = query_handler.retriever.get_vector_store_stats()
        if stats["total_chunks"] == 0:
            raise HTTPException(
                status_code=400,
                detail="No textbooks ingested yet. Please ingest a textbook first."
            )
        
        # Handle query
        response = query_handler.handle_query(request)
        
        return response.dict()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/metrics", response_model=dict)
async def get_query_metrics():
    """
    Get aggregated metrics from all processed queries.
    
    Returns:
    - total_queries: Number of queries processed
    - avg_retrieved_chunks: Average chunks retrieved
    - avg_pruned_chunks: Average chunks removed by pruning
    - avg_token_reduction_percentage: Average tokens saved
    - total_tokens_saved: Total tokens saved across all queries
    - recent_queries: Last 5 queries with detailed metrics
    """
    try:
        metrics = query_handler.get_metrics_summary()
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector-store-stats", response_model=dict)
async def get_vector_store_statistics():
    """
    Get statistics about the vector store (index size, chunks, etc.)
    """
    try:
        stats = query_handler.retriever.get_vector_store_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
