"""
Flask application factory.
Creates and configures the Flask app with all necessary extensions and blueprints.
"""
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import init_db, close_db
import atexit


def create_app():
    """
    Application factory pattern.
    Creates and configures the Flask application.
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Validate configuration
    Config.validate()
    
    # Enable CORS for frontend communication
    # Get allowed origins from environment variable
    allowed_origins = Config.ALLOWED_ORIGINS.split(',') if Config.ALLOWED_ORIGINS else ["http://localhost:5173"]
    
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True
        }
    })
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Register cleanup handler
    atexit.register(lambda: close_db())
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'DocGPT API'}, 200
    
    print("✅ Flask application created successfully")
    
    return app


def register_blueprints(app):
    """Register all Flask blueprints for modular routing."""
    from app.routes.auth_routes import auth_bp
    from app.routes.document_routes import document_bp
    from app.routes.session_routes import session_bp
    from app.routes.chat_routes import chat_bp
    
    # Register with /api prefix for clear API versioning
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    app.register_blueprint(session_bp, url_prefix='/api/sessions')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')


def register_error_handlers(app):
    """Register global error handlers for consistent error responses."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'error': 'Bad Request',
            'message': str(error)
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }, 500
