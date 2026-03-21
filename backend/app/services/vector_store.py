"""Vector store management using FAISS.

Key fix: stores FULL chunk content (not just preview) so that
retrieval actually passes real PDF text to the LLM.
"""

from typing import List, Dict, Any, Tuple
import json
import numpy as np
from pathlib import Path

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from app.config import VECTOR_INDEX_PATH, CHUNKS_METADATA_PATH, PROCESSED_CHUNKS_DIR
from app.utils.helpers import setup_logger

logger = setup_logger(__name__)

# Full content is stored in a separate file to keep metadata lean
FULL_CONTENT_PATH = PROCESSED_CHUNKS_DIR / "chunks_full_content.json"


class VectorStore:
    """Manage vector embeddings and similarity search using FAISS."""

    def __init__(self):
        self.index = None
        self.chunk_metadata = {}    # chunk_id → metadata + full content
        self.chunk_to_index = {}    # chunk_id → FAISS position
        self.index_to_chunk = {}    # FAISS position → chunk_id
        self.embedding_dim = None
        self.has_faiss = HAS_FAISS
        self._full_content: Dict[str, str] = {}   # chunk_id → full content

        if not HAS_FAISS:
            logger.warning("FAISS not installed – using in-memory cosine search")

        # Auto-load if index already exists on disk
        self._try_load()

    # ── Index creation ────────────────────────────────────────────────────
    def create_index(self, embedding_dim: int) -> None:
        self.embedding_dim = embedding_dim
        if HAS_FAISS:
            self.index = faiss.IndexFlatL2(embedding_dim)
            logger.info(f"Created FAISS index (dim={embedding_dim})")
        else:
            logger.info("Created in-memory vector store")

    # ── Add vectors ───────────────────────────────────────────────────────
    def add_vectors(self,
                    chunks: List[Dict[str, Any]],
                    embeddings: List[np.ndarray]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")

        embeddings_array = np.array(embeddings, dtype=np.float32)

        if HAS_FAISS and self.index:
            start_idx = self.index.ntotal
            self.index.add(embeddings_array)
        else:
            start_idx = len(self.chunk_to_index)
            # Store embeddings in memory for fallback search
            if not hasattr(self, '_mem_embeddings'):
                self._mem_embeddings = {}
            for i, emb in enumerate(embeddings):
                self._mem_embeddings[chunks[i]["chunk_id"]] = emb

        for i, chunk in enumerate(chunks):
            chunk_id = chunk["chunk_id"]
            index_pos = start_idx + i
            full_content = chunk.get("content", "")

            # Store metadata (lightweight)
            self.chunk_metadata[chunk_id] = {
                "chunk_id": chunk_id,
                "textbook_id": chunk["textbook_id"],
                "textbook_name": chunk["textbook_name"],
                "chapter_number": chunk.get("chapter_number"),
                "chapter_title": chunk.get("chapter_title"),
                "section_title": chunk.get("section_title"),
                "page_number": chunk.get("page_number"),
                "content_length": chunk["content_length"],
                "content_preview": full_content[:200] + "..." if len(full_content) > 200 else full_content,
            }

            # Store FULL content separately
            self._full_content[chunk_id] = full_content

            self.chunk_to_index[chunk_id] = index_pos
            self.index_to_chunk[index_pos] = chunk_id

        logger.info(f"Added {len(chunks)} chunks. Total: {len(self.chunk_metadata)}")

    # ── Search ────────────────────────────────────────────────────────────
    def search(self,
               query_embedding: np.ndarray,
               k: int = 10,
               textbook_id: str = None) -> List[Tuple[str, float]]:
        if not self.chunk_metadata:
            logger.warning("Vector store is empty")
            return []

        query_embedding = np.array([query_embedding], dtype=np.float32)

        if HAS_FAISS and self.index and self.index.ntotal > 0:
            distances, indices = self.index.search(
                query_embedding, min(k * 2, self.index.ntotal)
            )
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue
                chunk_id = self.index_to_chunk.get(int(idx))
                if not chunk_id:
                    continue
                if textbook_id and self.chunk_metadata[chunk_id]["textbook_id"] != textbook_id:
                    continue
                similarity = float(1 / (1 + dist))
                results.append((chunk_id, similarity))
            return results[:k]
        else:
            return self._cosine_search(query_embedding[0], k, textbook_id)

    def _cosine_search(self,
                       query_emb: np.ndarray,
                       k: int,
                       textbook_id: str = None) -> List[Tuple[str, float]]:
        """Cosine similarity fallback when FAISS not available."""
        results = []
        mem_emb = getattr(self, '_mem_embeddings', {})

        for chunk_id, meta in self.chunk_metadata.items():
            if textbook_id and meta["textbook_id"] != textbook_id:
                continue
            if chunk_id in mem_emb:
                stored = mem_emb[chunk_id]
                # cosine similarity
                num = float(np.dot(query_emb, stored))
                den = float(np.linalg.norm(query_emb) * np.linalg.norm(stored) + 1e-8)
                sim = (num / den + 1) / 2  # normalise to 0-1
            else:
                sim = 0.1
            results.append((chunk_id, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    # ── Full content retrieval ────────────────────────────────────────────
    def get_chunk_content(self, chunk_id: str) -> str:
        """Return FULL text content of a chunk (not just preview)."""
        return self._full_content.get(chunk_id, "")

    # ── Persistence ───────────────────────────────────────────────────────
    def save_index(self, index_path: Path = VECTOR_INDEX_PATH) -> None:
        index_path.parent.mkdir(parents=True, exist_ok=True)

        if HAS_FAISS and self.index:
            faiss.write_index(self.index, str(index_path))
            logger.info(f"Saved FAISS index → {index_path}")

        # Save metadata + mappings
        metadata_path = CHUNKS_METADATA_PATH
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "chunk_to_index": self.chunk_to_index,
                "index_to_chunk": {str(k): v for k, v in self.index_to_chunk.items()},
                "metadata": self.chunk_metadata,
                "embedding_dim": self.embedding_dim,
            }, f, ensure_ascii=False)
        logger.info(f"Saved metadata → {metadata_path}")

        # Save full content separately
        FULL_CONTENT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(FULL_CONTENT_PATH, 'w', encoding='utf-8') as f:
            json.dump(self._full_content, f, ensure_ascii=False)
        logger.info(f"Saved full content → {FULL_CONTENT_PATH}")

        # Save in-memory embeddings if FAISS not available
        if not HAS_FAISS and hasattr(self, '_mem_embeddings'):
            emb_path = VECTOR_INDEX_PATH.parent / "mem_embeddings.json"
            serialisable = {k: v.tolist() for k, v in self._mem_embeddings.items()}
            with open(emb_path, 'w') as f:
                json.dump(serialisable, f)

    def _try_load(self) -> bool:
        """Try to load existing index from disk on startup."""
        metadata_path = CHUNKS_METADATA_PATH
        if not metadata_path.exists():
            return False
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.chunk_to_index = data.get("chunk_to_index", {})
            self.index_to_chunk = {int(k): v for k, v in data.get("index_to_chunk", {}).items()}
            self.chunk_metadata = data.get("metadata", {})
            self.embedding_dim = data.get("embedding_dim")

            # Load full content
            if FULL_CONTENT_PATH.exists():
                with open(FULL_CONTENT_PATH, 'r', encoding='utf-8') as f:
                    self._full_content = json.load(f)

            # Load FAISS index
            if HAS_FAISS and VECTOR_INDEX_PATH.exists():
                self.index = faiss.read_index(str(VECTOR_INDEX_PATH))
                logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")

            # Load in-memory embeddings
            emb_path = VECTOR_INDEX_PATH.parent / "mem_embeddings.json"
            if not HAS_FAISS and emb_path.exists():
                with open(emb_path, 'r') as f:
                    raw = json.load(f)
                self._mem_embeddings = {k: np.array(v, dtype=np.float32) for k, v in raw.items()}

            logger.info(f"Auto-loaded {len(self.chunk_metadata)} chunks from disk")
            return True
        except Exception as e:
            logger.warning(f"Could not auto-load index: {e}")
            return False

    # ── Stats ─────────────────────────────────────────────────────────────
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_chunks": len(self.chunk_metadata),
            "embedding_dim": self.embedding_dim,
            "has_faiss": HAS_FAISS,
            "index_size": self.index.ntotal if self.index else 0,
            "full_content_loaded": len(self._full_content),
        }
