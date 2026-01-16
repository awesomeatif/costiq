"""
CostIQ Application Configuration

This module handles all application settings using Pydantic Settings.
Settings can be overridden via environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings with sensible defaults for local development.
    All settings can be overridden via environment variables.
    """
    
    # Application Info
    APP_NAME: str = "CostIQ"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # Database Settings
    # Using SQLite for local development as specified
    # For production, switch to PostgreSQL
    DATABASE_URL: str = "sqlite:///./costiq.db"
    
    # File Upload Settings
    # Maximum file size in bytes (10MB default)
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    # Allowed file types for upload
    ALLOWED_EXTENSIONS: list = [".csv"]
    # Directory to store uploaded files temporarily
    UPLOAD_DIR: str = "uploads"
    
    # Security Settings (for future auth implementation)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        # Allow reading from .env file
        env_file = ".env"
        case_sensitive = True


# Global settings instance
# This is imported throughout the application
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency injection helper to get settings.
    Useful for testing where settings might be mocked.
    """
    return settings
