import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App configuration
    APP_NAME: str = "Anubodh AI Backend"
    API_V1_STR: str = "/api/v1"
    
    # Environment configs
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./anubodh.db"
    
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

# Force SQLite database to /tmp on Linux/Hugging Face to bypass any write permission limits
if os.name != 'nt' and "sqlite" in settings.DATABASE_URL:
    settings.DATABASE_URL = "sqlite+aiosqlite:////tmp/anubodh.db"
    print(f"Forced Linux SQLite database URL to: {settings.DATABASE_URL}")
elif settings.DATABASE_URL.startswith("sqlite+aiosqlite:///./"):
    core_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(core_dir))
    db_name = settings.DATABASE_URL.split("///./")[-1]
    settings.DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(backend_dir, db_name)}"
    print(f"Resolved database URL to: {settings.DATABASE_URL}")
