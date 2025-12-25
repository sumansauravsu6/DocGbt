"""
Simplified application entry point without ML dependencies.
For testing purposes - runs without vector/embedding services.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'DocGPT Backend is running'})

@app.route('/api/test')
def test():
    return jsonify({
        'supabase_configured': bool(os.getenv('SUPABASE_URL')),
        'clerk_configured': bool(os.getenv('CLERK_SECRET_KEY')),
        'chroma_host': os.getenv('CHROMA_HOST', 'localhost'),
        'message': 'Configuration test endpoint'
    })

# Mock API endpoints for frontend
@app.route('/api/documents', methods=['GET', 'POST'])
def documents():
    if request.method == 'GET':
        return jsonify({'documents': [], 'message': 'Backend in simple mode - upload not available'})
    return jsonify({'message': 'Backend in simple mode - upload not available'}), 503

@app.route('/api/documents/<doc_id>', methods=['GET', 'DELETE'])
def document_detail(doc_id):
    return jsonify({'message': 'Backend in simple mode'}), 503

@app.route('/api/sessions', methods=['GET', 'POST'])
def sessions():
    return jsonify({'sessions': [], 'message': 'Backend in simple mode'}), 503

@app.route('/api/chat/<session_id>', methods=['GET', 'POST'])
def chat(session_id):
    return jsonify({'messages': [], 'message': 'Backend in simple mode - AI features require Python 3.11'}), 503

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print("🚀 Starting DocGPT Backend (Simple Mode - No ML)")
    print(f"   Server: http://{host}:{port}")
    print(f"   Health: http://localhost:{port}/health")
    print(f"   Test:   http://localhost:{port}/api/test")
    print("\n   Press CTRL+C to stop the server\n")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)
