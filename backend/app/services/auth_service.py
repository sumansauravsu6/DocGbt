"""
Authentication service.
Handles user authentication and registration.
"""
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    Service for authentication operations.
    
    Note: Actual authentication is handled by Clerk.
    This service manages user records in our database.
    """
    
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
    
    def ensure_user_exists(self, user_id: str, email: str):
        """
        Ensure user exists in database.
        Creates user if doesn't exist (first-time login).
        
        Args:
            user_id: Clerk user ID
            email: User email
            
        Returns:
            User object
        """
        return self.user_repo.get_or_create(user_id, email)
    
    def get_user(self, user_id: str):
        """Get user by ID."""
        return self.user_repo.get_by_id(user_id)
    
    def update_user_email(self, user_id: str, new_email: str):
        """
        Update user email.
        Called when user updates email in Clerk.
        """
        return self.user_repo.update_email(user_id, new_email)
