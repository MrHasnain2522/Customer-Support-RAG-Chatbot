"""
HuggingFace API Embedding Service
"""
import os
import numpy as np
import requests
from typing import List, Union
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HuggingFaceAPIEmbeddings:
    """HuggingFace API-based embedding service"""
    
    def __init__(self):
        """Initialize HuggingFace API"""
        self.api_token = os.getenv('HUGGINGFACE_API_TOKEN')
        if not self.api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN not found")
        
        self.model_name = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model_name}"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized HuggingFace API with model: {self.model_name}")
    
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings via API
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
            single_input = True
        else:
            single_input = False
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": texts,
                    "options": {"wait_for_model": True}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                embeddings = np.array(response.json())
                
                if single_input:
                    embeddings = embeddings.reshape(1, -1)
                
                logger.info(f"Generated embeddings for {len(texts)} texts via API")
                return embeddings
            
            elif response.status_code == 503:
                logger.warning("Model loading, retrying...")
                import time
                time.sleep(5)
                return self.encode(texts)
            
            else:
                error_msg = f"API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            logger.error("API timeout")
            raise Exception("API timeout after 30 seconds")
        
        except Exception as e:
            logger.error(f"API error: {str(e)}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        try:
            test_embedding = self.encode("test")
            return test_embedding.shape[1]
        except:
            if "MiniLM" in self.model_name:
                return 384
            elif "mpnet" in self.model_name:
                return 768
            else:
                return 384
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity"""
        try:
            embedding1 = embedding1 / np.linalg.norm(embedding1)
            embedding2 = embedding2 / np.linalg.norm(embedding2)
            similarity = np.dot(embedding1, embedding2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise