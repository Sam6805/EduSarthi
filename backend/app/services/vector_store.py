"""Vector store management using FAISS."""

from typing import List, Dict, Any, Tuple
import json
import numpy as np
from pathlib import Path

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from app.config import VECTOR_INDEX_PATH, CHUNKS_METADATA_PATH
from app.utils.helpers import setup_logger

logger = setup_logger(__name__)


class VectorStore:
    """Manage vector embeddings and similarity search using FAISS."""
    
    def __init__(self):
        self.index = None
        self.chunk_metadata = {}  # Maps chunk_id to metadata
        self.chunk_to_index = {}  # Maps chunk_id to FAISS index position
        self.index_to_chunk = {}  # Maps FAISS index position to chunk_id
        self.embedding_dim = None
        self.has_faiss = HAS_FAISS
        
        if not HAS_FAISS:
            logger.warning("FAISS not installed, using in-memory storage")
    
    def create_index(self, embedding_dim: int) -> None:
        """Create a new FAISS index."""
        if not HAS_FAISS:
            self.embedding_dim = embedding_dim
            logger.info("Created in-memory vector store")
            return
        
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        logger.info(f"Created FAISS index with dimension {embedding_dim}")
    
    def add_vectors(self, 
                   chunks: List[Dict[str, Any]],
                   embeddings: List[np.ndarray]) -> None:
        """Add chunks and their embeddings to the index."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        if HAS_FAISS:
            start_idx = self.index.ntotal if self.index else 0
            self.index.add(embeddings_array)
        else:
            start_idx = len(self.chunk_to_index)
        
        # Store metadata and index mappings
        for i, chunk in enumerate(chunks):
            chunk_id = chunk["chunk_id"]
            index_pos = start_idx + i
            
            self.chunk_metadata[chunk_id] = {
                "chunk_id": chunk_id,
                "textbook_id": chunk["textbook_id"],
                "textbook_name": chunk["textbook_name"],
                "chapter_number": chunk.get("chapter_number"),
                "chapter_title": chunk.get("chapter_title"),
                "section_title": chunk.get("section_title"),
                "page_number": chunk.get("page_number"),
                "content_length": chunk["content_length"],
                "content_preview": chunk["content"][:100] + "..." if len(chunk["content"]) > 100 else chunk["content"]
            }
            
            self.chunk_to_index[chunk_id] = index_pos
            self.index_to_chunk[index_pos] = chunk_id
        
        logger.info(f"Added {len(chunks)} chunks to vector store. Total chunks: {len(self.chunk_metadata)}")
    
    def search(self, 
               query_embedding: np.ndarray,
               k: int = 10,
               textbook_id: str = None) -> List[Tuple[str, float]]:
        """
        Search for similar chunks.
        Returns: [(chunk_id, similarity_score), ...]
        """
        if len(self.chunk_metadata) == 0:
            logger.warning("Vector store is empty")
            return []
        
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        if HAS_FAISS and self.index:
            distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            results = []
            
            for dist, idx in zip(distances[0], indices):
                if idx == -1:  # Invalid result
                    continue
                
                chunk_id = self.index_to_chunk.get(idx)
                if not chunk_id:
                    continue
                
                # Filter by textbook if specified
                if textbook_id and self.chunk_metadata[chunk_id]["textbook_id"] != textbook_id:
                    continue
                
                # Convert L2 distance to similarity score (0-1)
                # L2 distance: smaller = more similar
                # similarity = 1 / (1 + distance)
                similarity = 1 / (1 + float(dist))
                results.append((chunk_id, similarity))
            
            return results
        else:
            # Fallback: in-memory search (for demo)
            return self._inMemorySearch(query_embedding[0], k, textbook_id)
    
    def _inMemorySearch(self, 
                       query_embedding: np.ndarray,
                       k: int,
                       textbook_id: str = None) -> List[Tuple[str, float]]:
        """In-memory similarity search using cosine distance."""
        results = []
        
        for chunk_id, metadata in self.chunk_metadata.items():
            if textbook_id and metadata["textbook_id"] != textbook_id:
                continue
            
            # For demo, use simple hash-based similarity
            similarity = self._hashBasedSimilarity(chunk_id, query_embedding)
            results.append((chunk_id, similarity))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def _hashBasedSimilarity(self, chunk_id: str, query_embedding: np.ndarray) -> float:
        """Simple similarity based on chunk_id hash for demo purposes."""
        return float(np.abs(np.sin(hash(chunk_id) * hash(query_embedding[0]) / 1e10)))
    
    def get_chunk_content(self, chunk_id: str) -> str:
        """Retrieve full chunk content (requires secondary storage)."""
        # This is a placeholder - in production, store chunks separately
        metadata = self.chunk_metadata.get(chunk_id)
        if metadata:
            return metadata.get("content_preview", "Content not available")
        return None
    
    def save_index(self, index_path: Path = VECTOR_INDEX_PATH) -> None:
        """Save FAISS index and metadata to disk."""
        if not HAS_FAISS:
            logger.info("Skipping FAISS save (not installed)")
            return
        
        if self.index is None:
            logger.warning("No index to save")
            return
        
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        logger.info(f"Saved FAISS index to {index_path}")
        
        # Save metadata
        metadata_path = CHUNKS_METADATA_PATH
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "chunk_to_index": self.chunk_to_index,
                "index_to_chunk": {int(k): v for k, v in self.index_to_chunk.items()},
                "metadata": self.chunk_metadata
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved metadata to {metadata_path}")
    
    def load_index(self, index_path: Path = VECTOR_INDEX_PATH) -> bool:
        """Load FAISS index and metadata from disk."""
        if not index_path.exists():
            logger.warning(f"Index file not found: {index_path}")
            return False
        
        if HAS_FAISS:
            try:
                self.index = faiss.read_index(str(index_path))
                self.embedding_dim = self.index.d
                logger.info(f"Loaded FAISS index from {index_path}")
            except Exception as e:
                logger.error(f"Failed to load FAISS index: {e}")
                return False
        
        # Load metadata
        metadata_path = CHUNKS_METADATA_PATH
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chunk_to_index = data.get("chunk_to_index", {})
                    self.index_to_chunk = {int(k): v for k, v in data.get("index_to_chunk", {}).items()}
                    self.chunk_metadata = data.get("metadata", {})
                logger.info(f"Loaded metadata from {metadata_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_chunks": len(self.chunk_metadata),
            "embedding_dim": self.embedding_dim,
            "has_faiss": HAS_FAISS,
            "index_size": self.index.ntotal if self.index else 0
        }
