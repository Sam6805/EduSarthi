"""Main FastAPI application."""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env FIRST before anything else reads env vars
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

# Support running with: python app/main.py
if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.utils.helpers import setup_logger
from app.api import routes_ingest, routes_query, routes_health

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI app."""
    logger.info("=== EduSarthi Backend Starting ===")
    logger.info(f"API Version: {API_VERSION}")

    # Log which LLM provider is active
    import os
    provider = os.getenv("LLM_PROVIDER", "claude")
    has_key   = bool(os.getenv("LLM_API_KEY") or os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))
    logger.info(f"LLM Provider : {provider}")
    logger.info(f"API Key set  : {has_key}")
    if not has_key:
        logger.warning("No API key found – using offline KB fallback")

    # Load vector index if it exists
    try:
        from app.core.query_handler import QueryHandler
        qh = QueryHandler()
        stats = qh.retriever.get_vector_store_stats()
        logger.info(f"Vector store : {stats['total_chunks']} chunks loaded")
    except Exception as e:
        logger.warning(f"Vector store not found (offline mode OK): {e}")

    yield

    logger.info("=== EduSarthi Backend Shutting Down ===")


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
)

# CORS – allow frontend on any port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(routes_ingest.router)
app.include_router(routes_query.router)
app.include_router(routes_health.router)


@app.get("/")
async def root():
    return {
        "title": API_TITLE,
        "version": API_VERSION,
        "endpoints": {
            "ingestion": "/api/ingest",
            "query": "/api/query",
            "health": "/api/health",
            "docs": "/docs",
        },
    }


@app.get("/api")
async def api_info():
    return {
        "title": API_TITLE,
        "version": API_VERSION,
        "available_endpoints": [
            "POST /api/ingest/textbook",
            "POST /api/ingest/demo-textbook",
            "GET  /api/ingest/textbooks",
            "POST /api/query/ask",
            "GET  /api/query/metrics",
            "GET  /api/query/vector-store-stats",
            "GET  /api/health",
            "GET  /api/health/status",
        ],
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
