"""
Document service.
Handles document upload, processing, and management.
"""
from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository
from app.repositories.user_repository import UserRepository
from app.utils.file_utils import FileUtils
from app.utils.pdf_utils import PDFUtils
from app.config import Config
from uuid import UUID
from typing import List


class DocumentService:
    """
    Service for document operations.
    
    Orchestrates document upload, PDF processing, and embedding generation.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.user_repo = UserRepository(db)
        self.file_utils = FileUtils()
        self.pdf_utils = PDFUtils()
        self._vector_service = None
    
    @property
    def vector_service(self):
        """Lazy load VectorService only when needed"""
        if self._vector_service is None:
            from app.services.vector_service import VectorService
            self._vector_service = VectorService()
        return self._vector_service
    
    def upload_document(self, user_id: str, file_data: bytes, filename: str):
        """
        Upload and process a document.
        
        Workflow:
        1. Validate file
        2. Upload to Supabase Storage
        3. Extract text from PDF
        4. Create document record
        5. Generate embeddings and store in ChromaDB
        
        Args:
            user_id: User ID
            file_data: File content as bytes
            filename: Original filename
            
        Returns:
            Document object
        """
        # Validate file type
        if not self.file_utils.allowed_file(filename):
            raise ValueError("Only PDF files are allowed")
        
        # Get file metadata
        file_size = self.file_utils.get_file_size(file_data)
        page_count = self.pdf_utils.get_page_count(file_data)
        
        # Upload to Supabase Storage
        file_url = self.file_utils.upload_to_supabase(file_data, filename, user_id)
        
        # Create document record
        document = self.document_repo.create(
            user_id=user_id,
            name=filename,
            file_url=file_url,
            file_size=file_size,
            page_count=page_count
        )
        
        # Extract text and generate embeddings
        try:
            # Extract text from PDF
            pages = self.pdf_utils.extract_text_from_pdf(file_data)
            
            # Chunk pages
            chunks = self.pdf_utils.chunk_pages(
                pages,
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP
            )
            
            # Add to vector database
            self.vector_service.add_document_chunks(document.id, chunks)
            
        except Exception as e:
            # If embedding fails, delete document and raise error
            self.document_repo.delete(document.id)
            self.file_utils.delete_from_supabase(file_url)
            raise Exception(f"Failed to process document: {str(e)}")
        
        return document
    
    def get_user_documents(self, user_id: str, limit: int = 100, offset: int = 0):
        """Get all documents for a user."""
        return self.document_repo.get_by_user(user_id, limit, offset)
    
    def get_document(self, document_id: UUID, user_id: str):
        """
        Get document by ID.
        Verifies ownership.
        """
        document = self.document_repo.get_by_id(document_id)
        
        if not document:
            raise ValueError("Document not found")
        
        # Verify ownership
        if document.user_id != user_id:
            raise PermissionError("You do not have permission to access this document")
        
        return document
    
    def delete_document(self, document_id: UUID, user_id: str):
        """
        Delete document.
        
        Workflow:
        1. Verify ownership
        2. Delete from vector database
        3. Delete from Supabase Storage
        4. Delete from database (cascades to sessions and messages)
        """
        document = self.get_document(document_id, user_id)
        
        # Delete embeddings from ChromaDB
        self.vector_service.delete_document_chunks(document_id)
        
        # Delete file from storage
        self.file_utils.delete_from_supabase(document.file_url)
        
        # Delete from database (cascades)
        self.document_repo.delete(document_id)
        
        return True
    
    def count_user_documents(self, user_id: str) -> int:
        """Count total documents for user."""
        return self.document_repo.count_by_user(user_id)
