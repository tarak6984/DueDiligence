"""Configuration management for the application."""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Configuration
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY")
    GROK_API_BASE: str = os.getenv("GROK_API_BASE", "https://api.x.ai/v1")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server Configuration
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Storage Configuration
    STORAGE_DIR: Path = Path(os.getenv("STORAGE_DIR", "data/storage"))
    DB_DIR: Path = Path(os.getenv("DB_DIR", "data/db"))
    VECTOR_DIR: Path = Path(os.getenv("VECTOR_DIR", "data/vectors"))
    
    # Processing Settings
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
    CITATION_CHUNK_SIZE: int = int(os.getenv("CITATION_CHUNK_SIZE", "300"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Model Settings
    GROK_MODEL: str = "grok-beta"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000
    
    @classmethod
    def has_grok_api(cls) -> bool:
        """Check if Grok API key is configured."""
        return cls.GROK_API_KEY is not None and len(cls.GROK_API_KEY) > 0


config = Config()
