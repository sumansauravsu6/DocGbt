"""
Authentication routes.
Handles user authentication and registration.
"""
from flask import Blueprint, request
from app.middleware.auth_middleware import require_auth
from app.services.auth_service import AuthService
from app.database import SessionLocal
from app.utils.response_utils import ResponseUtils

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    Get current authenticated user.
    
    Returns user information from Clerk token.
    Creates user record if doesn't exist (first-time login).
    """
    try:
        db = SessionLocal()
        auth_service = AuthService(db)
        
        # Ensure user exists in database
        user = auth_service.ensure_user_exists(
            user_id=request.user_id,
            email=request.user_email
        )
        
        return ResponseUtils.success(user.to_dict())
        
    except Exception as e:
        return ResponseUtils.internal_error(str(e))
    
    finally:
        db.close()


@auth_bp.route('/status', methods=['GET'])
@require_auth
def auth_status():
    """
    Check authentication status.
    Simple endpoint to verify token is valid.
    """
    return ResponseUtils.success({
        'authenticated': True,
        'user_id': request.user_id,
        'email': request.user_email
    })
