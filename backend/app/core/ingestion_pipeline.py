"""Ingestion pipeline + delete support."""

from pathlib import Path
from typing import Dict, Any, List
import json
import time
import shutil

from app.services.pdf_extractor import PDFExtractor
from app.services.chunker import TextChunker
from app.services.embedder import EmbeddingGenerator
from app.services.vector_store import VectorStore
from app.utils.helpers import setup_logger, generate_id
from app.config import PROCESSED_CHUNKS_DIR, VECTOR_INDEX_PATH, CHUNKS_METADATA_PATH

logger = setup_logger(__name__)

MANIFEST_PATH = PROCESSED_CHUNKS_DIR / "textbooks_manifest.json"


class IngestionPipeline:
    """Pipeline for ingesting, querying, and deleting textbooks."""

    def __init__(self):
        self.extractor = PDFExtractor()
        self.chunker = TextChunker()
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.textbooks_metadata: Dict[str, Any] = {}
        self._load_manifest()

    # ── Ingest ────────────────────────────────────────────────────────────
    def process_pdf(self, pdf_path: Path, textbook_name: str,
                    class_level: str = None, subject: str = None) -> Dict[str, Any]:
        pipeline_start = time.time()
        textbook_id = generate_id("textbook")
        logger.info(f"Ingesting: {textbook_name} (ID: {textbook_id})")

        try:
            # Step 1 – extract
            extracted = self.extractor.extract_text_with_structure(pdf_path)
            logger.info(f"  Extracted {extracted['page_count']} pages, {extracted['total_chars']} chars")

            if extracted["total_chars"] < 200:
                return {
                    "status": "error",
                    "message": (
                        "Could not extract text from this PDF. "
                        "It may be a scanned/image PDF. Please use a text-based PDF."
                    ),
                    "textbook_id": textbook_id,
                }

            # Step 2 – segment chapters
            chapters = self.extractor.segment_by_chapters(extracted["raw_text"])
            real_chapter_count = len(chapters)
            logger.info(f"  Found {real_chapter_count} chapter(s)")

            # Step 3 – chunk
            chunks = self.chunker.chunk_chapters(chapters, textbook_name, textbook_id)
            logger.info(f"  Created {len(chunks)} chunks")

            # Step 4 – embed
            embeddings = self.embedder.embed_chunks(chunks)

            # Step 5 – index
            if not self.vector_store.index:
                self.vector_store.create_index(self.embedder.get_embedding_dim())
            self.vector_store.add_vectors(chunks, embeddings)

            # Step 6 – save
            self.vector_store.save_index()
            self.chunker.save_chunks_metadata(chunks, textbook_id)

            total_time = time.time() - pipeline_start

            # Store metadata with REAL chapter count
            self.textbooks_metadata[textbook_id] = {
                "textbook_id": textbook_id,
                "textbook_name": textbook_name,
                "class_level": class_level or "Auto-detected",
                "subject": subject or "General",
                "chapters": real_chapter_count,       # ← real count
                "chunks": len(chunks),
                "uploaded_at": time.time(),
                "file_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
            }
            self._save_manifest()

            return {
                "status": "success",
                "textbook_id": textbook_id,
                "textbook_name": textbook_name,
                "chapters_extracted": real_chapter_count,
                "chunks_created": len(chunks),
                "embeddings_generated": len(embeddings),
                "total_time_seconds": round(total_time, 2),
            }

        except Exception as e:
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e), "textbook_id": textbook_id}

    # ── Delete ────────────────────────────────────────────────────────────
    def delete_textbook(self, textbook_id: str) -> Dict[str, Any]:
        """Remove a textbook from the manifest and rebuild the vector index."""
        if textbook_id not in self.textbooks_metadata:
            return {"status": "error", "message": f"Textbook {textbook_id} not found"}

        name = self.textbooks_metadata[textbook_id]["textbook_name"]
        logger.info(f"Deleting textbook: {name} ({textbook_id})")

        # Remove from manifest
        del self.textbooks_metadata[textbook_id]
        self._save_manifest()

        # Remove per-textbook chunk file
        chunk_file = PROCESSED_CHUNKS_DIR / f"{textbook_id}_chunks.json"
        if chunk_file.exists():
            chunk_file.unlink()

        # Rebuild vector store without deleted textbook's chunks
        self._rebuild_vector_store()

        return {"status": "success", "message": f"Deleted '{name}'", "textbook_id": textbook_id}

    def _rebuild_vector_store(self):
        """Rebuild FAISS index from all remaining textbooks."""
        logger.info("Rebuilding vector store after deletion...")

        # Wipe existing index + content
        self.vector_store = VectorStore.__new__(VectorStore)
        self.vector_store.index = None
        self.vector_store.chunk_metadata = {}
        self.vector_store.chunk_to_index = {}
        self.vector_store.index_to_chunk = {}
        self.vector_store.embedding_dim = None
        self.vector_store._full_content = {}
        self.vector_store.has_faiss = VectorStore().has_faiss

        remaining_ids = list(self.textbooks_metadata.keys())
        if not remaining_ids:
            # Save empty index
            self.vector_store.save_index()
            return

        # Re-ingest chunks from saved chunk files
        for tb_id in remaining_ids:
            chunk_file = PROCESSED_CHUNKS_DIR / f"{tb_id}_chunks.json"
            if not chunk_file.exists():
                continue
            try:
                with open(chunk_file, "r", encoding="utf-8") as f:
                    chunk_metas = json.load(f)
                # We need full content — get from current full_content store
                old_content_path = PROCESSED_CHUNKS_DIR / "chunks_full_content.json"
                full_content_map = {}
                if old_content_path.exists():
                    with open(old_content_path, "r", encoding="utf-8") as f:
                        full_content_map = json.load(f)

                chunks = []
                for meta in chunk_metas:
                    cid = meta["chunk_id"]
                    content = full_content_map.get(cid, meta.get("content_preview", ""))
                    chunks.append({**meta, "content": content, "content_length": len(content)})

                if chunks:
                    if not self.vector_store.index:
                        self.vector_store.create_index(self.embedder.get_embedding_dim())
                    embeddings = self.embedder.embed_chunks(chunks)
                    self.vector_store.add_vectors(chunks, embeddings)
            except Exception as e:
                logger.error(f"Error rebuilding chunks for {tb_id}: {e}")

        self.vector_store.save_index()
        logger.info("Vector store rebuilt successfully")

    # ── Demo ──────────────────────────────────────────────────────────────
    def process_demo_textbook(self) -> Dict[str, Any]:
        textbook_id = generate_id("demo")
        textbook_name = "Demo Textbook - Class 6 Science"
        demo_text = """
Chapter 1: Food and Digestion
Food is essential for all living organisms. Plants make food through photosynthesis.
Animals get food by eating plants or other animals. Carbohydrates, proteins, fats,
vitamins and minerals are essential nutrients. The human digestive system includes
the mouth, esophagus, stomach, small intestine, and large intestine.

Chapter 2: Materials and Their Properties
Materials can be natural or synthetic. Properties include color, hardness, density,
and solubility. Natural materials include wood, cotton, and stone. Man-made materials
include plastic and steel.
"""
        chapters = self.extractor.segment_by_chapters(demo_text)
        chunks = self.chunker.chunk_chapters(chapters, textbook_name, textbook_id)
        embeddings = self.embedder.embed_chunks(chunks)
        if not self.vector_store.index:
            self.vector_store.create_index(self.embedder.get_embedding_dim())
        self.vector_store.add_vectors(chunks, embeddings)
        self.vector_store.save_index()
        self.chunker.save_chunks_metadata(chunks, textbook_id)

        self.textbooks_metadata[textbook_id] = {
            "textbook_id": textbook_id,
            "textbook_name": textbook_name,
            "class_level": "6",
            "subject": "Science",
            "chapters": len(chapters),
            "chunks": len(chunks),
            "uploaded_at": time.time(),
        }
        self._save_manifest()
        return {
            "status": "success",
            "textbook_id": textbook_id,
            "textbook_name": textbook_name,
            "chapters_extracted": len(chapters),
            "chunks_created": len(chunks),
            "is_demo": True,
        }

    # ── Helpers ───────────────────────────────────────────────────────────
    def get_textbooks(self) -> Dict[str, Any]:
        return self.textbooks_metadata

    def _load_manifest(self):
        if MANIFEST_PATH.exists():
            try:
                with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                    self.textbooks_metadata = json.load(f)
                logger.info(f"Loaded {len(self.textbooks_metadata)} textbook(s) from manifest")
            except Exception as e:
                logger.warning(f"Could not load manifest: {e}")

    def _save_manifest(self):
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(self.textbooks_metadata, f, indent=2, ensure_ascii=False, default=str)
