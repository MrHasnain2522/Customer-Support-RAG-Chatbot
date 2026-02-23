"""
Chat Service with JSON storage for PostgreSQL
Enhanced with source deduplication
Replace: app/services/chat_service.py
"""
import uuid
import re
from datetime import datetime
from app import db
from app.models.user import User
from app.models.conversation import Conversation
from app.rag.retriever import RAGRetriever
from app.rag.generator import ResponseGenerator
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service for handling chat operations with JSON storage"""
    
    def __init__(self):
        self.retriever = RAGRetriever()
        self.generator = ResponseGenerator()
    
    def process_message(self, user_id: str, message: str, conversation_id: str = None):
        """
        Process chat message with JSON storage and deduplicated sources
        
        Args:
            user_id: User identifier
            message: User's message
            conversation_id: Optional conversation ID
            
        Returns:
            dict: Response data (sources NOT exposed to frontend)
        """
        try:
            # Get or create user
            user = self._get_or_create_user(user_id)
            
            # Get or create conversation
            if conversation_id:
                conversation = Conversation.query.filter_by(
                    conversation_id=conversation_id
                ).first()
                if not conversation:
                    conversation = self._create_conversation(user_id)
            else:
                conversation = self._create_conversation(user_id)
            
            # Add user message to JSON
            conversation.add_message(
                role='user',
                content=message,
                context_used=False,
                sources=[]
            )
            
            # Get conversation history
            history = conversation.get_last_n_messages(10)  # Increased from 5 for better context
            
            # Retrieve context from RAG
            context = self.retriever.retrieve(message, history)
            
            # Log context for debugging
            logger.debug(f"RAW CONTEXT SAMPLE: {str(context)[:300] if context else 'None'}")
            
            # Extract and deduplicate sources (stored internally, NOT sent to frontend)
            sources = []
            if context:
                sources = self._extract_and_deduplicate_sources(context)
            
            # Generate response
            response = self.generator.generate(message, context, history)
            
            # Add assistant message to JSON with deduplicated sources (stored in DB only)
            conversation.add_message(
                role='assistant',
                content=response,
                context_used=bool(context),
                sources=sources  # Stored in DB for internal use, not returned to frontend
            )
            
            # Update title if first exchange
            if len(conversation.get_messages()) == 2:
                conversation.title = message[:50]
                db.session.commit()
            
            # Get current timestamp
            current_time = datetime.utcnow()
            
            logger.info(f"Processed message for conversation {conversation.conversation_id}")
            
            # FIX: 'sources' removed from response — PDF filenames no longer exposed to frontend
            return {
                'response': response,
                'conversation_id': conversation.conversation_id,
                'timestamp': current_time,
                'context_used': bool(context)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise
    
    def _extract_and_deduplicate_sources(self, context: str):
        """
        Extract source information from context and deduplicate by filename
        Keeps only the highest relevance score for each unique file
        
        Args:
            context: Retrieved context string with source citations
            
        Returns:
            list: Deduplicated sources sorted by relevance (max 3)
        """
        if not context:
            return []
        
        # Parse: [Source 1: file.pdf (Relevance: 0.85)]
        pattern = r'\[Source \d+: (.+?) \(Relevance: ([\d.]+)\)\]'
        matches = re.findall(pattern, context)
        
        # Dictionary to track highest relevance per file
        seen_files = {}
        
        for filename, relevance in matches:
            filename = filename.strip()
            relevance_score = float(relevance)
            
            # Keep only the highest relevance score for each file
            if filename not in seen_files:
                seen_files[filename] = relevance_score
            else:
                if relevance_score > seen_files[filename]:
                    seen_files[filename] = relevance_score
        
        # Convert to list of dicts and sort by relevance
        sources = [
            {'filename': filename, 'relevance': relevance}
            for filename, relevance in seen_files.items()
        ]
        
        # Sort by relevance (highest first) and limit to top 3
        sources = sorted(sources, key=lambda x: x['relevance'], reverse=True)[:3]
        
        logger.info(f"Deduplicated {len(matches)} sources to {len(sources)} unique sources")
        
        return sources
    
    def _extract_sources(self, context: str):
        """
        DEPRECATED: Use _extract_and_deduplicate_sources instead
        Legacy method kept for backward compatibility
        """
        return self._extract_and_deduplicate_sources(context)
    
    def get_conversation_history(self, conversation_id: str):
        """Get full conversation history"""
        try:
            conversation = Conversation.query.filter_by(
                conversation_id=conversation_id
            ).first()
            
            if not conversation:
                return {'error': 'Conversation not found'}
            
            return conversation.to_json()
            
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise
    
    def get_user_conversations(self, user_id: str):
        """Get all user conversations"""
        try:
            conversations = Conversation.query.filter_by(
                user_id=user_id,
                is_active=True
            ).order_by(Conversation.updated_at.desc()).all()
            
            return [conv.to_json() for conv in conversations]
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            raise
    
    def _get_or_create_user(self, user_id: str):
        """Get or create user"""
        user = User.query.filter_by(user_id=user_id).first()
        
        if not user:
            user = User(user_id=user_id)
            db.session.add(user)
            db.session.commit()
            logger.info(f"Created new user: {user_id}")
        
        return user
    
    def _create_conversation(self, user_id: str):
        """Create new conversation"""
        conversation = Conversation(
            conversation_id=str(uuid.uuid4()),
            user_id=user_id,
            messages_json=[],
            metadata_json={}
        )
        
        db.session.add(conversation)
        db.session.commit()
        logger.info(f"Created conversation: {conversation.conversation_id}")
        
        return conversation