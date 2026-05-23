import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App configuration
    APP_NAME: str = "Aethera AI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Environment configs
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./aethera.db"
    
    # JWT security configs
    JWT_SECRET_KEY: str = "supersecret_default_key_for_development_replace_this_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Gemini model configurations
    MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"
    
    # Groq configurations
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Vector DB
    QDRANT_URL: str = "memory"  # Use "memory" for zero-config in-memory Qdrant client
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def _get_env_file() -> str:
    # Check current directory
    if os.path.exists(".env"):
        return ".env"
    # Check one level up
    if os.path.exists("../.env"):
        return "../.env"
    # Check relative to config.py (3 levels up - inside backend/)
    path_3 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    if os.path.exists(path_3):
        return path_3
    # Check relative to config.py (4 levels up - root of workspace)
    path_4 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
    if os.path.exists(path_4):
        return path_4
    return path_3

settings = Settings(_env_file=_get_env_file())
