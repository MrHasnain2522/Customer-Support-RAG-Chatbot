"""
Database initialization script
Run this to initialize the database with tables and seed data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app import db as database
from app.utils.logger import get_logger

logger = get_logger(__name__)


def init_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Import models to register them
            from app.models.user import User
            from app.models.conversation import Conversation
            from app.models.message import Message
            from app.models.greeting import Greeting
            
            # Create all tables
            database.create_all()
            logger.info("Database tables created successfully")
            
            # Seed initial data
            seed_greetings()
            
            logger.info("Database initialization complete")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise


def seed_greetings():
    """Seed initial greetings"""
    try:
        from app.models.greeting import Greeting
        
        # Check if greetings already exist
        count = Greeting.query.count()
        if count > 0:
            logger.info(f"Greetings already exist ({count}). Skipping seed.")
            return
        
        # Create initial greetings
        greetings = [
            Greeting(text="Hello! How can I help you today?", language="en", category="casual"),
            Greeting(text="Hi there! What can I do for you?", language="en", category="casual"),
            Greeting(text="Good day! How may I assist you?", language="en", category="formal"),
            Greeting(text="Welcome! What brings you here today?", language="en", category="friendly"),
            Greeting(text="Greetings! How can I be of service?", language="en", category="formal"),
        ]
        
        for greeting in greetings:
            database.session.add(greeting)
        
        database.session.commit()
        logger.info(f"Seeded {len(greetings)} greetings")
        
    except Exception as e:
        logger.error(f"Error seeding greetings: {str(e)}")
        database.session.rollback()
        raise


def clear_database():
    """Clear all data from database (keeps tables)"""
    app = create_app()
    
    with app.app_context():
        try:
            from app.models.user import User
            from app.models.conversation import Conversation
            from app.models.message import Message
            from app.models.greeting import Greeting
            
            # Delete all records
            Message.query.delete()
            Conversation.query.delete()
            User.query.delete()
            Greeting.query.delete()
            
            database.session.commit()
            logger.info("Database cleared successfully")
            
        except Exception as e:
            logger.error(f"Error clearing database: {str(e)}")
            database.session.rollback()
            raise


if __name__ == '__main__':
    init_database()