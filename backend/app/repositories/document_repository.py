"""
Document repository.
Handles database operations for Document model.
"""
from sqlalchemy.orm import Session
from app.models.document import Document
from typing import List, Optional
from uuid import UUID


class DocumentRepository:
    """Repository for Document model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: str, name: str, file_url: str, 
               file_size: int = None, page_count: int = None) -> Document:
        """
        Create a new document.
        
        Args:
            user_id: Owner user ID
            name: Document name
            file_url: Supabase Storage URL
            file_size: File size in bytes
            page_count: Number of pages
            
        Returns:
            Document: Created document object
        """
        document = Document(
            user_id=user_id,
            name=name,
            file_url=file_url,
            file_size=file_size,
            page_count=page_count
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def get_by_id(self, document_id: UUID) -> Optional[Document]:
        """Get document by ID."""
        return self.db.query(Document).filter(Document.id == document_id).first()
    
    def get_by_user(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Document]:
        """
        Get all documents for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of documents ordered by created_at (newest first)
        """
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def check_ownership(self, document_id: UUID, user_id: str) -> bool:
        """
        Check if user owns document.
        Important for authorization.
        """
        document = self.get_by_id(document_id)
        return document is not None and document.user_id == user_id
    
    def update(self, document_id: UUID, **kwargs) -> Optional[Document]:
        """
        Update document fields.
        
        Args:
            document_id: Document ID
            **kwargs: Fields to update
            
        Returns:
            Updated document or None
        """
        document = self.get_by_id(document_id)
        
        if not document:
            return None
        
        # Update allowed fields
        allowed_fields = {'name', 'file_url', 'file_size', 'page_count'}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(document, key, value)
        
        self.db.commit()
        self.db.refresh(document)
        
        return document
    
    def delete(self, document_id: UUID) -> bool:
        """
        Delete document.
        Cascade deletes sessions and messages.
        """
        document = self.get_by_id(document_id)
        
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        
        return True
    
    def count_by_user(self, user_id: str) -> int:
        """Count total documents for user."""
        return self.db.query(Document).filter(Document.user_id == user_id).count()
