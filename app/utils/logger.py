"""
Logging configuration
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def get_logger(name: str):
    """
    Get configured logger
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        # File handler (optional)
        log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
                
                file_handler = RotatingFileHandler(
                    os.path.join(log_dir, 'app.log'),
                    maxBytes=10485760,  # 10MB
                    backupCount=5
                )
                file_handler.setLevel(logging.INFO)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except Exception:
                # If can't create log directory, just use console logging
                pass
    
    return logger