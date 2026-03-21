"""API routes for querying."""

from fastapi import APIRouter, HTTPException

from app.core.query_handler import QueryHandler
from app.schemas import QueryRequest
from app.utils.helpers import setup_logger

router = APIRouter(prefix="/api/query", tags=["query"])
logger = setup_logger(__name__)
query_handler = QueryHandler()


@router.post("/ask", response_model=dict)
async def ask_question(request: QueryRequest) -> dict:
    """
    Ask a question about textbook content.

    Works even when no PDFs have been ingested:
    - If FAISS index has chunks  → retrieve → prune → Claude/OpenAI/Gemini/Offline answer
    - If no chunks in index      → skip retrieval → Claude/OpenAI/Gemini/Offline answer
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        response = query_handler.handle_query(request)
        return response.dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/metrics", response_model=dict)
async def get_query_metrics():
    """Get aggregated metrics from all processed queries."""
    try:
        metrics = query_handler.get_metrics_summary()
        return {"status": "success", "metrics": metrics}
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector-store-stats", response_model=dict)
async def get_vector_store_statistics():
    """Get statistics about the vector store."""
    try:
        stats = query_handler.retriever.get_vector_store_stats()
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
