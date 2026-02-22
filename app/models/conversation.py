"""
Conversation model with JSON storage for PostgreSQL
Replace: app/models/conversation.py
"""
from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Boolean, Integer, DateTime


class Conversation(db.Model):
    """Conversation model with JSON storage"""
    
    __tablename__ = 'conversations'
    
    id = db.Column(Integer, primary_key=True)
    conversation_id = db.Column(String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(String(100), db.ForeignKey('users.user_id'), nullable=False, index=True)
    title = db.Column(String(200), nullable=True)
    
    # JSON storage for entire conversation
    messages_json = db.Column(JSONB, default=list)  # All messages in JSON
    metadata_json = db.Column(JSONB, default=dict)  # Metadata
    
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Conversation {self.conversation_id}>'
    
    def add_message(self, role: str, content: str, context_used: bool = False, sources: list = None):
        """Add message to JSON array"""
        message = {
            'id': len(self.messages_json) + 1 if self.messages_json else 1,
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'context_used': context_used,
            'sources': sources or []
        }
        
        # Initialize if None
        if self.messages_json is None:
            self.messages_json = []
        
        # Append message
        messages = list(self.messages_json)
        messages.append(message)
        self.messages_json = messages
        
        # Update metadata
        self.update_metadata()
        db.session.commit()
    
    def update_metadata(self):
        """Update conversation metadata"""
        if self.metadata_json is None:
            self.metadata_json = {}
        
        metadata = dict(self.metadata_json)
        metadata['total_messages'] = len(self.messages_json) if self.messages_json else 0
        metadata['last_updated'] = datetime.utcnow().isoformat()
        self.metadata_json = metadata
    
    def get_messages(self):
        """Get all messages"""
        return self.messages_json or []
    
    def get_last_n_messages(self, n: int = 10):
        """Get last N messages"""
        messages = self.messages_json or []
        return messages[-n:] if len(messages) > n else messages
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': self.messages_json or [],
            'metadata': self.metadata_json or {},
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_json(self):
        """Export as JSON"""
        return {
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'title': self.title,
            'messages': self.messages_json or [],
            'metadata': self.metadata_json or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }