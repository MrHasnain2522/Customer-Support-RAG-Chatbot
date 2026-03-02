"""
RAG Retriever - Optimized for Catalog Queries and Policy Details
"""
import os
from typing import List, Dict, Optional
import numpy as np
from app.rag.embeddings import EmbeddingService
from app.rag.document_loader import DocumentLoader
from app.utils.logger import get_logger

logger = get_logger(__name__)

class RAGRetriever:
    """Retriever with Vector DB support and Dynamic Search Depth"""
    
    def __init__(self, vector_db_type: str = None):
        """Initialize retriever and load configured vector store"""
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
        
        # Auto-load knowledge base if enabled
        if os.getenv('AUTO_RELOAD_KNOWLEDGE_BASE', 'True').lower() == 'true':
            self.load_knowledge_base()
    
    def load_knowledge_base(self, force_reload: bool = False):
        """Load and index documents from the knowledge base directory"""
        try:
            if not force_reload and self.vector_store:
                stats = self.vector_store.get_stats()
                if stats.get('total_documents', 0) > 0:
                    logger.info(f"Knowledge base already loaded: {stats}")
                    return
            
            chunk_size = int(os.getenv('CHUNK_SIZE', 700))
            chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 100))
            
            documents = self.document_loader.load_and_chunk_documents(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            if not documents:
                logger.warning("No documents found to load")
                return
            
            texts = [doc['text'] for doc in documents]
            metadatas = [doc['metadata'] for doc in documents]
            
            logger.info(f"Indexing {len(texts)} chunks...")
            embeddings = self.embedding_service.encode(texts)
            
            if self.vector_db_type == 'faiss':
                self.vector_store.add_documents(embeddings, texts, metadatas)
                self.vector_store.save()
            elif self.vector_db_type == 'chroma':
                self.vector_store.add_documents(embeddings.tolist(), texts, metadatas)
                
            logger.info(f"Success: {self.vector_store.get_stats()}")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {str(e)}", exc_info=True)

    def retrieve(self, query: str, conversation_history: list = None, top_k: int = None) -> Optional[str]:
        """
        Retrieve context with increased depth for policies and lists.
        """
        try:
            if not self.vector_store:
                return None
            
            # 1. Broad Search Detection
            # If the user asks for colors, lists, or policies, we pull more chunks.
            broad_keywords = ['list', 'all', 'every', 'color', 'refund', 'policy', 'return', 'exchange']
            is_broad_query = any(word in query.lower() for word in broad_keywords)
            
            # 2. Set Dynamic Top-K
            if top_k is None:
                base_k = int(os.getenv('TOP_K_RESULTS', 3))
                # Pull significantly more chunks (10-12) if a broad list/policy is requested
                top_k = base_k * 4 if is_broad_query else base_k
            
            threshold = float(os.getenv('SIMILARITY_THRESHOLD', 0.25))
            query_embedding = self.embedding_service.encode(query)
            
            # 3. Vector Search
            if self.vector_db_type == 'faiss':
                results = self.vector_store.search(query_embedding, top_k, threshold)
            elif self.vector_db_type == 'chroma':
                results = self.vector_store.search(query_embedding.tolist(), top_k, threshold)
            else:
                return None
            
            if not results:
                return None
            
            # 4. Format Context for the LLM
            context_parts = []
            for i, result in enumerate(results, 1):
                source = result.get('metadata', {}).get('filename', 'Catalog')
                text = result['text']
                context_parts.append(f"--- Document Snippet {i} (Source: {source}) ---\n{text}")
            
            logger.info(f"Retrieved {len(results)} chunks for query: {query}")
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Retrieval error: {str(e)}", exc_info=True)
            return None

    def add_document(self, text: str, metadata: Dict = None):
        """Add a single text entry manually to the index"""
        try:
            if not self.vector_store: return
            embedding = self.embedding_service.encode(text)
            
            if self.vector_db_type == 'faiss':
                self.vector_store.add_documents(embedding.reshape(1, -1), [text], [metadata])
                self.vector_store.save()
            elif self.vector_db_type == 'chroma':
                self.vector_store.add_documents([embedding.tolist()], [text], [metadata])
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")

    def get_stats(self) -> Dict:
        """Return the current number of indexed chunks"""
        return self.vector_store.get_stats() if self.vector_store else {'total_documents': 0}