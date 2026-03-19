"""API routes for health checks and system status."""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import platform

from app.config import API_VERSION
from app.utils.helpers import setup_logger
from app.core.query_handler import QueryHandler

router = APIRouter(prefix="/api/health", tags=["health"])
logger = setup_logger(__name__)
query_handler = QueryHandler()


@router.get("")
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns:
    - status: "healthy" or "unhealthy"
    - timestamp: Current server time
    - version: API version
    - components: Status of individual components
    """
    try:
        components = {}
        
        # Check vector store
        try:
            stats = query_handler.retriever.get_vector_store_stats()
            components["vector_store"] = "ready" if stats["total_chunks"] > 0 else "empty"
        except:
            components["vector_store"] = "error"
        
        # Check LLM
        try:
            llm_info = query_handler.generator.get_info()
            components["llm"] = f"{llm_info['provider']}" if llm_info['has_api_key'] else "mock"
        except:
            components["llm"] = "error"
        
        # Overall status
        overall_status = "healthy" if all(v != "error" for v in components.values()) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION,
            "components": components,
            "environment": platform.system()
        }
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION,
            "error": str(e)
        }


@router.get("/status")
async def detailed_status() -> dict:
    """
    Get detailed system status including metrics and configuration.
    """
    try:
        stats = query_handler.retriever.get_vector_store_stats()
        metrics = query_handler.get_metrics_summary()
        llm_info = query_handler.generator.get_info()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION,
            "vector_store": stats,
            "metrics": metrics,
            "llm": llm_info
        }
    
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
