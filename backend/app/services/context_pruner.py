"""Context pruning service to reduce token usage while maintaining relevance."""

from typing import List, Dict, Any, Tuple
import re

from app.utils.helpers import estimate_tokens, setup_logger
from app.config import (
    MAX_CONTEXT_TOKENS,
    PRUNING_THRESHOLD,
    MIN_CHUNKS_REQUIRED
)

logger = setup_logger(__name__)


class ContextPruner:
    """Prune retrieved chunks to reduce token usage while maintaining answer quality."""
    
    def __init__(self,
                 max_tokens: int = MAX_CONTEXT_TOKENS,
                 relevance_threshold: float = PRUNING_THRESHOLD,
                 min_chunks: int = MIN_CHUNKS_REQUIRED):
        self.max_tokens = max_tokens
        self.relevance_threshold = relevance_threshold
        self.min_chunks = min_chunks
    
    def prune_chunks(self,
                     chunks_with_scores: List[Dict[str, Any]],
                     question: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Prune chunks based on multiple strategies.
        
        Returns:
            - pruned_chunks: List of chunks to include
            - metrics: Dict with pruning statistics
        """
        if not chunks_with_scores:
            return [], {"strategy": "none", "chunks_kept": 0, "tokens_before": 0, "tokens_after": 0}
        
        # Strategy 1: Filter by relevance threshold
        threshold_passing = [
            c for c in chunks_with_scores 
            if c.get("relevance_score", 0) >= self.relevance_threshold
        ]
        
        # Ensure minimum chunks
        if len(threshold_passing) < self.min_chunks:
            threshold_passing = chunks_with_scores[:self.min_chunks]
        
        # Strategy 2: Token budget enforcement
        final_chunks = []
        current_tokens = 0
        
        for chunk in threshold_passing:
            chunk_tokens = estimate_tokens(chunk.get("content", ""))
            
            if current_tokens + chunk_tokens <= self.max_tokens:
                final_chunks.append(chunk)
                current_tokens += chunk_tokens
            elif len(final_chunks) < self.min_chunks:
                # Force include even if over budget (maintain minimum quality)
                final_chunks.append(chunk)
                current_tokens += chunk_tokens
            else:
                break
        
        # Calculate metrics
        tokens_before = sum(estimate_tokens(c.get("content", "")) for c in chunks_with_scores)
        tokens_after = current_tokens
        
        metrics = {
            "strategy": "relevance_and_tokens",
            "chunks_retrieved": len(chunks_with_scores),
            "chunks_after_threshold": len(threshold_passing),
            "chunks_kept": len(final_chunks),
            "chunks_pruned": len(chunks_with_scores) - len(final_chunks),
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "token_reduction": tokens_before - tokens_after,
            "reduction_percentage": (1 - tokens_after / tokens_before * 100) if tokens_before > 0 else 0
        }
        
        logger.info(f"Pruning: {metrics['chunks_retrieved']} → {metrics['chunks_kept']} chunks, "
                   f"tokens: {metrics['tokens_before']} → {metrics['tokens_after']}")
        
        return final_chunks, metrics
    
    def rerank_by_relevance(self,
                           chunks: List[Dict[str, Any]],
                           question: str) -> List[Dict[str, Any]]:
        """
        Rerank chunks by relevance to the question.
        Uses keyword matching and section proximity.
        """
        # Extract question keywords
        question_keywords = self._extract_keywords(question)
        
        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            score = self._calculate_relevance_score(
                chunk.get("content", ""),
                chunk.get("chapter_title", ""),
                question_keywords
            )
            chunk["relevance_score"] = score
            scored_chunks.append(chunk)
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_chunks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text (simple tokenization)."""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text).lower()
        words = text.split()
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'and', 'or', 'of', 'to', 'in', 'for', 'what', 'how', 'why'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
    
    def _calculate_relevance_score(self,
                                  chunk_content: str,
                                  chapter_title: str,
                                  keywords: List[str]) -> float:
        """
        Calculate relevance score for a chunk.
        Considers: keyword presence, chapter title match, content density
        """
        score = 0.0
        
        # Keyword matching (0-0.6)
        content_lower = chunk_content.lower()
        chapter_lower = (chapter_title or "").lower()
        
        keyword_matches = sum(1 for kw in keywords if kw in content_lower)
        keyword_score = min(keyword_matches / len(keywords), 1.0) * 0.6 if keywords else 0.3
        score += keyword_score
        
        # Chapter relevance (0-0.2)
        chapter_match_score = 0.2 if any(kw in chapter_lower for kw in keywords) else 0.0
        score += chapter_match_score
        
        # Content quality (0-0.2) - prefer longer, more detailed chunks
        content_length = len(chunk_content)
        if content_length > 1000:
            score += 0.2
        elif content_length > 500:
            score += 0.15
        elif content_length > 300:
            score += 0.1
        
        return min(score, 1.0)
    
    def build_pruned_context(self,
                            pruned_chunks: List[Dict[str, Any]],
                            include_metadata: bool = True) -> str:
        """
        Build a formatted context string from pruned chunks.
        Suitable for inclusion in LLM prompt.
        """
        context_parts = []
        
        for i, chunk in enumerate(pruned_chunks, 1):
            if include_metadata:
                metadata_str = self._format_metadata(chunk)
                context_parts.append(f"[Source {i}: {metadata_str}]")
            
            context_parts.append(chunk.get("content", ""))
            context_parts.append("")  # Blank line for readability
        
        return "\n".join(context_parts)
    
    def _format_metadata(self, chunk: Dict[str, Any]) -> str:
        """Format chunk metadata for context."""
        parts = []
        
        if chunk.get("textbook_name"):
            parts.append(chunk["textbook_name"])
        
        if chunk.get("chapter_title"):
            parts.append(f"Ch: {chunk['chapter_title']}")
        
        if chunk.get("page_number"):
            parts.append(f"P{chunk['page_number']}")
        
        return " | ".join(parts) if parts else "Source"
    
    def compare_baseline_vs_pruned(self,
                                   baseline_chunks: List[Dict[str, Any]],
                                   pruned_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare baseline (no pruning) vs pruned retrieval.
        Returns metrics for both approaches.
        """
        baseline_tokens = sum(estimate_tokens(c.get("content", "")) for c in baseline_chunks)
        pruned_tokens = sum(estimate_tokens(c.get("content", "")) for c in pruned_chunks)
        
        return {
            "baseline": {
                "chunks_count": len(baseline_chunks),
                "tokens": baseline_tokens,
            },
            "pruned": {
                "chunks_count": len(pruned_chunks),
                "tokens": pruned_tokens,
            },
            "improvement": {
                "chunks_reduction": len(baseline_chunks) - len(pruned_chunks),
                "chunks_reduction_percent": (1 - len(pruned_chunks) / len(baseline_chunks)) * 100 if baseline_chunks else 0,
                "token_reduction": baseline_tokens - pruned_tokens,
                "token_reduction_percent": (1 - pruned_tokens / baseline_tokens) * 100 if baseline_tokens > 0 else 0,
            }
        }
