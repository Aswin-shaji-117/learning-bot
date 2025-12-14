from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    APP_NAME: str = "RAG Subject Chatbot"
    APP_VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    
    # Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "google/flan-t5-base"
    
    # Document Processing
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    MAX_FILE_SIZE_MB: int = 10
    
    # Directories
    UPLOAD_DIR: str = "./uploads"
    



settings = Settings()
