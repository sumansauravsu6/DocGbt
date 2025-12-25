"""
ChatMessage model.
Represents individual chat messages in a session.
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.database import Base


class ChatMessage(Base):
    """
    ChatMessage model - represents a single message in a chat session.
    
    Messages can be from either 'user' or 'assistant'.
    Assistant messages include source references (page numbers).
    """
    __tablename__ = 'chat_messages'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to session
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Message information
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSONB)  # Store page numbers and chunk references as JSON
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name='check_role'),
    )
    
    # Relationships
    session = relationship('Session', back_populates='messages')
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'session_id': str(self.session_id),
            'role': self.role,
            'content': self.content,
            'sources': self.sources,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<ChatMessage(id='{self.id}', session_id='{self.session_id}', role='{self.role}')>"
