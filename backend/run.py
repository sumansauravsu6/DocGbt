"""
Application entry point.
Initializes and runs the Flask application.
"""
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    app.run(host=host, port=port, debug=debug)
