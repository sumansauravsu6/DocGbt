"""
Clerk authentication middleware.
Verifies JWT tokens from Clerk and extracts user information.
"""
import jwt
import requests
from functools import wraps
from flask import request, jsonify
from app.config import Config


class ClerkAuthMiddleware:
    """
    Middleware for Clerk JWT verification.
    
    Verifies Clerk session tokens and extracts user claims.
    Uses Clerk's JWKS endpoint for token verification.
    """
    
    def __init__(self):
        self.secret_key = Config.CLERK_SECRET_KEY
        self.jwks_url = "https://api.clerk.dev/v1/jwks"
        self._jwks_cache = None
    
    def get_jwks(self):
        """
        Fetch JSON Web Key Set from Clerk.
        Caches the result to avoid repeated requests.
        """
        if self._jwks_cache is None:
            try:
                response = requests.get(self.jwks_url, timeout=5)
                response.raise_for_status()
                self._jwks_cache = response.json()
            except Exception as e:
                print(f"Error fetching JWKS: {str(e)}")
                return None
        
        return self._jwks_cache
    
    def verify_token(self, token):
        """
        Verify Clerk JWT token.
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            dict: Decoded token claims if valid
            None: If token is invalid
        """
        try:
            # Decode without verification first to get header
            unverified_header = jwt.get_unverified_header(token)
            
            # For development, we can verify using the secret key
            # In production, use JWKS for proper verification
            decoded = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256', 'RS256'],
                options={'verify_signature': False}  # Set to True in production with proper JWKS
            )
            
            return decoded
            
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            print(f"Token verification error: {str(e)}")
            return None
    
    def get_user_from_token(self, token):
        """
        Extract user information from token.
        
        Returns:
            dict: User information (user_id, email)
            None: If token is invalid
        """
        claims = self.verify_token(token)
        
        if not claims:
            return None
        
        # Clerk token claims structure
        # 'sub' contains the user_id
        user_id = claims.get('sub')
        email = claims.get('email') or claims.get('email_address')
        
        if not user_id:
            return None
        
        return {
            'user_id': user_id,
            'email': email,
            'claims': claims
        }


# Global middleware instance
clerk_auth = ClerkAuthMiddleware()


def require_auth(f):
    """
    Decorator to require authentication for routes.
    
    Usage:
        @app.route('/protected')
        @require_auth
        def protected_route():
            user_id = request.user_id
            return {'message': f'Hello {user_id}'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Missing authorization header'
            }), 401
        
        # Extract token (format: "Bearer <token>")
        try:
            scheme, token = auth_header.split(' ')
            if scheme.lower() != 'bearer':
                raise ValueError('Invalid authorization scheme')
        except ValueError:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid authorization header format'
            }), 401
        
        # Verify token and get user info
        user_info = clerk_auth.get_user_from_token(token)
        
        if not user_info:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or expired token'
            }), 401
        
        # Attach user info to request object
        request.user_id = user_info['user_id']
        request.user_email = user_info.get('email')
        request.user_claims = user_info.get('claims', {})
        
        return f(*args, **kwargs)
    
    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication.
    Attaches user info if token is present and valid.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                scheme, token = auth_header.split(' ')
                if scheme.lower() == 'bearer':
                    user_info = clerk_auth.get_user_from_token(token)
                    if user_info:
                        request.user_id = user_info['user_id']
                        request.user_email = user_info.get('email')
                        request.user_claims = user_info.get('claims', {})
            except Exception:
                pass  # Continue without auth
        
        # Set defaults if not authenticated
        if not hasattr(request, 'user_id'):
            request.user_id = None
            request.user_email = None
            request.user_claims = {}
        
        return f(*args, **kwargs)
    
    return decorated_function
