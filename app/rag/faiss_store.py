"""
FAISS Vector Store
"""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FAISSVectorStore:
    """FAISS-based vector store"""
    
    def __init__(self, index_path: str = None, metadata_path: str = None):
        """Initialize FAISS store"""
        self.index_path = index_path or os.getenv('FAISS_INDEX_PATH', 'vector_stores/faiss/index.faiss')
        self.metadata_path = metadata_path or os.getenv('FAISS_METADATA_PATH', 'vector_stores/faiss/metadata.pkl')
        
        self.index = None
        self.metadata = []
        self.dimension = None
        
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        self.load()
    
    def create_index(self, dimension: int):
        """Create new FAISS index"""
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        logger.info(f"Created FAISS index with dimension {dimension}")
    
    def add_documents(self, embeddings: np.ndarray, texts: List[str], metadatas: Optional[List[Dict]] = None):
        """
        Add documents to vector store
        
        Args:
            embeddings: Document embeddings (n x dimension)
            texts: Document texts
            metadatas: Optional metadata
        """
        if self.index is None:
            self.create_index(embeddings.shape[1])
        
        # Normalize embeddings
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store metadata
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        for text, metadata in zip(texts, metadatas):
            self.metadata.append({
                'text': text,
                'metadata': metadata
            })
        
        logger.info(f"Added {len(texts)} documents. Total: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5, threshold: float = None) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results
            threshold: Similarity threshold
            
        Returns:
            List of documents with scores
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []
        
        # Normalize query
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        
        # Convert to similarity scores
        similarities = 1 / (1 + distances[0])
        
        # Prepare results
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if idx == -1:
                continue
            
            if threshold is not None and similarity < threshold:
                continue
            
            doc_data = self.metadata[idx]
            results.append({
                'text': doc_data['text'],
                'metadata': doc_data['metadata'],
                'score': float(similarity),
                'index': int(idx)
            })
        
        logger.info(f"Found {len(results)} documents")
        return results
    
    def save(self):
        """Save index and metadata"""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            logger.info(f"Saved FAISS index to {self.index_path}")
        
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'dimension': self.dimension
            }, f)
        logger.info(f"Saved metadata to {self.metadata_path}")
    
    def load(self):
        """Load index and metadata"""
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                logger.info(f"Loaded FAISS index from {self.index_path}")
            
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data['metadata']
                    self.dimension = data['dimension']
                logger.info(f"Loaded metadata from {self.metadata_path}")
        except Exception as e:
            logger.error(f"Error loading FAISS: {str(e)}")
    
    def clear(self):
        """Clear vector store"""
        self.index = None
        self.metadata = []
        self.dimension = None
        
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)
        
        logger.info("Cleared FAISS vector store")
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            'total_documents': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else None
        }