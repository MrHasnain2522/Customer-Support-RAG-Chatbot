"""
RAG Retriever - Retrieves relevant context from vector database
"""
import os
from typing import List, Dict, Optional
import numpy as np
from app.rag.embeddings import EmbeddingService
from app.rag.document_loader import DocumentLoader
from app.utils.logger import get_logger
logger = get_logger(__name__)


class RAGRetriever:
    """Retriever with vector database support"""
    
    def __init__(self, vector_db_type: str = None):
        """
        Initialize retriever
        
        Args:
            vector_db_type: 'faiss', 'chroma', or 'none'
        """
        self.embedding_service = EmbeddingService()
        self.document_loader = DocumentLoader()
        
        self.vector_db_type = vector_db_type or os.getenv('VECTOR_DB_TYPE', 'faiss')
        
        # Initialize vector store
        self.vector_store = None
        if self.vector_db_type == 'faiss':
            from app.rag.faiss_store import FAISSVectorStore
            self.vector_store = FAISSVectorStore()
            logger.info("Using FAISS vector store")
        elif self.vector_db_type == 'chroma':
            from app.rag.chroma_store import ChromaVectorStore
            self.vector_store = ChromaVectorStore()
            logger.info("Using ChromaDB")
        else:
            logger.warning("No vector database configured")
        
        # Auto-load knowledge base
        if os.getenv('AUTO_RELOAD_KNOWLEDGE_BASE', 'True').lower() == 'true':
            self.load_knowledge_base()
    
    def load_knowledge_base(self, force_reload: bool = False):
        """
        Load documents from knowledge_base/documents/
        
        Args:
            force_reload: Force reload even if already loaded
        """
        try:
            # Check if already loaded
            if not force_reload and self.vector_store:
                stats = self.vector_store.get_stats()
                if stats.get('total_documents', 0) > 0:
                    logger.info(f"Knowledge base already loaded: {stats}")
                    return
            
            # Load and chunk documents
            chunk_size = int(os.getenv('CHUNK_SIZE', 500))
            chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 50))
            
            documents = self.document_loader.load_and_chunk_documents(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            if not documents:
                logger.warning("No documents found in knowledge base")
                return
            
            # Extract texts and metadata
            texts = [doc['text'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks...")
            embeddings = self.embedding_service.encode(texts)
            
            # Add to vector store
            if self.vector_db_type == 'faiss':
                self.vector_store.add_documents(embeddings, texts, metadatas)
                self.vector_store.save()
            elif self.vector_db_type == 'chroma':
                embeddings_list = embeddings.tolist()
                self.vector_store.add_documents(embeddings_list, texts, metadatas)
            
            stats = self.vector_store.get_stats()
            logger.info(f"Knowledge base loaded: {stats}")
            
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}", exc_info=True)
    
    def retrieve(self, query: str, conversation_history: list = None, top_k: int = None) -> Optional[str]:
        """
        Retrieve relevant context
        
        Args:
            query: User query
            conversation_history: Previous messages
            top_k: Number of documents to retrieve
            
        Returns:
            Retrieved context or None
        """
        try:
            if not self.vector_store:
                logger.warning("No vector store configured")
                return None
            
            # Get parameters
            if top_k is None:
                top_k = int(os.getenv('TOP_K_RESULTS', 3))
            
            threshold = float(os.getenv('SIMILARITY_THRESHOLD', 0.3))
            
            # Generate query embedding
            query_embedding = self.embedding_service.encode(query)
            
            # Search
            if self.vector_db_type == 'faiss':
                results = self.vector_store.search(query_embedding, top_k, threshold)
            elif self.vector_db_type == 'chroma':
                query_embedding_list = query_embedding.tolist()
                results = self.vector_store.search(query_embedding_list, top_k, threshold)
            else:
                return None
            
            if not results:
                logger.info("No relevant documents found")
                return None
            
            # Format context
            context_parts = []
            for i, result in enumerate(results, 1):
                source = result.get('metadata', {}).get('filename', 'Unknown')
                text = result['text']
                score = result['score']
                
                context_parts.append(
                    f"[Source {i}: {source} (Relevance: {score:.2f})]\n{text}"
                )
            
            context = "\n\n".join(context_parts)
            logger.info(f"Retrieved {len(results)} relevant documents")
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}", exc_info=True)
            return None
    
    def add_document(self, text: str, metadata: Dict = None):
        """Add a single document"""
        try:
            if not self.vector_store:
                logger.warning("No vector store configured")
                return
            
            # Generate embedding
            embedding = self.embedding_service.encode(text)
            
            # Add to vector store
            if self.vector_db_type == 'faiss':
                self.vector_store.add_documents(
                    embedding.reshape(1, -1), 
                    [text], 
                    [metadata] if metadata else None
                )
                self.vector_store.save()
            elif self.vector_db_type == 'chroma':
                embedding_list = embedding.tolist()
                self.vector_store.add_documents(
                    [embedding_list], 
                    [text], 
                    [metadata] if metadata else None
                )
            
            logger.info("Document added to knowledge base")
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
    
    def clear_knowledge_base(self):
        """Clear knowledge base"""
        if self.vector_store:
            self.vector_store.clear()
            logger.info("Knowledge base cleared")
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        if self.vector_store:
            return self.vector_store.get_stats()
        return {'total_documents': 0}