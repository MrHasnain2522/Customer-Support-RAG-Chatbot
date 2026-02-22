"""
ChromaDB Vector Store
"""
import os
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChromaVectorStore:
    """ChromaDB-based vector store"""
    
    def __init__(self, persist_directory: str = None, collection_name: str = None):
        """Initialize ChromaDB"""
        self.persist_directory = persist_directory or os.getenv('CHROMA_PERSIST_DIRECTORY', 'vector_stores/chroma')
        self.collection_name = collection_name or os.getenv('CHROMA_COLLECTION_NAME', 'knowledge_base')
        
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        ))
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded ChromaDB collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "RAG knowledge base"}
            )
            logger.info(f"Created ChromaDB collection: {self.collection_name}")
    
    def add_documents(self, embeddings: List[List[float]], texts: List[str], 
                     metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        """
        Add documents
        
        Args:
            embeddings: Document embeddings
            texts: Document texts
            metadatas: Optional metadata
            ids: Optional IDs
        """
        if ids is None:
            current_count = self.collection.count()
            ids = [f"doc_{i}" for i in range(current_count, current_count + len(texts))]
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(texts)} documents. Total: {self.collection.count()}")
    
    def search(self, query_embedding: List[float], top_k: int = 5, 
               threshold: float = None, where: Dict = None) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results
            threshold: Similarity threshold
            where: Metadata filter
            
        Returns:
            List of documents with scores
        """
        if self.collection.count() == 0:
            logger.warning("ChromaDB collection is empty")
            return []
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )
        
        formatted_results = []
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i]
                similarity = 1 / (1 + distance)
                
                if threshold is not None and similarity < threshold:
                    continue
                
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'score': float(similarity),
                    'id': results['ids'][0][i]
                })
        
        logger.info(f"Found {len(formatted_results)} documents")
        return formatted_results
    
    def delete_documents(self, ids: List[str]):
        """Delete documents by IDs"""
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents")
    
    def clear(self):
        """Clear all documents"""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "RAG knowledge base"}
        )
        logger.info("Cleared ChromaDB collection")
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection_name,
            'persist_directory': self.persist_directory
        }