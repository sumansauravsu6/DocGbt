"""
Database initialization and session management.
Configures SQLAlchemy with Supabase PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config import Config
import re

# Create base class for declarative models
Base = declarative_base()

# Global session maker
SessionLocal = None
engine = None


def get_database_url():
    """
    Get database URL from Config.
    If DATABASE_URL is set, use it directly.
    Otherwise, fall back to constructing from Supabase URL (not recommended for production).
    """
    # Check if DATABASE_URL is provided (recommended)
    if hasattr(Config, 'DATABASE_URL') and Config.DATABASE_URL:
        return Config.DATABASE_URL
    
    # Fallback: Use Supabase REST API (no direct database connection)
    # For now, return None to skip database initialization
    return None


def init_db():
    """Initialize database connection and create tables."""
    global SessionLocal, engine
    
    try:
        database_url = get_database_url()
        
        # Skip database initialization if no URL provided
        if not database_url:
            print("⚠️  No DATABASE_URL configured - skipping direct database connection")
            print("   The app will use Supabase REST API for data operations")
            return
        
        # Create engine with connection pooling
        engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,  # Verify connections before using
            echo=Config.DEBUG  # Log SQL queries in debug mode
        )
        
        # Create session factory
        SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        raise


def get_db():
    """
    Get database session.
    Use this as a dependency in routes.
    Automatically handles session cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_db():
    """Close database connections."""
    if SessionLocal:
        SessionLocal.remove()
    if engine:
        engine.dispose()
