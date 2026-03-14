"""
Application configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # ── Flask ──────────────────────────────────
    SECRET_KEY  = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG       = os.getenv("DEBUG", "True").lower() == "true"

    # ── Database ───────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///instance/app.db"
    ).replace("postgres://", "postgresql://")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO                = False

    # ── API Keys ───────────────────────────────
    OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

    # ── RAG Configuration ──────────────────────
    EMBEDDING_MODEL    = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")  # ✅ OpenAI
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 4000))

    # ── CORS ───────────────────────────────────
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG           = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration — Railway"""
    DEBUG           = False
    SQLALCHEMY_ECHO = False

    # ✅ Force PostgreSQL on Railway
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        ""
    ).replace("postgres://", "postgresql://")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING                 = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///instance/test.db"


# Config dictionary
config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
    "default":     DevelopmentConfig
}