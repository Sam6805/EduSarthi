"""API routes for ingestion."""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import tempfile
from pathlib import Path
import os

from app.core.ingestion_pipeline import IngestionPipeline
from app.schemas import IngestionResponse, TextbookResponse
from app.utils.helpers import setup_logger

router = APIRouter(prefix="/api/ingest", tags=["ingestion"])
logger = setup_logger(__name__)
ingestion = IngestionPipeline()


@router.post("/textbook", response_model=dict)
async def ingest_textbook(
    file: UploadFile = File(...),
    textbook_name: str = Form(...),
    class_level: str = Form(None),
    subject: str = Form(None)
):
    """
    Upload and ingest a textbook PDF.
    
    This endpoint:
    1. Accepts a PDF file
    2. Extracts text and chapters
    3. Creates chunks with overlapping
    4. Generates embeddings
    5. Indexes in FAISS
    6. Returns ingestion summary
    """
    try:
        # Validate file
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        # Process PDF
        try:
            result = ingestion.process_pdf(
                pdf_path=tmp_path,
                textbook_name=textbook_name,
                class_level=class_level,
                subject=subject
            )
            return result
        finally:
            # Clean up temp file
            if tmp_path.exists():
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.post("/demo-textbook")
async def ingest_demo_textbook():
    """
    Ingest a demo textbook for testing without uploading a PDF.
    Useful for hackathon demos.
    """
    try:
        result = ingestion.process_demo_textbook()
        return result
    except Exception as e:
        logger.error(f"Demo ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/textbooks", response_model=dict)
async def list_textbooks():
    """
    List all ingested textbooks.
    """
    try:
        textbooks = ingestion.get_textbooks()
        return {
            "total_textbooks": len(textbooks),
            "textbooks": list(textbooks.values())
        }
    except Exception as e:
        logger.error(f"Error listing textbooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))
