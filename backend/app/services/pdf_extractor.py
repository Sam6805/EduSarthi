"""PDF extraction service.

Uses pdfplumber first (best for text PDFs), then PyPDF2 as fallback.
Both are already in requirements.txt.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

from app.utils.helpers import clean_text, setup_logger
from app.config import EXTRACTED_TEXT_DIR

logger = setup_logger(__name__)

# Try pdfplumber (better text extraction)
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    logger.warning("pdfplumber not installed")

# Try PyPDF2 as fallback
try:
    import PyPDF2
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    logger.warning("PyPDF2 not installed")


class PDFExtractor:
    """Extract and parse PDF documents."""

    # ── Public API ────────────────────────────────────────────────────────

    def extract_text_with_structure(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract text page-by-page from PDF.
        Returns:
            {
                "raw_text": str,
                "pages": [{"page_num": int, "text": str, "content_length": int}],
                "page_count": int,
                "total_chars": int,
            }
        """
        pages_data = []

        if HAS_PDFPLUMBER:
            pages_data = self._extract_pdfplumber(pdf_path)
        elif HAS_PYPDF:
            pages_data = self._extract_pypdf2(pdf_path)
        else:
            logger.error("No PDF library available! Install: pip install pdfplumber PyPDF2")
            pages_data = self._mock_pages()

        # If extraction yielded almost nothing, warn loudly
        total_chars = sum(p["content_length"] for p in pages_data)
        if total_chars < 500:
            logger.warning(
                f"Very little text extracted ({total_chars} chars). "
                "This PDF may be scanned/image-based. "
                "Install an OCR library or use a text-based PDF."
            )

        raw_text = "\n\n".join(p["text"] for p in pages_data if p["text"].strip())

        logger.info(f"Extracted {len(pages_data)} pages, {total_chars} chars total")
        return {
            "raw_text": raw_text,
            "pages": pages_data,
            "page_count": len(pages_data),
            "total_chars": total_chars,
        }

    def segment_by_chapters(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chapters.
        Tries multiple patterns; falls back to splitting by page/section breaks.
        """
        chapters_info = self._detect_chapters(text)

        segments = []
        for i, (chapter_title, start_pos) in enumerate(chapters_info):
            end_pos = chapters_info[i + 1][1] if i < len(chapters_info) - 1 else len(text)
            content = text[start_pos:end_pos].strip()

            match = re.search(r'\d+', chapter_title)
            chapter_num = int(match.group(0)) if match else i + 1

            if len(content) > 100:           # skip empty/tiny segments
                segments.append({
                    "chapter_num": chapter_num,
                    "chapter_title": chapter_title,
                    "content": content,
                    "content_length": len(content),
                    "start_position": start_pos,
                    "end_position": end_pos,
                })

        if not segments:
            # No chapters found — treat whole text as one block
            segments = [{
                "chapter_num": 1,
                "chapter_title": "Full Textbook",
                "content": text.strip(),
                "content_length": len(text),
                "start_position": 0,
                "end_position": len(text),
            }]

        logger.info(f"Segmented into {len(segments)} chapter(s)")
        return segments

    # ── Extraction backends ───────────────────────────────────────────────

    def _extract_pdfplumber(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text using pdfplumber (handles most text PDFs well)."""
        pages_data = []
        try:
            with pdfplumber.open(str(pdf_path)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    text = clean_text(text)
                    pages_data.append({
                        "page_num": page_num,
                        "text": text,
                        "content_length": len(text),
                    })
            logger.info(f"pdfplumber: extracted {len(pages_data)} pages")
        except Exception as e:
            logger.error(f"pdfplumber failed: {e} — trying PyPDF2")
            if HAS_PYPDF:
                pages_data = self._extract_pypdf2(pdf_path)
        return pages_data

    def _extract_pypdf2(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract text using PyPDF2 (fallback)."""
        pages_data = []
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text() or ""
                    text = clean_text(text)
                    pages_data.append({
                        "page_num": page_num,
                        "text": text,
                        "content_length": len(text),
                    })
            logger.info(f"PyPDF2: extracted {len(pages_data)} pages")
        except Exception as e:
            logger.error(f"PyPDF2 also failed: {e}")
        return pages_data

    def _mock_pages(self) -> List[Dict[str, Any]]:
        """Return demo content when no PDF library is available."""
        demo = (
            "Chapter 1: Matter\n\nMatter is anything that has mass and occupies space. "
            "All substances around us are made of matter. Matter exists in three states: "
            "solid, liquid, and gas.\n\n"
            "Chapter 2: Force and Motion\n\nForce is a push or pull. Newton's laws describe "
            "how forces affect motion of objects."
        )
        return [{"page_num": 1, "text": demo, "content_length": len(demo)}]

    # ── Chapter detection ─────────────────────────────────────────────────

    def _detect_chapters(self, text: str) -> List[Tuple[str, int]]:
        """Detect chapter boundaries using multiple regex patterns."""
        patterns = [
            r'(?:^|\n)\s*(Chapter\s+\d+\s*[:.]\s*[^\n]+)',          # Chapter 1: Title
            r'(?:^|\n)\s*(CHAPTER\s+\d+\s*[:.]\s*[^\n]+)',          # CHAPTER 1: Title
            r'(?:^|\n)\s*(Unit\s+\d+\s*[:.]\s*[^\n]+)',             # Unit 1: Title
            r'(?:^|\n)\s*(\d+\.\s+[A-Z][^\n]{5,60})',               # 1. TITLE
        ]

        all_matches = []
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.MULTILINE):
                all_matches.append((m.group(1).strip(), m.start()))

        # Sort by position and remove duplicates that are too close
        all_matches.sort(key=lambda x: x[1])
        chapters = []
        last_pos = -500
        for title, pos in all_matches:
            if pos - last_pos > 300:   # at least 300 chars between chapters
                chapters.append((title, pos))
                last_pos = pos

        if not chapters:
            # Fallback: split every ~3000 chars as a "section"
            chapters = self._split_into_sections(text, section_size=3000)

        return chapters if chapters else [("Full Text", 0)]

    def _split_into_sections(self, text: str, section_size: int = 3000) -> List[Tuple[str, int]]:
        """Divide long text into fixed-size sections when no chapters detected."""
        sections = []
        pos = 0
        sec_num = 1
        while pos < len(text):
            sections.append((f"Section {sec_num}", pos))
            pos += section_size
            sec_num += 1
        return sections
