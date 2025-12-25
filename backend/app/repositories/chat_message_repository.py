"""
ChatMessage repository.
Handles database operations for ChatMessage model.
"""
from sqlalchemy.orm import Session as DBSession
from app.models.chat_message import ChatMessage
from typing import List, Optional
from uuid import UUID


class ChatMessageRepository:
    """Repository for ChatMessage model operations."""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    def create(self, session_id: UUID, role: str, content: str, sources: dict = None) -> ChatMessage:
        """
        Create a new chat message.
        
        Args:
            session_id: Parent session ID
            role: 'user' or 'assistant'
            content: Message content
            sources: Source information (page numbers, chunks)
            
        Returns:
            ChatMessage: Created message object
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def get_by_id(self, message_id: UUID) -> Optional[ChatMessage]:
        """Get message by ID."""
        return self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    def get_by_session(self, session_id: UUID, limit: int = 100, offset: int = 0) -> List[ChatMessage]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session ID
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of messages ordered by created_at (oldest first for chat history)
        """
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_recent_messages(self, session_id: UUID, limit: int = 10) -> List[ChatMessage]:
        """
        Get recent messages for context.
        Used in RAG to maintain conversation context.
        """
        return (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )[::-1]  # Reverse to chronological order
    
    def delete(self, message_id: UUID) -> bool:
        """Delete a message."""
        message = self.get_by_id(message_id)
        
        if not message:
            return False
        
        self.db.delete(message)
        self.db.commit()
        
        return True
    
    def delete_by_session(self, session_id: UUID) -> int:
        """
        Delete all messages in a session.
        Returns count of deleted messages.
        """
        count = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .delete()
        )
        
        self.db.commit()
        
        return count
    
    def count_by_session(self, session_id: UUID) -> int:
        """Count total messages in session."""
        return self.db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()
