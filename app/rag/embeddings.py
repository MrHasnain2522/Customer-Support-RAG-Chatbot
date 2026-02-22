"""
Embedding service - Supports both local and HuggingFace API
"""
import os
import numpy as np
from app.config import Config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings - supports local and API modes"""
    
    _instance = None
    _embedder = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize embedding service"""
        if self._embedder is None:
            self._initialize_embedder()
    
    def _initialize_embedder(self):
        """Initialize the appropriate embedder (local or API)"""
        use_api = os.getenv('USE_HUGGINGFACE_API', 'False').lower() == 'true'
        
        if use_api:
            logger.info("Using HuggingFace API for embeddings")
            from app.rag.huggingface_api_embeddings import HuggingFaceAPIEmbeddings
            self._embedder = HuggingFaceAPIEmbeddings()
            self._mode = 'api'
        else:
            logger.info("Using local model for embeddings")
            from sentence_transformers import SentenceTransformer
            model_name = Config.EMBEDDING_MODEL
            logger.info(f"Loading model: {model_name}")
            self._embedder = SentenceTransformer(model_name)
            self._mode = 'local'
            logger.info("Model loaded successfully")
    
    def encode(self, texts):
        """
        Generate embeddings for texts
        
        Args:
            texts: Single text string or list of texts
            
        Returns:
            numpy array of embeddings
        """
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            if self._mode == 'api':
                embeddings = self._embedder.encode(texts)
            else:
                embeddings = self._embedder.encode(texts, convert_to_numpy=True)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def get_dimension(self):
        """Get embedding dimension"""
        if self._mode == 'api':
            return self._embedder.get_dimension()
        else:
            return self._embedder.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1, embedding2):
        """
        Compute cosine similarity
        
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
            logger.error(f"Error computing similarity: {str(e)}")
            raise
    
    def get_mode(self):
        """Get current mode (local or api)"""
        return self._mode