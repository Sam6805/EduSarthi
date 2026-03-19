"""Ingestion pipeline for processing textbooks."""

from pathlib import Path
from typing import Dict, Any
import json
import time

from app.services.pdf_extractor import PDFExtractor
from app.services.chunker import TextChunker
from app.services.embedder import EmbeddingGenerator
from app.services.vector_store import VectorStore
from app.utils.helpers import setup_logger, generate_id
from app.config import PROCESSED_CHUNKS_DIR

logger = setup_logger(__name__)


class IngestionPipeline:
    """Pipeline for ingesting and processing textbooks."""
    
    def __init__(self):
        self.extractor = PDFExtractor()
        self.chunker = TextChunker()
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.textbooks_metadata = {}  # Track ingested textbooks
    
    def process_pdf(self,
                   pdf_path: Path,
                   textbook_name: str,
                   class_level: str = None,
                   subject: str = None) -> Dict[str, Any]:
        """
        Process a PDF from upload to vector index.
        Returns ingestion summary.
        """
        pipeline_start = time.time()
        textbook_id = generate_id("textbook")
        
        logger.info(f"Starting ingestion: {textbook_name} (ID: {textbook_id})")
        
        try:
            # Step 1: Extract text with structure
            logger.info("Step 1: Extracting text from PDF...")
            extraction_start = time.time()
            extracted = self.extractor.extract_text_with_structure(pdf_path)
            extraction_time = time.time() - extraction_start
            logger.info(f"  Extracted {extracted['page_count']} pages in {extraction_time:.2f}s")
            
            # Step 2: Segment into chapters
            logger.info("Step 2: Segmenting into chapters...")
            chapters = self.extractor.segment_by_chapters(extracted["raw_text"])
            logger.info(f"  Found {len(chapters)} chapters")
            
            # Step 3: Chunk chapters
            logger.info("Step 3: Creating chunks...")
            chunking_start = time.time()
            chunks = self.chunker.chunk_chapters(chapters, textbook_name, textbook_id)
            chunking_time = time.time() - chunking_start
            logger.info(f"  Created {len(chunks)} chunks in {chunking_time:.2f}s")
            
            # Step 4: Generate embeddings
            logger.info("Step 4: Generating embeddings...")
            embedding_start = time.time()
            embeddings = self.embedder.embed_chunks(chunks)
            embedding_time = time.time() - embedding_start
            logger.info(f"  Generated {len(embeddings)} embeddings in {embedding_time:.2f}s")
            
            # Step 5: Index vectors
            logger.info("Step 5: Indexing vectors...")
            indexing_start = time.time()
            if not self.vector_store.index:
                self.vector_store.create_index(self.embedder.get_embedding_dim())
            self.vector_store.add_vectors(chunks, embeddings)
            indexing_time = time.time() - indexing_start
            logger.info(f"  Indexed vectors in {indexing_time:.2f}s")
            
            # Step 6: Save to disk
            logger.info("Step 6: Saving to disk...")
            save_start = time.time()
            self.vector_store.save_index()
            self.chunker.save_chunks_metadata(chunks, textbook_id)
            save_time = time.time() - save_start
            logger.info(f"  Saved to disk in {save_time:.2f}s")
            
            # Track metadata
            self.textbooks_metadata[textbook_id] = {
                "textbook_id": textbook_id,
                "textbook_name": textbook_name,
                "class_level": class_level,
                "subject": subject,
                "chapters": len(chapters),
                "chunks": len(chunks),
                "uploaded_at": time.time(),
                "file_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0
            }
            
            # Save metadata
            self._save_textbook_metadata()
            
            total_time = time.time() - pipeline_start
            
            result = {
                "status": "success",
                "textbook_id": textbook_id,
                "textbook_name": textbook_name,
                "chapters_extracted": len(chapters),
                "chunks_created": len(chunks),
                "embeddings_generated": len(embeddings),
                "total_time_seconds": round(total_time, 2),
                "timings": {
                    "extraction": round(extraction_time, 2),
                    "chunking": round(chunking_time, 2),
                    "embedding": round(embedding_time, 2),
                    "indexing": round(indexing_time, 2),
                    "saving": round(save_time, 2)
                }
            }
            
            logger.info(f"Ingestion completed in {total_time:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"Ingestion failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": str(e),
                "textbook_id": textbook_id
            }
    
    def process_demo_textbook(self) -> Dict[str, Any]:
        """
        Process a demo textbook without needing an actual PDF file.
        Useful for testing the pipeline.
        """
        textbook_id = generate_id("demo")
        textbook_name = "Demo Textbook - Class 6 Science"
        
        logger.info(f"Processing demo textbook: {textbook_name}")
        
        # Create demo chapters
        demo_text = """
        Chapter 1: Food and Digestion
        
        Food is one of the most essential things for all living organisms. Food provides energy 
        and materials for growth and repair of body parts. Different organisms need different kinds 
        of food. Plants make food using sunlight through photosynthesis. Animals must eat other 
        organisms for food.
        
        Chapter 2: Materials and Their Properties
        
        A material is a substance or mixture of substances from which something is made. All things 
        that we see around us are made of one or more materials. Materials can be classified as 
        natural or man-made. Natural materials are found in nature like wood, cotton, and stone. 
        Man-made or synthetic materials are made by humans like plastic and steel.
        
        Chapter 3: Living Organisms and Their Habitats
        
        A habitat is a place where an organism lives. Different organisms live in different habitats. 
        For example, fish live in water, birds live on land and in air, and snakes live in holes and 
        on the ground. Each organism is adapted to its habitat to obtain food, shelter, and other 
        necessities for survival.
        """
        
        # Segment into chapters
        chapters = self.extractor.segment_by_chapters(demo_text)
        
        # Create chunks
        chunks = self.chunker.chunk_chapters(chapters, textbook_name, textbook_id)
        
        # Generate embeddings
        embeddings = self.embedder.embed_chunks(chunks)
        
        # Index vectors
        if not self.vector_store.index:
            self.vector_store.create_index(self.embedder.get_embedding_dim())
        self.vector_store.add_vectors(chunks, embeddings)
        self.vector_store.save_index()
        self.chunker.save_chunks_metadata(chunks, textbook_id)
        
        # Track metadata
        self.textbooks_metadata[textbook_id] = {
            "textbook_id": textbook_id,
            "textbook_name": textbook_name,
            "class_level": "6",
            "subject": "Science",
            "chapters": len(chapters),
            "chunks": len(chunks),
            "uploaded_at": time.time()
        }
        
        self._save_textbook_metadata()
        
        return {
            "status": "success",
            "textbook_id": textbook_id,
            "textbook_name": textbook_name,
            "chapters_extracted": len(chapters),
            "chunks_created": len(chunks),
            "embeddings_generated": len(embeddings),
            "is_demo": True
        }
    
    def get_textbooks(self) -> Dict[str, Any]:
        """Get list of ingested textbooks."""
        return self.textbooks_metadata
    
    def _save_textbook_metadata(self) -> None:
        """Save textbook metadata to disk."""
        metadata_path = PROCESSED_CHUNKS_DIR / "textbooks_manifest.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.textbooks_metadata, f, indent=2, ensure_ascii=False, default=str)
