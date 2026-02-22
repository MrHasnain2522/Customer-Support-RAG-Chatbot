"""
Database configuration and utilities
"""
from app import db
from app.utils.logger import get_logger

logger = get_logger(__name__)


def init_db(app):
    """
    Initialize database
    Creates all tables if they don't exist
    """
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from app.models import User, Conversation, Message, Greeting
            
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise


def drop_db(app):
    """
    Drop all database tables
    WARNING: This will delete all data!
    """
    with app.app_context():
        try:
            db.drop_all()
            logger.warning("All database tables dropped")
            
        except Exception as e:
            logger.error(f"Error dropping database: {str(e)}")
            raise


def reset_db(app):
    """
    Reset database (drop and recreate)
    WARNING: This will delete all data!
    """
    drop_db(app)
    init_db(app)
    logger.info("Database reset complete")