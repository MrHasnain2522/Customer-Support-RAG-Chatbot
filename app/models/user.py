"""
User model for PostgreSQL
Replace: app/models/user.py
"""
from app import db
from datetime import datetime
from sqlalchemy import String, Integer, DateTime


class User(db.Model):
    """User model"""
    
    __tablename__ = 'users'
    
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(100), unique=True, nullable=False, index=True)
    username = db.Column(String(100), nullable=True)
    email = db.Column(String(120), nullable=True)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.user_id}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }