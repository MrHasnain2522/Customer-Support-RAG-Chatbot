"""
Message model for PostgreSQL
Replace: app/models/message.py
"""
from app import db
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, Text, LargeBinary


class Message(db.Model):
    """Message model"""
    
    __tablename__ = 'messages'
    
    id = db.Column(Integer, primary_key=True)
    conversation_id = db.Column(String(100), db.ForeignKey('conversations.conversation_id'), nullable=False, index=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False, index=True)
    
    role = db.Column(String(20), nullable=False)  # user or assistant
    content = db.Column(Text, nullable=False)
    
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    context_used = db.Column(Boolean, default=False)
    embedding = db.Column(LargeBinary, nullable=True)
    
    def __repr__(self):
        return f'<Message {self.id} from {self.role}>'
    
    @classmethod
    def create_user_message(cls, conversation_id, user_id, content):
        """Create a user message"""
        message = cls(
            conversation_id=conversation_id,
            user_id=user_id,
            role='user',
            content=content,
            context_used=False
        )
        return message
    
    @classmethod
    def create_assistant_message(cls, conversation_id, user_id, content, context_used=False):
        """Create an assistant message"""
        message = cls(
            conversation_id=conversation_id,
            user_id=user_id,
            role='assistant',
            content=content,
            context_used=context_used
        )
        return message
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'context_used': self.context_used
        }