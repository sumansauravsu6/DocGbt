"""
User repository.
Handles database operations for User model.
"""
from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional


class UserRepository:
    """
    Repository pattern for User model.
    Separates data access logic from business logic.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: str, email: str) -> User:
        """
        Create a new user.
        
        Args:
            user_id: Clerk user ID
            email: User email
            
        Returns:
            User: Created user object
        """
        user = User(
            id=user_id,
            email=email
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_or_create(self, user_id: str, email: str) -> User:
        """
        Get existing user or create new one.
        Useful for first-time user authentication.
        """
        user = self.get_by_id(user_id)
        
        if not user:
            user = self.create(user_id, email)
        
        return user
    
    def update_email(self, user_id: str, new_email: str) -> Optional[User]:
        """Update user email."""
        user = self.get_by_id(user_id)
        
        if user:
            user.email = new_email
            self.db.commit()
            self.db.refresh(user)
        
        return user
    
    def delete(self, user_id: str) -> bool:
        """Delete user."""
        user = self.get_by_id(user_id)
        
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        
        return False
