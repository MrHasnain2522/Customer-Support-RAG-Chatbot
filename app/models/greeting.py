"""
Greeting model with ID and timestamps
Replace: app/models/greeting.py
"""
from app import db
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, Text


class Greeting(db.Model):
    """Greeting model with ID and timestamps"""
    
    __tablename__ = 'greetings'
    
    # Primary key ID
    id = db.Column(Integer, primary_key=True, autoincrement=True)
    
    # Greeting data
    text = db.Column(Text, nullable=False)
    language = db.Column(String(10), default='en', nullable=False)
    category = db.Column(String(50), nullable=True)  # casual, formal, friendly
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Status
    is_active = db.Column(Boolean, default=True)
    
    # Usage tracking
    usage_count = db.Column(Integer, default=0)
    last_used_at = db.Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Greeting ID:{self.id} "{self.text[:30]}...">'
    
    def mark_used(self):
        """Mark greeting as used"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'text': self.text,
            'language': self.language,
            'category': self.category,
            'is_active': self.is_active,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None
        }
    
    def to_json(self):
        """Export as JSON"""
        return {
            'id': self.id,
            'text': self.text,
            'language': self.language,
            'category': self.category,
            'timestamp': self.created_at.isoformat() if self.created_at else None,
            'usage_count': self.usage_count
        }