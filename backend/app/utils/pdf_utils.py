"""
PDF processing utilities.
Handles PDF text extraction and chunking for RAG.
"""
import PyPDF2
import io
from typing import List, Dict


class PDFUtils:
    """Utilities for PDF processing."""
    
    @staticmethod
    def extract_text_from_pdf(file_data: bytes) -> List[Dict[str, any]]:
        """
        Extract text from PDF file.
        
        Args:
            file_data: PDF file content as bytes
            
        Returns:
            List of dicts with page_number and text
            
        Format:
            [
                {'page_number': 1, 'text': 'Page 1 content...'},
                {'page_number': 2, 'text': 'Page 2 content...'},
            ]
        """
        pages = []
        
        try:
            # Create PDF reader from bytes
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                
                pages.append({
                    'page_number': page_num,
                    'text': text.strip()
                })
            
            return pages
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def get_page_count(file_data: bytes) -> int:
        """
        Get number of pages in PDF.
        
        Args:
            file_data: PDF file content as bytes
            
        Returns:
            int: Number of pages
        """
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            return len(pdf_reader.pages)
            
        except Exception as e:
            raise Exception(f"Failed to read PDF: {str(e)}")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = start + chunk_size
            
            # Extract chunk
            chunk = text[start:end]
            
            # Add chunk if it has meaningful content
            if chunk.strip():
                chunks.append(chunk.strip())
            
            # Move start position (with overlap)
            start = end - chunk_overlap
            
            # Prevent infinite loop if chunk_overlap >= chunk_size
            if chunk_overlap >= chunk_size:
                start = end
        
        return chunks
    
    @staticmethod
    def chunk_pages(pages: List[Dict[str, any]], chunk_size: int = 1000, 
                    chunk_overlap: int = 200) -> List[Dict[str, any]]:
        """
        Chunk pages while preserving page numbers.
        
        Args:
            pages: List of page dicts from extract_text_from_pdf
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of chunk dicts with page_number, chunk_id, and text
            
        Format:
            [
                {'page_number': 1, 'chunk_id': 0, 'text': 'Chunk 1...'},
                {'page_number': 1, 'chunk_id': 1, 'text': 'Chunk 2...'},
                {'page_number': 2, 'chunk_id': 0, 'text': 'Chunk 3...'},
            ]
        """
        all_chunks = []
        
        for page in pages:
            page_number = page['page_number']
            text = page['text']
            
            # Chunk the page text
            chunks = PDFUtils.chunk_text(text, chunk_size, chunk_overlap)
            
            # Add page number and chunk ID to each chunk
            for chunk_id, chunk_text in enumerate(chunks):
                all_chunks.append({
                    'page_number': page_number,
                    'chunk_id': chunk_id,
                    'text': chunk_text
                })
        
        return all_chunks
