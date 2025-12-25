"""
File utilities for handling uploads and storage.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from supabase import create_client
from app.config import Config


class FileUtils:
    """Utilities for file handling and Supabase Storage operations."""
    
    def __init__(self):
        # Use service_role key for storage operations to bypass RLS
        storage_key = Config.SUPABASE_SERVICE_KEY or Config.SUPABASE_KEY
        self.supabase = create_client(Config.SUPABASE_URL, storage_key)
        self.bucket_name = Config.SUPABASE_STORAGE_BUCKET
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of file to check
            
        Returns:
            bool: True if file type is allowed
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def generate_unique_filename(original_filename: str) -> str:
        """
        Generate unique filename to avoid collisions.
        
        Args:
            original_filename: Original uploaded filename
            
        Returns:
            str: Unique filename with UUID prefix
        """
        # Secure the filename
        filename = secure_filename(original_filename)
        
        # Generate UUID prefix
        unique_id = str(uuid.uuid4())
        
        # Combine UUID with original filename
        name, ext = os.path.splitext(filename)
        return f"{unique_id}_{name}{ext}"
    
    def upload_to_supabase(self, file_data: bytes, filename: str, user_id: str) -> str:
        """
        Upload file to Supabase Storage.
        
        Args:
            file_data: File content as bytes
            filename: Name of file
            user_id: User ID for organizing files
            
        Returns:
            str: Public URL of uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            # Generate unique filename
            unique_filename = self.generate_unique_filename(filename)
            
            # Create file path with user_id for organization
            file_path = f"{user_id}/{unique_filename}"
            
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(self.bucket_name).upload(
                file_path,
                file_data,
                file_options={"content-type": "application/pdf"}
            )
            
            # Get signed URL (valid for 1 year)
            signed_url = self.supabase.storage.from_(self.bucket_name).create_signed_url(file_path, 31536000)  # 1 year in seconds
            
            # Return the signed URL
            return signed_url['signedURL']
            
        except Exception as e:
            raise Exception(f"Failed to upload file to Supabase: {str(e)}")
    
    def delete_from_supabase(self, file_path: str) -> bool:
        """
        Delete file from Supabase Storage.
        
        Args:
            file_path: Path of file in storage
            
        Returns:
            bool: True if deletion successful
        """
        try:
            # Extract path from URL if full URL is provided
            if file_path.startswith('http'):
                # Parse path from URL
                # Format: https://xxx.supabase.co/storage/v1/object/public/bucket/path
                parts = file_path.split(f'{self.bucket_name}/')
                if len(parts) > 1:
                    file_path = parts[1]
            
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True
            
        except Exception as e:
            print(f"Failed to delete file: {str(e)}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        Get public URL for a file.
        
        Args:
            file_path: Path of file in storage
            
        Returns:
            str: Public URL
        """
        return self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
    
    @staticmethod
    def get_file_size(file_data: bytes) -> int:
        """Get file size in bytes."""
        return len(file_data)
