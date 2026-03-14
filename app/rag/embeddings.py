"""
Embedding service - OpenAI API based
No torch, no sentence-transformers, no local model
"""
import os
import numpy as np
from openai import OpenAI
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI API"""

    _instance  = None
    _client    = None
    _model     = "text-embedding-3-small"   # ✅ cheap + fast + 1536 dims
    _dimension = 1536

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize OpenAI embedding client"""
        if self._client is None:
            self._initialize_embedder()

    def _initialize_embedder(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY", "")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing!\n"
                "Add it to your .env file."
            )

        self._client = OpenAI(api_key=api_key)
        self._mode   = "openai_api"

        logger.info(f"EmbeddingService initialized → model: {self._model}")

    def encode(self, texts) -> np.ndarray:
        """
        Generate embeddings for texts using OpenAI API.

        Args:
            texts: Single string or list of strings

        Returns:
            numpy array of embeddings shape (n, 1536)
        """
        try:
            if isinstance(texts, str):
                texts = [texts]

            # ✅ Clean texts — OpenAI doesn't like empty strings
            texts = [t.strip().replace("\n", " ") for t in texts]
            texts = [t if t else " " for t in texts]

            logger.debug(f"Encoding {len(texts)} texts with {self._model}")

            response = self._client.embeddings.create(
                model=self._model,
                input=texts,
            )

            embeddings = np.array(
                [item.embedding for item in response.data],
                dtype=np.float32
            )

            logger.debug(f"Embeddings shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

    def get_sentence_embedding_dimension(self) -> int:
        """Alias for compatibility with old code."""
        return self._dimension

    def compute_similarity(self, embedding1, embedding2) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            float: Similarity score (0 to 1)
        """
        try:
            embedding1 = embedding1 / np.linalg.norm(embedding1)
            embedding2 = embedding2 / np.linalg.norm(embedding2)
            similarity = np.dot(embedding1, embedding2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            raise

    def get_mode(self) -> str:
        """Get current mode."""
        return self._mode