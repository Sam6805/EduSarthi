"""Embedding generation service using sentence-transformers."""

from typing import List, Dict, Any
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

from app.config import EMBEDDING_MODEL, EMBEDDING_DIM
from app.utils.helpers import setup_logger

logger = setup_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text chunks."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = None
        self.embedding_dim = EMBEDDING_DIM
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading embedding model: {model_name}")
                self.model = SentenceTransformer(model_name)
                logger.info(f"Loaded embedding model with dimension: {self.embedding_dim}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}, using mock embeddings")
        else:
            logger.warning("sentence-transformers not installed, using mock embeddings")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        if self.model is None:
            return self._generate_mock_embedding(text)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return self._generate_mock_embedding(text)
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[np.ndarray]:
        """Generate embeddings for multiple chunks."""
        embeddings = []
        texts = [chunk["content"] for chunk in chunks]
        
        if self.model is None:
            logger.info("Using mock embeddings")
            return [self._generate_mock_embedding(text) for text in texts]
        
        try:
            batch_embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb.astype(np.float32) for emb in batch_embeddings]
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [self._generate_mock_embedding(text) for text in texts]
    
    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """Generate a mock embedding based on text hash."""
        # For demo purposes, create a deterministic embedding based on text
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        # Normalize to unit vector
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        return embedding
    
    def get_embedding_dim(self) -> int:
        """Get the dimension of generated embeddings."""
        return self.embedding_dim
