"""
User model.
Represents users authenticated via Clerk.
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User model - stores Clerk user information.
    
    Note: Authentication is handled by Clerk.
    This model stores user metadata and relationships.
    """
    __tablename__ = 'users'
    
    # Primary key is Clerk user_id
    id = Column(String(255), primary_key=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    documents = relationship('Document', back_populates='user', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"
