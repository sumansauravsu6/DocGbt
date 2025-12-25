"""
Session repository.
Handles database operations for Session model.
"""
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from typing import List, Optional
from uuid import UUID


class SessionRepository:
    """Repository for Session model operations."""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    def create(self, document_id: UUID, title: str = "New Chat") -> Session:
        """
        Create a new chat session.
        
        Args:
            document_id: Parent document ID
            title: Session title (generated from first message)
            
        Returns:
            Session: Created session object
        """
        session = Session(
            document_id=document_id,
            title=title
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def get_by_id(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        return self.db.query(Session).filter(Session.id == session_id).first()
    
    def get_by_document(self, document_id: UUID, limit: int = 50, offset: int = 0) -> List[Session]:
        """
        Get all sessions for a document.
        
        Args:
            document_id: Document ID
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of sessions ordered by created_at (newest first)
        """
        return (
            self.db.query(Session)
            .filter(Session.document_id == document_id)
            .order_by(Session.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def update_title(self, session_id: UUID, title: str) -> Optional[Session]:
        """
        Update session title.
        Typically called after first user message.
        """
        session = self.get_by_id(session_id)
        
        if not session:
            return None
        
        session.title = title
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def delete(self, session_id: UUID) -> bool:
        """
        Delete session.
        Cascade deletes all messages.
        """
        session = self.get_by_id(session_id)
        
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        
        return True
    
    def count_by_document(self, document_id: UUID) -> int:
        """Count total sessions for document."""
        return self.db.query(Session).filter(Session.document_id == document_id).count()
    
    def get_with_messages(self, session_id: UUID) -> Optional[Session]:
        """
        Get session with all messages loaded.
        Uses eager loading for performance.
        """
        from sqlalchemy.orm import joinedload
        
        return (
            self.db.query(Session)
            .options(joinedload(Session.messages))
            .filter(Session.id == session_id)
            .first()
        )
