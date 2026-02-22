"""
Greeting service for managing greetings
"""
from app import db
from app.models import Greeting
from app.utils.logger import get_logger
import random

logger = get_logger(__name__)


class GreetingService:
    """Service for managing greetings"""
    
    def get_all_greetings(self, language=None, category=None, active_only=True):
        """
        Get all greetings with optional filters
        
        Args:
            language: Filter by language
            category: Filter by category
            active_only: Only return active greetings
            
        Returns:
            list: List of greeting dictionaries
        """
        query = Greeting.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        if language:
            query = query.filter_by(language=language)
        if category:
            query = query.filter_by(category=category)
        
        greetings = query.all()
        return [greeting.to_dict() for greeting in greetings]
    
    def get_greeting_by_id(self, greeting_id):
        """Get a specific greeting by ID"""
        greeting = Greeting.query.get(greeting_id)
        return greeting.to_dict() if greeting else None
    
    def create_greeting(self, text, language='en', category=None):
        """
        Create a new greeting
        
        Args:
            text: Greeting text
            language: Language code
            category: Greeting category
            
        Returns:
            dict: Created greeting
        """
        try:
            greeting = Greeting(
                text=text,
                language=language,
                category=category
            )
            db.session.add(greeting)
            db.session.commit()
            
            logger.info(f"Created greeting: {greeting.id}")
            return greeting.to_dict()
            
        except Exception as e:
            logger.error(f"Error creating greeting: {str(e)}")
            db.session.rollback()
            raise
    
    def update_greeting(self, greeting_id, **kwargs):
        """Update a greeting"""
        greeting = Greeting.query.get(greeting_id)
        if not greeting:
            return None
        
        try:
            for key, value in kwargs.items():
                if hasattr(greeting, key):
                    setattr(greeting, key, value)
            
            db.session.commit()
            logger.info(f"Updated greeting: {greeting_id}")
            return greeting.to_dict()
            
        except Exception as e:
            logger.error(f"Error updating greeting: {str(e)}")
            db.session.rollback()
            raise
    
    def delete_greeting(self, greeting_id):
        """Delete a greeting"""
        greeting = Greeting.query.get(greeting_id)
        if not greeting:
            return False
        
        try:
            db.session.delete(greeting)
            db.session.commit()
            logger.info(f"Deleted greeting: {greeting_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting greeting: {str(e)}")
            db.session.rollback()
            raise
    
    def get_random_greeting(self, language='en', category=None):
        """Get a random greeting"""
        greetings = self.get_all_greetings(language=language, category=category)
        
        if not greetings:
            return {'text': 'Hello!', 'language': 'en', 'category': 'default'}
        
        return random.choice(greetings)