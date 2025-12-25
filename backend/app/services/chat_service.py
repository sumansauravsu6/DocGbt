"""
Chat service.
Handles chat operations and message management.
"""
from sqlalchemy.orm import Session as DBSession
from app.repositories.chat_message_repository import ChatMessageRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.document_repository import DocumentRepository
from app.services.session_service import SessionService
from uuid import UUID
from typing import List, Dict


class ChatService:
    """
    Service for chat operations.
    
    Orchestrates RAG and message storage.
    """
    
    def __init__(self, db: DBSession):
        self.db = db
        self.message_repo = ChatMessageRepository(db)
        self.session_repo = SessionRepository(db)
        self.document_repo = DocumentRepository(db)
        self._rag_service = None
        self.session_service = SessionService(db)
    
    @property
    def rag_service(self):
        """Lazy load RAGService only when needed"""
        if self._rag_service is None:
            from app.services.rag_service import RAGService
            self._rag_service = RAGService()
        return self._rag_service
    
    def send_message(self, session_id: UUID, user_id: str, message: str) -> Dict:
        """
        Send a message and get AI response.
        
        Workflow:
        1. Verify session ownership
        2. Save user message
        3. Get conversation history
        4. Generate AI response using RAG
        5. Save AI response
        6. Update session title if first message
        
        Args:
            session_id: Session ID
            user_id: User ID
            message: User message content
            
        Returns:
            Dict with user message and AI response
        """
        # Verify session ownership
        session = self.session_repo.get_by_id(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        if not self.document_repo.check_ownership(session.document_id, user_id):
            raise PermissionError("You do not have permission to access this session")
        
        # Save user message
        user_message = self.message_repo.create(
            session_id=session_id,
            role='user',
            content=message
        )
        
        # Get conversation history (excluding the message we just saved)
        history_messages = self.message_repo.get_recent_messages(session_id, limit=10)
        conversation_history = [msg.to_dict() for msg in history_messages[:-1]]  # Exclude current
        
        # Generate AI response using RAG
        rag_result = self.rag_service.chat(
            query=message,
            document_id=session.document_id,
            conversation_history=conversation_history
        )
        
        # Save AI response
        assistant_message = self.message_repo.create(
            session_id=session_id,
            role='assistant',
            content=rag_result['answer'],
            sources=rag_result.get('sources')
        )
        
        # Update session title if this is the first user message
        if self.message_repo.count_by_session(session_id) == 2:  # 1 user + 1 assistant = first exchange
            title = self.session_service.generate_session_title(message)
            self.session_repo.update_title(session_id, title)
        
        return {
            'user_message': user_message.to_dict(),
            'assistant_message': assistant_message.to_dict()
        }
    
    def get_session_messages(self, session_id: UUID, user_id: str, 
                            limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Get all messages for a session.
        Verifies ownership.
        """
        # Verify session ownership
        session = self.session_repo.get_by_id(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        if not self.document_repo.check_ownership(session.document_id, user_id):
            raise PermissionError("You do not have permission to access this session")
        
        # Get messages
        messages = self.message_repo.get_by_session(session_id, limit, offset)
        
        return [msg.to_dict() for msg in messages]
    
    def delete_message(self, message_id: UUID, user_id: str):
        """Delete a message (with ownership verification)."""
        message = self.message_repo.get_by_id(message_id)
        
        if not message:
            raise ValueError("Message not found")
        
        # Verify ownership through session and document
        session = self.session_repo.get_by_id(message.session_id)
        if not session or not self.document_repo.check_ownership(session.document_id, user_id):
            raise PermissionError("You do not have permission to delete this message")
        
        return self.message_repo.delete(message_id)
    
    def clear_session_history(self, session_id: UUID, user_id: str):
        """Clear all messages in a session."""
        # Verify ownership
        session = self.session_repo.get_by_id(session_id)
        
        if not session:
            raise ValueError("Session not found")
        
        if not self.document_repo.check_ownership(session.document_id, user_id):
            raise PermissionError("You do not have permission to modify this session")
        
        return self.message_repo.delete_by_session(session_id)
