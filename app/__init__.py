"""
Flask application factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    """
    Application factory pattern
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from app.api.chat_routes   import chat_bp
    from app.api.health_routes import health_bp
    from app.api.stt_routes    import stt_bp        # ← ADD THIS

    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(chat_bp,   url_prefix='/api')
    app.register_blueprint(stt_bp)                  # ← ADD THIS (url_prefix already set in stt_routes.py)

    # Create tables
    with app.app_context():
        db.create_all()
    
    return app