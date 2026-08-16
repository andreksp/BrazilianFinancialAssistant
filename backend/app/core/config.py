"""
Configuration settings for the Brazilian Financial Assistant application.
Uses pydantic-settings for environment variable management.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS
    FRONTEND_URL: str = "http://localhost:4200"
    CORS_ORIGINS: List[str] = ["http://localhost:4200", "http://localhost:3000", "http://localhost:8501"]

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # LLM Configuration
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL_PARSER: str = "claude-haiku-4-5-20251001"
    LLM_MODEL_EXPLAINER: str = "claude-sonnet-4-6"

    # ChromaDB
    CHROMA_DB_PATH: str = "./chroma_data"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
