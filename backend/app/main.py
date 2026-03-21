"""Main FastAPI application."""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Support running with: python app/main.py
if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.utils.helpers import setup_logger
from app.api import routes_ingest, routes_query, routes_health

logger = setup_logger(__name__)


# Initialize API
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI app."""
    logger.info("=== Education Tutor Backend Starting ===")
    logger.info(f"API Version: {API_VERSION}")
    logger.info("Initializing services...")
    
    # Load vector index if it exists
    try:
        from app.core.query_handler import QueryHandler
        qh = QueryHandler()
        stats = qh.retriever.get_vector_store_stats()
        logger.info(f"Vector store loaded: {stats['total_chunks']} chunks")
    except Exception as e:
        logger.warning(f"Vector store not found: {e}")
    
    yield
    
    logger.info("=== Education Tutor Backend Shutting Down ===")


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes_ingest.router)
app.include_router(routes_query.router)
app.include_router(routes_health.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "title": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "endpoints": {
            "ingestion": "/api/ingest",
            "query": "/api/query",
            "health": "/api/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "title": API_TITLE,
        "version": API_VERSION,
        "description": API_DESCRIPTION,
        "available_endpoints": [
            "POST /api/ingest/textbook - Upload and ingest a PDF textbook",
            "POST /api/ingest/demo-textbook - Ingest demo textbook",
            "GET /api/ingest/textbooks - List all textbooks",
            "POST /api/query/ask - Ask a question",
            "GET /api/query/metrics - Get query metrics",
            "GET /api/query/vector-store-stats - Get vector store statistics",
            "GET /api/health - Health check",
            "GET /api/health/status - Detailed status",
            "GET /docs - Swagger UI documentation",
            "GET /redoc - ReDoc documentation"
        ]
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
