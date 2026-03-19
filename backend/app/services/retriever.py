"""Retriever service coordinating search and ranking."""

from typing import List, Dict, Any, Tuple
import time

from app.services.embedder import EmbeddingGenerator
from app.services.vector_store import VectorStore
from app.services.context_pruner import ContextPruner
from app.utils.helpers import setup_logger
from app.config import TOP_K_CHUNKS, SIMILARITY_THRESHOLD

logger = setup_logger(__name__)


class Retriever:
    """Retrieve and rank relevant chunks."""
    
    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.pruner = ContextPruner()
    
    def retrieve_for_question(self,
                             question: str,
                             textbook_id: str = None,
                             k: int = TOP_K_CHUNKS,
                             threshold: float = SIMILARITY_THRESHOLD) -> Tuple[List[Dict[str, Any]], float]:
        """
        Retrieve most relevant chunks for a question.
        
        Returns:
            - chunks: List of retrieved chunks with metadata and scores
            - latency: Retrieval time
        """
        start_time = time.time()
        
        try:
            # Generate embedding for question
            question_embedding = self.embedder.embed_text(question)
            
            # Search vector store
            search_results = self.vector_store.search(
                question_embedding,
                k=k,
                textbook_id=textbook_id
            )
            
            # Convert results to chunk dictionaries
            chunks = []
            for chunk_id, score in search_results:
                if score < threshold:
                    continue
                
                metadata = self.vector_store.chunk_metadata.get(chunk_id)
                if not metadata:
                    continue
                
                chunk_dict = {
                    **metadata,
                    "content": metadata.get("content_preview", ""),  # In production, fetch full content
                    "relevance_score": score
                }
                chunks.append(chunk_dict)
            
            latency = (time.time() - start_time) * 1000  # ms
            logger.info(f"Retrieved {len(chunks)} chunks in {latency:.2f}ms")
            
            return chunks, latency
        
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return [], (time.time() - start_time) * 1000
    
    def retrieve_and_rerank(self,
                           question: str,
                           textbook_id: str = None,
                           k: int = TOP_K_CHUNKS) -> Tuple[List[Dict[str, Any]], float]:
        """
        Retrieve chunks and rerank by relevance to question.
        """
        chunks, latency = self.retrieve_for_question(question, textbook_id, k)
        
        if not chunks:
            return chunks, latency
        
        # Rerank by relevance
        reranked = self.pruner.rerank_by_relevance(chunks, question)
        
        return reranked, latency
    
    def retrieve_with_pruning(self,
                             question: str,
                             textbook_id: str = None,
                             k: int = TOP_K_CHUNKS,
                             apply_pruning: bool = True) -> Dict[str, Any]:
        """
        Full retrieval pipeline with optional pruning.
        
        Returns:
            {
                "retrieved_chunks": [...],
                "pruned_chunks": [...],
                "retrieval_latency": float,
                "pruning_latency": float,
                "metrics": {...}
            }
        """
        start_time = time.time()
        
        # Step 1: Retrieve and rerank
        retrieved, retrieval_latency = self.retrieve_and_rerank(question, textbook_id, k)
        
        # Step 2: Prune (optional)
        pruning_latency = 0
        pruned_chunks = retrieved
        metrics = {}
        
        if apply_pruning and retrieved:
            prune_start = time.time()
            pruned_chunks, metrics = self.pruner.prune_chunks(retrieved, question)
            pruning_latency = (time.time() - prune_start) * 1000
        
        total_latency = (time.time() - start_time) * 1000
        
        return {
            "retrieved_chunks": retrieved,
            "pruned_chunks": pruned_chunks,
            "retrieval_latency": retrieval_latency,
            "pruning_latency": pruning_latency,
            "total_latency": total_latency,
            "pruning_metrics": metrics,
            "question": question,
            "textbook_id": textbook_id
        }
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return self.vector_store.get_stats()
