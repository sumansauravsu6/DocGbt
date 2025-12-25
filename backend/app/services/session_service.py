"""
Session service.
Handles chat session management.
"""
from sqlalchemy.orm import Session as DBSession
from app.repositories.session_repository import SessionRepository
from app.repositories.document_repository import DocumentRepository
from uuid import UUID


class SessionService:
    """Service for session operations."""
    
    def __init__(self, db: DBSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.document_repo = DocumentRepository(db)
    
    def create_session(self, document_id: UUID, user_id: str, title: str = "New Chat"):
        """
        Create a new chat session.
        
        Args:
            document_id: Parent document ID
            user_id: User ID (for ownership verification)
            title: Session title
            
        Returns:
            Session object
        """
        # Verify document ownership
        if not self.document_repo.check_ownership(document_id, user_id):
            raise PermissionError("You do not have permission to create sessions for this document")
        
        # Create session
        session = self.session_repo.create(document_id, title)
        
        return session
    
    def get_document_sessions(self, document_id: UUID, user_id: str, limit: int = 50, offset: int = 0):
        """
        Get all sessions for a document.
        Verifies ownership.
        """
        # Verify document ownership
        if not self.document_repo.check_ownership(document_id, user_id):
            raise PermissionError("You do not have permission to access this document")
        
        return self.session_repo.get_by_document(document_id, limit, offset)
    
    def get_session(self, session_id: UUID, user_id: str):
        """
        Get session by ID.
        Verifies ownership through document.
        """
        session = self.session_repo.get_by_id(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        # Verify ownership
        if not self.document_repo.check_ownership(session.document_id, user_id):
            raise PermissionError("You do not have permission to access this session")
        
        return session
    
    def update_session_title(self, session_id: UUID, user_id: str, title: str):
        """
        Update session title.
        Typically called after first user message.
        """
        # Verify ownership
        session = self.get_session(session_id, user_id)
        
        # Update title
        return self.session_repo.update_title(session_id, title)
    
    def delete_session(self, session_id: UUID, user_id: str):
        """
        Delete session.
        Cascades to all messages.
        """
        # Verify ownership
        self.get_session(session_id, user_id)
        
        # Delete
        return self.session_repo.delete(session_id)
    
    def generate_session_title(self, first_message: str, max_length: int = 50) -> str:
        """
        Generate session title from first user message.
        
        Args:
            first_message: First user message
            max_length: Maximum title length
            
        Returns:
            Generated title
        """
        # Simple implementation: use first N characters
        # In production, you might use an LLM to generate a better title
        title = first_message.strip()
        
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
        
        return title if title else "New Chat"
