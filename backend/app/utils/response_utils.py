"""
Response utilities for consistent API responses.
"""
from flask import jsonify
from typing import Any, Dict, List


class ResponseUtils:
    """Utilities for standardized API responses."""
    
    @staticmethod
    def success(data: Any = None, message: str = None, status_code: int = 200):
        """
        Create a success response.
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            
        Returns:
            Flask response with JSON
        """
        response = {
            'success': True
        }
        
        if message:
            response['message'] = message
        
        if data is not None:
            response['data'] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(message: str, error_code: str = None, status_code: int = 400):
        """
        Create an error response.
        
        Args:
            message: Error message
            error_code: Error code for client handling
            status_code: HTTP status code
            
        Returns:
            Flask response with JSON
        """
        response = {
            'success': False,
            'error': message
        }
        
        if error_code:
            response['error_code'] = error_code
        
        return jsonify(response), status_code
    
    @staticmethod
    def created(data: Any, message: str = "Resource created successfully"):
        """Create a 201 Created response."""
        return ResponseUtils.success(data, message, 201)
    
    @staticmethod
    def no_content():
        """Create a 204 No Content response."""
        return '', 204
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized"):
        """Create a 401 Unauthorized response."""
        return ResponseUtils.error(message, 'UNAUTHORIZED', 401)
    
    @staticmethod
    def forbidden(message: str = "Forbidden"):
        """Create a 403 Forbidden response."""
        return ResponseUtils.error(message, 'FORBIDDEN', 403)
    
    @staticmethod
    def not_found(message: str = "Resource not found"):
        """Create a 404 Not Found response."""
        return ResponseUtils.error(message, 'NOT_FOUND', 404)
    
    @staticmethod
    def validation_error(message: str, errors: Dict = None):
        """
        Create a 422 Validation Error response.
        
        Args:
            message: Error message
            errors: Dict of field-specific errors
        """
        response = {
            'success': False,
            'error': message,
            'error_code': 'VALIDATION_ERROR'
        }
        
        if errors:
            response['errors'] = errors
        
        return jsonify(response), 422
    
    @staticmethod
    def internal_error(message: str = "Internal server error"):
        """Create a 500 Internal Server Error response."""
        return ResponseUtils.error(message, 'INTERNAL_ERROR', 500)
    
    @staticmethod
    def paginated(data: List, total: int, page: int = 1, per_page: int = 20):
        """
        Create a paginated response.
        
        Args:
            data: List of items
            total: Total count of items
            page: Current page number
            per_page: Items per page
        """
        return ResponseUtils.success({
            'items': data,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        })
