"""
Session model.
Represents chat sessions for a document.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class Session(Base):
    """
    Session model - represents a chat session for a document.
    
    Each document can have multiple sessions, similar to ChatGPT's "New Chat".
    Sessions provide isolated conversation history.
    """
    __tablename__ = 'sessions'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to document
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Session information
    title = Column(String(500), nullable=False, default='New Chat')
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    document = relationship('Document', back_populates='sessions')
    messages = relationship('ChatMessage', back_populates='session', cascade='all, delete-orphan', order_by='ChatMessage.created_at')
    
    def to_dict(self, include_messages=False):
        """Convert model to dictionary for JSON serialization."""
        data = {
            'id': str(self.id),
            'document_id': str(self.document_id),
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_messages:
            data['messages'] = [message.to_dict() for message in self.messages]
            data['message_count'] = len(self.messages)
        
        return data
    
    def __repr__(self):
        return f"<Session(id='{self.id}', document_id='{self.document_id}', title='{self.title}')>"
