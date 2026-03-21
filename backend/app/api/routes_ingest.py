"""API routes for PDF ingestion + deletion."""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
import tempfile
from pathlib import Path
import os

from app.core.ingestion_pipeline import IngestionPipeline
from app.utils.helpers import setup_logger

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])
logger = setup_logger(__name__)
ingestion = IngestionPipeline()


@router.post("/textbook", response_model=dict)
async def ingest_textbook(
    file: UploadFile = File(...),
    textbook_name: str = Form(None),
    class_level: str = Form(None),
    subject: str = Form(None),
):
    """Upload and ingest a PDF textbook."""
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        name = textbook_name or file.filename.replace(".pdf", "").replace("_", " ").replace("-", " ")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            result = ingestion.process_pdf(
                pdf_path=tmp_path,
                textbook_name=name,
                class_level=class_level,
                subject=subject,
            )
            logger.info(f"Ingestion: {result.get('status')} – {result.get('chunks_created', 0)} chunks, {result.get('chapters_extracted', 0)} chapters")
            return result
        finally:
            if tmp_path.exists():
                os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/upload", response_model=dict)
async def upload_textbook(
    file: UploadFile = File(...),
    textbook_name: str = Form(None),
    class_level: str = Form(None),
    subject: str = Form(None),
):
    """Alias for /textbook – frontend calls /api/ingest/upload."""
    return await ingest_textbook(
        file=file, textbook_name=textbook_name,
        class_level=class_level, subject=subject
    )


@router.delete("/textbook/{textbook_id}", response_model=dict)
async def delete_textbook(textbook_id: str):
    """Delete an uploaded textbook and remove it from the vector index."""
    try:
        result = ingestion.delete_textbook(textbook_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demo-textbook")
async def ingest_demo_textbook():
    """Ingest a built-in demo textbook."""
    try:
        return ingestion.process_demo_textbook()
    except Exception as e:
        logger.error(f"Demo ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/textbooks", response_model=dict)
async def list_textbooks():
    """List all ingested textbooks with real chapter counts."""
    try:
        textbooks = ingestion.get_textbooks()
        return {
            "total_textbooks": len(textbooks),
            "textbooks": list(textbooks.values()),
        }
    except Exception as e:
        logger.error(f"Error listing textbooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
