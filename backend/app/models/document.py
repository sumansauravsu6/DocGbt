"""
Document model.
Represents uploaded documents (each document is a DocGPT).
"""
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class Document(Base):
    """
    Document model - each uploaded document becomes a DocGPT.
    
    Stores document metadata and references to the file in Supabase Storage.
    """
    __tablename__ = 'documents'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to user
    user_id = Column(String(255), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Document information
    name = Column(String(500), nullable=False)
    file_url = Column(Text, nullable=False)  # Supabase Storage URL
    file_size = Column(BigInteger)  # File size in bytes
    page_count = Column(Integer)  # Number of pages
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='documents')
    sessions = relationship('Session', back_populates='document', cascade='all, delete-orphan')
    
    def to_dict(self, include_sessions=False):
        """Convert model to dictionary for JSON serialization."""
        data = {
            'id': str(self.id),
            'user_id': self.user_id,
            'name': self.name,
            'file_url': self.file_url,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sessions:
            data['sessions'] = [session.to_dict() for session in self.sessions]
        
        return data
    
    def __repr__(self):
        return f"<Document(id='{self.id}', name='{self.name}', user_id='{self.user_id}')>"
