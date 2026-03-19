"""Text chunking service for creating retrievable chunks."""

from typing import List, Dict, Any
import json
from pathlib import Path

from app.config import (
    PDF_MIN_CHUNK_SIZE,
    PDF_MAX_CHUNK_SIZE,
    PDF_CHUNK_OVERLAP,
    PROCESSED_CHUNKS_DIR
)
from app.utils.helpers import setup_logger, generate_id

logger = setup_logger(__name__)


class TextChunker:
    """Split text into overlapping chunks while preserving metadata."""
    
    def __init__(self, 
                 min_chunk_size: int = PDF_MIN_CHUNK_SIZE,
                 max_chunk_size: int = PDF_MAX_CHUNK_SIZE,
                 overlap: int = PDF_CHUNK_OVERLAP):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_text(self, 
                   text: str, 
                   textbook_name: str,
                   textbook_id: str,
                   chapter_title: str = None,
                   chapter_number: int = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks.
        Returns list of chunk dicts with metadata.
        """
        chunks = []
        
        # Split by paragraphs first for better semantic boundaries
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds max size, save current chunk
            if current_chunk and len(current_chunk) + len(para) > self.max_chunk_size:
                chunks.append(self._create_chunk(
                    current_chunk,
                    textbook_id,
                    textbook_name,
                    chapter_number,
                    chapter_title,
                    chunk_index
                ))
                chunk_index += 1
                
                # Create overlap by including last part of previous chunk
                overlap_text = current_chunk[-self.overlap:] if len(current_chunk) > self.overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Don't forget the last chunk
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(self._create_chunk(
                current_chunk,
                textbook_id,
                textbook_name,
                chapter_number,
                chapter_title,
                chunk_index
            ))
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def chunk_chapters(self,
                      chapters_data: List[Dict[str, Any]],
                      textbook_name: str,
                      textbook_id: str) -> List[Dict[str, Any]]:
        """
        Chunk multiple chapters while preserving chapter metadata.
        chapters_data: [{"chapter_num": int, "chapter_title": str, "content": str}, ...]
        """
        all_chunks = []
        
        for chapter in chapters_data:
            chapter_chunks = self.chunk_text(
                text=chapter["content"],
                textbook_name=textbook_name,
                textbook_id=textbook_id,
                chapter_title=chapter["chapter_title"],
                chapter_number=chapter["chapter_num"]
            )
            all_chunks.extend(chapter_chunks)
        
        logger.info(f"Created {len(all_chunks)} total chunks from {len(chapters_data)} chapters")
        return all_chunks
    
    def _create_chunk(self,
                     content: str,
                     textbook_id: str,
                     textbook_name: str,
                     chapter_number: int = None,
                     chapter_title: str = None,
                     chunk_index: int = 0) -> Dict[str, Any]:
        """Create a single chunk with metadata."""
        return {
            "chunk_id": generate_id(f"{textbook_id}_ch{chapter_number}_chunk"),
            "textbook_id": textbook_id,
            "textbook_name": textbook_name,
            "chapter_number": chapter_number,
            "chapter_title": chapter_title,
            "section_title": None,  # Can be enhanced with section detection
            "page_number": None,  # Can be enhanced with OCR
            "chunk_index": chunk_index,
            "content": content.strip(),
            "content_length": len(content),
            "created_at": __import__('datetime').datetime.now().isoformat()
        }
    
    def save_chunks_metadata(self, 
                            chunks: List[Dict[str, Any]],
                            textbook_id: str) -> Path:
        """Save chunk metadata for later retrieval."""
        output_path = PROCESSED_CHUNKS_DIR / f"{textbook_id}_chunks.json"
        
        # Prepare metadata (don't store full content in metadata file)
        metadata_list = []
        for chunk in chunks:
            metadata_list.append({
                "chunk_id": chunk["chunk_id"],
                "textbook_id": chunk["textbook_id"],
                "textbook_name": chunk["textbook_name"],
                "chapter_number": chunk["chapter_number"],
                "chapter_title": chunk["chapter_title"],
                "content_length": chunk["content_length"],
                "content_preview": chunk["content"][:100] + "..."
            })
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(metadata_list)} chunk metadata to {output_path}")
        return output_path
