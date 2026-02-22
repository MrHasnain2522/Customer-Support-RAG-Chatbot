"""
Chat Service with JSON storage for PostgreSQL
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
        Process chat message with JSON storage
        
        Args:
            user_id: User identifier
            message: User's message
            conversation_id: Optional conversation ID
            
        Returns:
            dict: Response data
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
            history = conversation.get_last_n_messages(5)
            
            # Retrieve context from RAG
            context = self.retriever.retrieve(message, history)
            
            # Extract sources
            sources = []
            if context:
                sources = self._extract_sources(context)
            
            # Generate response
            response = self.generator.generate(message, context, history)
            
            # Add assistant message to JSON
            conversation.add_message(
                role='assistant',
                content=response,
                context_used=bool(context),
                sources=sources
            )
            
            # Update title if first exchange
            if len(conversation.get_messages()) == 2:
                conversation.title = message[:50]
                db.session.commit()
            
            # Get current timestamp
            current_time = datetime.utcnow()
            
            logger.info(f"Processed message for conversation {conversation.conversation_id}")
            
            return {
                'response': response,
                'conversation_id': conversation.conversation_id,
                'timestamp': current_time,  # Return datetime object, not string
                'context_used': bool(context),
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise
    
    def _extract_sources(self, context: str):
        """Extract source information from context"""
        sources = []
        if not context:
            return sources
        
        # Parse: [Source 1: file.pdf (Relevance: 0.85)]
        pattern = r'\[Source \d+: (.+?) \(Relevance: ([\d.]+)\)\]'
        matches = re.findall(pattern, context)
        
        for filename, relevance in matches:
            sources.append({
                'filename': filename.strip(),
                'relevance': float(relevance)
            })
        
        return sources
    
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