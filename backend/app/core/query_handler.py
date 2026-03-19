"""Query handler orchestrating the full answer generation pipeline."""

from typing import Dict, Any
import time

from app.services.retriever import Retriever
from app.services.context_pruner import ContextPruner
from app.services.llm_generator import LLMGenerator
from app.utils.helpers import setup_logger, estimate_tokens
from app.schemas import QueryRequest, QueryResponse, GeneratedAnswer

logger = setup_logger(__name__)


class QueryHandler:
    """Handle questions end-to-end: retrieve, prune, generate."""
    
    def __init__(self):
        self.retriever = Retriever()
        self.pruner = ContextPruner()
        self.generator = LLMGenerator()
        self.query_history = []  # For metrics tracking
    
    def handle_query(self, request: QueryRequest) -> QueryResponse:
        """
        Handle a student question end-to-end.
        """
        pipeline_start = time.time()
        
        logger.info(f"Handling query: {request.question[:50]}...")
        
        # Step 1: Retrieve relevant chunks
        retrieval_result = self.retriever.retrieve_with_pruning(
            question=request.question,
            textbook_id=request.textbook_id,
            apply_pruning=request.use_pruning
        )
        
        retrieved_chunks = retrieval_result["retrieved_chunks"]
        pruned_chunks = retrieval_result["pruned_chunks"]
        
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks, pruned to {len(pruned_chunks)}")
        
        # Step 2: Calculate token estimates
        tokens_before = estimate_tokens(self._chunks_to_text(retrieved_chunks))
        tokens_after = estimate_tokens(self._chunks_to_text(pruned_chunks))
        
        # Step 3: Build context from pruned chunks
        context = self.pruner.build_pruned_context(
            pruned_chunks,
            include_metadata=True
        )
        
        # Step 4: Generate answer
        generation_start = time.time()
        answer_data = self.generator.generate_answer(
            question=request.question,
            context=context,
            language=request.language,
            simple=True,
            detailed=False
        )
        generation_latency = (time.time() - generation_start) * 1000
        
        # Step 5: Extract source information
        source_chapter = None
        source_pages = set()
        
        for chunk in pruned_chunks[:3]:  # Top 3 chunks for source info
            if chunk.get("chapter_title"):
                source_chapter = chunk["chapter_title"]
            if chunk.get("page_number"):
                source_pages.add(chunk["page_number"])
        
        # Build response
        response = QueryResponse(
            question=request.question,
            answer=GeneratedAnswer(
                simple_answer=answer_data.get("simple_answer", ""),
                detailed_answer=answer_data.get("detailed_answer"),
                source_chapter=source_chapter,
                source_pages=sorted(list(source_pages))
            ),
            retrieved_chunks_count=len(retrieved_chunks),
            retrieved_chunks=self._format_chunks_for_response(retrieved_chunks[:5]),
            pruned_chunks_count=len(retrieved_chunks) - len(pruned_chunks),
            pruning_applied=request.use_pruning,
            token_estimate_before_pruning=tokens_before,
            token_estimate_after_pruning=tokens_after,
            token_reduction_percentage=(
                (1 - tokens_after / tokens_before) * 100 
                if tokens_before > 0 else 0
            ),
            retrieval_latency_ms=retrieval_result["retrieval_latency"],
            pruning_latency_ms=retrieval_result["pruning_latency"],
            generation_latency_ms=generation_latency,
            total_latency_ms=(time.time() - pipeline_start) * 1000,
            textbook_used=request.textbook_id or "all"
        )
        
        # Track for metrics
        self._record_query(response)
        
        return response
    
    def _chunks_to_text(self, chunks):
        """Combine chunk contents into single text."""
        return " ".join([c.get("content", "") for c in chunks])
    
    def _format_chunks_for_response(self, chunks):
        """Format chunks for API response."""
        from app.schemas import RetrievedChunk
        
        formatted = []
        for chunk in chunks:
            formatted.append(RetrievedChunk(
                chunk_id=chunk.get("chunk_id", ""),
                textbook_name=chunk.get("textbook_name", ""),
                chapter_title=chunk.get("chapter_title"),
                page_number=chunk.get("page_number"),
                content=chunk.get("content_preview", chunk.get("content", ""))[:300],
                relevance_score=chunk.get("relevance_score", 0.0),
                is_pruned=False
            ))
        return formatted
    
    def _record_query(self, response: QueryResponse) -> None:
        """Record query for metrics."""
        self.query_history.append({
            "question": response.question,
            "retrieved_chunks": response.retrieved_chunks_count,
            "pruned_chunks": response.pruned_chunks_count,
            "tokens_before": response.token_estimate_before_pruning,
            "tokens_after": response.token_estimate_after_pruning,
            "reduction_percent": response.token_reduction_percentage,
            "latency_ms": response.total_latency_ms
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all queries processed."""
        if not self.query_history:
            return {
                "total_queries": 0,
                "avg_chunks_retrieved": 0,
                "avg_chunks_pruned": 0,
                "avg_token_reduction": 0,
                "total_tokens_saved": 0
            }
        
        total_queries = len(self.query_history)
        avg_retrieved = sum(q["retrieved_chunks"] for q in self.query_history) / total_queries
        avg_pruned = sum(q["pruned_chunks"] for q in self.query_history) / total_queries
        avg_reduction = sum(q["reduction_percent"] for q in self.query_history) / total_queries
        total_saved = sum(q["tokens_before"] - q["tokens_after"] for q in self.query_history)
        
        return {
            "total_queries": total_queries,
            "avg_retrieved_chunks": round(avg_retrieved, 2),
            "avg_pruned_chunks": round(avg_pruned, 2),
            "avg_token_reduction_percentage": round(avg_reduction, 2),
            "total_tokens_saved": total_saved,
            "recent_queries": self.query_history[-5:]  # Last 5 queries
        }
