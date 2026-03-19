"""PDF extraction service for textbook processing."""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import re

try:
    import PyPDF2
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

from app.utils.helpers import clean_text, setup_logger
from app.config import EXTRACTED_TEXT_DIR

logger = setup_logger(__name__)


class PDFExtractor:
    """Extract and parse PDF documents."""
    
    def __init__(self):
        if not HAS_PYPDF:
            logger.warning("PyPDF2 not installed, using mock extraction")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract raw text from PDF file."""
        if not HAS_PYPDF:
            return self._extract_mock()
        
        text_parts = []
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"[Page {page_num + 1}]\n{text}")
            
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    def extract_text_with_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract text with page and structure information.
        Returns: {
            "raw_text": str,
            "pages": [{"page_num": int, "text": str}, ...],
            "page_count": int
        }
        """
        if not HAS_PYPDF:
            return self._extract_structure_mock()
        
        pages_data = []
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if text:
                        pages_data.append({
                            "page_num": page_num,
                            "text": clean_text(text),
                            "content_length": len(text)
                        })
            
            raw_text = "\n".join([p["text"] for p in pages_data])
            
            return {
                "raw_text": raw_text,
                "pages": pages_data,
                "page_count": len(pages_data),
                "total_chars": len(raw_text)
            }
        except Exception as e:
            logger.error(f"Error extracting PDF structure: {e}")
            raise
    
    def detect_chapters(self, text: str) -> List[Tuple[str, int]]:
        """
        Detect chapter boundaries in text.
        Returns: [(chapter_title, start_position), ...]
        Common patterns:
        - "Chapter 1: ..."
        - "Chapter 1. ..."
        - "CHAPTER 1 ..."
        """
        chapter_pattern = r'(?:^|\n)\s*Chapter\s+(\d+)\s*[:.]?\s*(.+?)(?=\n|$)'
        
        chapters = []
        for match in re.finditer(chapter_pattern, text, re.IGNORECASE | re.MULTILINE):
            chapter_num = match.group(1)
            chapter_title = match.group(2).strip()
            if not chapter_title:
                chapter_title = f"Chapter {chapter_num}"
            
            chapters.append((chapter_title, match.start()))
        
        if not chapters:
            logger.warning("No chapters detected, treating entire text as one chapter")
            chapters = [("Full Text", 0)]
        
        return chapters
    
    def segment_by_chapters(self, text: str) -> List[Dict[str, Any]]:
        """
        Segment text into chapters.
        Returns: [{"chapter_num": int, "chapter_title": str, "content": str}, ...]
        """
        chapters_info = self.detect_chapters(text)
        segments = []
        
        for i, (chapter_title, start_pos) in enumerate(chapters_info):
            # Determine end position
            if i < len(chapters_info) - 1:
                end_pos = chapters_info[i + 1][1]
            else:
                end_pos = len(text)
            
            content = text[start_pos:end_pos]
            
            # Extract chapter number if present
            match = re.search(r'\d+', chapter_title)
            chapter_num = int(match.group(0)) if match else i + 1
            
            segments.append({
                "chapter_num": chapter_num,
                "chapter_title": chapter_title,
                "content": content.strip(),
                "content_length": len(content),
                "start_position": start_pos,
                "end_position": end_pos
            })
        
        return segments
    
    def save_extracted_data(self, textbook_id: str, extracted: Dict[str, Any]) -> Path:
        """Save extracted data to JSON for reuse."""
        output_path = EXTRACTED_TEXT_DIR / f"{textbook_id}_extracted.json"
        
        # For JSON serialization, keep data serializable
        data_to_save = {
            "raw_text": extracted["raw_text"],
            "page_count": extracted["page_count"],
            "total_chars": extracted["total_chars"],
            "pages": [
                {
                    "page_num": p["page_num"],
                    "content_length": p["content_length"]
                } for p in extracted["pages"]
            ]
        }
        
        import json
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2)
        
        logger.info(f"Saved extracted data to {output_path}")
        return output_path
    
    def _extract_mock(self) -> str:
        """Mock extraction for demo purposes."""
        return """
        Class 6 Science Textbook
        
        Chapter 1: Food and Digestion
        
        Food is necessary for all living organisms. Plants make their own food through photosynthesis, 
        while animals obtain food by eating plants or other animals. Carbohydrates, proteins, fats, 
        vitamins and minerals are essential nutrients.
        
        The human digestive system consists of the mouth, esophagus, stomach, small intestine, and large intestine.
        
        Chapter 2: Materials and Their Properties
        
        Materials can be classified as natural or synthetic. Properties of materials include color, hardness,
        density, and solubility. Understanding material properties helps us choose the right material for 
        different applications.
        """
    
    def _extract_structure_mock(self) -> Dict[str, Any]:
        """Mock structured extraction for demo purposes."""
        raw = self._extract_mock()
        return {
            "raw_text": raw,
            "pages": [
                {"page_num": 1, "text": raw[:500], "content_length": 500},
                {"page_num": 2, "text": raw[500:], "content_length": len(raw) - 500}
            ],
            "page_count": 2,
            "total_chars": len(raw)
        }
