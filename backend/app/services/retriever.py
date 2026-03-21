"""Retriever service – coordinates search, reranking, and pruning.

Key fix: uses vector_store.get_chunk_content() to load FULL PDF text
into each chunk before passing to the context pruner and LLM.
"""

from typing import List, Dict, Any, Tuple
import time

from app.services.embedder import EmbeddingGenerator
from app.services.vector_store import VectorStore
from app.services.context_pruner import ContextPruner
from app.utils.helpers import setup_logger
from app.config import TOP_K_CHUNKS, SIMILARITY_THRESHOLD

logger = setup_logger(__name__)


class Retriever:
    """Retrieve and rank relevant chunks from the vector store."""

    def __init__(self):
        self.embedder = EmbeddingGenerator()
        self.vector_store = VectorStore()
        self.pruner = ContextPruner()

    # ── Core retrieval ────────────────────────────────────────────────────
    def retrieve_for_question(self,
                              question: str,
                              textbook_id: str = None,
                              k: int = TOP_K_CHUNKS,
                              threshold: float = SIMILARITY_THRESHOLD
                              ) -> Tuple[List[Dict[str, Any]], float]:
        start = time.time()
        try:
            question_embedding = self.embedder.embed_text(question)
            search_results = self.vector_store.search(
                question_embedding, k=k, textbook_id=textbook_id
            )

            chunks = []
            for chunk_id, score in search_results:
                if score < threshold:
                    continue
                metadata = self.vector_store.chunk_metadata.get(chunk_id)
                if not metadata:
                    continue

                # ✅ KEY FIX: fetch FULL content, not just the preview
                full_content = self.vector_store.get_chunk_content(chunk_id)
                if not full_content:
                    full_content = metadata.get("content_preview", "")

                chunk_dict = {
                    **metadata,
                    "content": full_content,          # full PDF text ✅
                    "content_preview": metadata.get("content_preview", full_content[:200]),
                    "relevance_score": score,
                }
                chunks.append(chunk_dict)

            latency = (time.time() - start) * 1000
            logger.info(f"Retrieved {len(chunks)} chunks in {latency:.1f}ms")
            return chunks, latency

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return [], (time.time() - start) * 1000

    def retrieve_and_rerank(self,
                            question: str,
                            textbook_id: str = None,
                            k: int = TOP_K_CHUNKS
                            ) -> Tuple[List[Dict[str, Any]], float]:
        chunks, latency = self.retrieve_for_question(question, textbook_id, k)
        if chunks:
            chunks = self.pruner.rerank_by_relevance(chunks, question)
        return chunks, latency

    def retrieve_with_pruning(self,
                              question: str,
                              textbook_id: str = None,
                              k: int = TOP_K_CHUNKS,
                              apply_pruning: bool = True) -> Dict[str, Any]:
        start = time.time()

        retrieved, retrieval_latency = self.retrieve_and_rerank(question, textbook_id, k)

        pruned_chunks = retrieved
        pruning_latency = 0.0
        metrics = {}

        if apply_pruning and retrieved:
            prune_start = time.time()
            pruned_chunks, metrics = self.pruner.prune_chunks(retrieved, question)
            pruning_latency = (time.time() - prune_start) * 1000

        return {
            "retrieved_chunks": retrieved,
            "pruned_chunks": pruned_chunks,
            "retrieval_latency": retrieval_latency,
            "pruning_latency": pruning_latency,
            "total_latency": (time.time() - start) * 1000,
            "pruning_metrics": metrics,
            "question": question,
            "textbook_id": textbook_id,
        }

    def get_vector_store_stats(self) -> Dict[str, Any]:
        return self.vector_store.get_stats()
