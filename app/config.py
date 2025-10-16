from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    
    # Application Configuration
    app_name: str = "Document QA API"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Default credentials
    default_username: str = "admin"
    default_password: str = "admin123"
    
    # Model Configuration
    embedding_model: str = "text-embedding-ada-002"
    llm_model: str = "gpt-4-turbo-preview"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Vector Store Configuration
    vector_store_path: str = "./data/vector_store"
    documents_path: str = "./data/documents"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Create necessary directories
def create_directories():
    settings = get_settings()
    os.makedirs(settings.vector_store_path, exist_ok=True)
    os.makedirs(settings.documents_path, exist_ok=True)
    os.makedirs("./app/static", exist_ok=True)