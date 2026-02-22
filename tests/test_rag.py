"""
Tests for RAG components
"""
import pytest
from app.rag.embeddings import EmbeddingService
from app.rag.retriever import RAGRetriever
from app.rag.generator import ResponseGenerator


class TestEmbeddingService:
    """Test Embedding Service"""
    
    def test_singleton_pattern(self):
        """Test that EmbeddingService follows singleton pattern"""
        service1 = EmbeddingService()
        service2 = EmbeddingService()
        assert service1 is service2
    
    def test_encode_single_text(self):
        """Test encoding single text"""
        service = EmbeddingService()
        text = "Hello world"
        
        embedding = service.encode(text)
        assert embedding is not None
        assert len(embedding.shape) == 2
        assert embedding.shape[0] == 1
    
    def test_encode_multiple_texts(self):
        """Test encoding multiple texts"""
        service = EmbeddingService()
        texts = ["Hello", "World", "Test"]
        
        embeddings = service.encode(texts)
        assert embeddings is not None
        assert embeddings.shape[0] == 3
    
    def test_compute_similarity(self):
        """Test similarity computation"""
        service = EmbeddingService()
        
        text1 = "Hello world"
        text2 = "Hi there"
        text3 = "Python programming"
        
        emb1 = service.encode(text1)[0]
        emb2 = service.encode(text2)[0]
        emb3 = service.encode(text3)[0]
        
        # Similar texts should have higher similarity
        sim_12 = service.compute_similarity(emb1, emb2)
        sim_13 = service.compute_similarity(emb1, emb3)
        
        # Greetings should be more similar than greeting vs programming
        assert sim_12 > sim_13


class TestRAGRetriever:
    """Test RAG Retriever"""
    
    def test_retriever_initialization(self):
        """Test retriever initialization"""
        retriever = RAGRetriever()
        assert retriever.knowledge_base is not None
        assert len(retriever.knowledge_base) > 0
    
    def test_retrieve_relevant_context(self):
        """Test retrieving relevant context"""
        retriever = RAGRetriever()
        
        query = "What is Python?"
        context = retriever.retrieve(query, top_k=2)
        
        # Should return context or None
        assert context is None or isinstance(context, str)
    
    def test_add_document(self):
        """Test adding document to knowledge base"""
        retriever = RAGRetriever()
        
        initial_count = len(retriever.knowledge_base)
        retriever.add_document("New document about AI")
        
        assert len(retriever.knowledge_base) == initial_count + 1
    
    def test_clear_knowledge_base(self):
        """Test clearing knowledge base"""
        retriever = RAGRetriever()
        
        retriever.clear_knowledge_base()
        assert len(retriever.knowledge_base) == 0
        assert retriever.embeddings is None


class TestResponseGenerator:
    """Test Response Generator"""
    
    def test_generator_initialization(self):
        """Test generator initialization"""
        generator = ResponseGenerator()
        assert generator is not None
    
    def test_generate_simple_response(self):
        """Test generating simple response"""
        generator = ResponseGenerator()
        
        query = "Hello"
        response = generator.generate(query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_with_context(self):
        """Test generating response with context"""
        generator = ResponseGenerator()
        
        query = "What is Flask?"
        context = "Flask is a lightweight web framework for Python."
        response = generator.generate(query, context=context)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_with_history(self):
        """Test generating response with conversation history"""
        generator = ResponseGenerator()
        
        query = "Tell me more"
        history = [
            {'role': 'user', 'content': 'What is Python?'},
            {'role': 'assistant', 'content': 'Python is a programming language.'}
        ]
        
        response = generator.generate(query, conversation_history=history)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0