"""
Application configuration module.
Centralizes all environment variables and configuration settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class with all application settings."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Supabase settings
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
    SUPABASE_STORAGE_BUCKET = os.getenv('SUPABASE_STORAGE_BUCKET', 'document')
    
    # Database (optional - if you want direct PostgreSQL access)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Clerk authentication settings
    CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY')
    CLERK_PUBLISHABLE_KEY = os.getenv('CLERK_PUBLISHABLE_KEY')
    
    # Qdrant settings
    QDRANT_URL = os.getenv('QDRANT_URL')
    QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
    QDRANT_COLLECTION_NAME = os.getenv('QDRANT_COLLECTION_NAME', 'document_chunks')
    
    # Groq AI settings
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # RAG settings
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300
    TOP_K_RESULTS = 8
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:5174,http://localhost:3000')
    
    @staticmethod
    def validate():
        """Validate that all required environment variables are set."""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'CLERK_SECRET_KEY'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file."
            )
