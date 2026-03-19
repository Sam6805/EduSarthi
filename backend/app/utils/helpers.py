"""Utility functions for the backend."""

import json
import re
from typing import List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime

# ============= Token Counting =============
def estimate_tokens(text: str) -> int:
    """
    Estimate number of tokens using a simple heuristic.
    Typically: 1 token ≈ 4 characters (OpenAI approximation)
    """
    words = len(text.split())
    # Average word = 4 chars + 1 space
    chars = len(text)
    # Use word-based estimate as it's more reliable
    return int(words / 0.75)  # ~0.75 words per token average


def estimate_tokens_from_chunks(chunks: List[Dict[str, Any]]) -> int:
    """Estimate tokens from a list of chunk dictionaries."""
    total_text = " ".join([chunk.get("content", "") for chunk in chunks])
    return estimate_tokens(total_text)


# ============= Text Cleaning =============
def clean_text(text: str) -> str:
    """Clean extracted PDF text."""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that appear in PDFs
    text = text.replace('\x00', '')  # Null bytes
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# ============= File I/O =============
def save_json(data: Any, filepath: Path) -> None:
    """Save data to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def load_json(filepath: Path) -> Any:
    """Load data from JSON file."""
    if not filepath.exists():
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============= ID Generation =============
def generate_id(prefix: str = "") -> str:
    """Generate a unique ID based on timestamp."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id


# ============= Text Formatting =============
def format_answer(simple: str, detailed: str = None) -> Dict[str, str]:
    """Format answer for consistent output."""
    return {
        "simple_answer": simple.strip(),
        "detailed_answer": (detailed.strip() if detailed else None),
    }


# ============= Logging Setup =============
def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Set up a logger with consistent formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:  # Avoid duplicate handlers
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# ============= Metadata Helpers =============
def extract_chapter_number(chapter_title: str) -> int:
    """Extract chapter number from title (e.g., "Chapter 5: ..." -> 5)."""
    match = re.search(r'\b(\d+)\b', chapter_title)
    return int(match.group(1)) if match else 0


def format_metadata_text(metadata: Dict[str, Any]) -> str:
    """Format metadata as human-readable text."""
    parts = []
    if metadata.get("chapter_title"):
        parts.append(f"Chapter: {metadata['chapter_title']}")
    if metadata.get("section_title"):
        parts.append(f"Section: {metadata['section_title']}")
    if metadata.get("page_number"):
        parts.append(f"Page: {metadata['page_number']}")
    return " | ".join(parts) if parts else "No metadata"
