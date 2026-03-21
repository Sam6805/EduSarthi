"""API routes for health checks, system status, and LLM diagnostics."""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import platform
import json
import urllib.request
import urllib.error
import os

from app.config import API_VERSION, LLM_API_KEY, LLM_MODEL
from app.utils.helpers import setup_logger
from app.core.query_handler import QueryHandler

router = APIRouter(prefix="/api/health", tags=["health"])
logger = setup_logger(__name__)
query_handler = QueryHandler()


@router.get("")
async def health_check() -> dict:
    try:
        components = {}
        try:
            stats = query_handler.retriever.get_vector_store_stats()
            components["vector_store"] = "ready" if stats["total_chunks"] > 0 else "empty"
        except:
            components["vector_store"] = "error"

        try:
            llm_info = query_handler.generator.get_info()
            components["llm"] = llm_info.get("primary_provider", "unknown")
        except:
            components["llm"] = "error"

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION,
            "components": components,
            "environment": platform.system(),
        }
    except Exception as e:
        return {"status": "unhealthy", "timestamp": datetime.now().isoformat(),
                "version": API_VERSION, "error": str(e)}


@router.get("/status")
async def detailed_status() -> dict:
    try:
        stats = query_handler.retriever.get_vector_store_stats()
        metrics = query_handler.get_metrics_summary()
        llm_info = query_handler.generator.get_info()
        return {"status": "healthy", "timestamp": datetime.now().isoformat(),
                "version": API_VERSION, "vector_store": stats,
                "metrics": metrics, "llm": llm_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-gemini")
async def test_gemini() -> dict:
    """Test Gemini API directly — helps diagnose connection issues."""
    api_key = os.getenv("LLM_API_KEY", LLM_API_KEY)
    model   = os.getenv("LLM_MODEL", LLM_MODEL) or "gemini-1.5-flash"

    if not api_key:
        return {"status": "error", "reason": "LLM_API_KEY not set in .env"}

    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent?key={api_key}")

    payload = json.dumps({
        "contents": [{"parts": [{"text": "Say hello in one word."}]}],
        "generationConfig": {"maxOutputTokens": 10},
    }).encode("utf-8")

    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"status": "ok", "model": model, "response": text,
                "api_key_prefix": api_key[:8] + "..."}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"status": "error", "http_code": e.code,
                "reason": body[:300], "model": model,
                "api_key_prefix": api_key[:8] + "..."}
    except Exception as e:
        return {"status": "error", "reason": str(e), "model": model}
