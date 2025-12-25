"""
Session routes.
Handles chat session management.
"""
from flask import Blueprint, request
from app.middleware.auth_middleware import require_auth
from app.services.session_service import SessionService
from app.database import SessionLocal
from app.utils.response_utils import ResponseUtils
from uuid import UUID

# Create blueprint
session_bp = Blueprint('sessions', __name__)


@session_bp.route('/document/<document_id>', methods=['POST'])
@require_auth
def create_session(document_id):
    """
    Create a new chat session for a document.
    
    Args:
        document_id: UUID of parent document
    
    Body (optional):
        {
            "title": "Custom session title"
        }
    
    Returns:
        Session object
    """
    try:
        from supabase import create_client
        from app.config import Config
        from datetime import datetime
        import uuid
        
        # Get request data
        data = request.get_json() or {}
        title = data.get('title', 'New Chat')
        
        # Use Supabase REST API
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # First verify the document belongs to the user
        doc_result = supabase.table('documents').select('id').eq('id', document_id).eq('user_id', request.user_id).execute()
        if not doc_result.data:
            return ResponseUtils.forbidden('You do not have access to this document')
        
        # Create session
        session_data = {
            'id': str(uuid.uuid4()),
            'document_id': document_id,
            'title': title,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('sessions').insert(session_data).execute()
        
        return ResponseUtils.created(
            result.data[0],
            message='Session created successfully'
        )
        
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(str(e))


@session_bp.route('/document/<document_id>', methods=['GET'])
@require_auth
def get_document_sessions(document_id):
    """
    Get all sessions for a document.
    
    Args:
        document_id: UUID of document
    
    Query params:
        limit: Max number of results (default 50)
        offset: Pagination offset (default 0)
    
    Returns:
        List of session objects
    """
    try:
        from supabase import create_client
        from app.config import Config
        
        # Get pagination params
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Use Supabase REST API
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # First verify the document belongs to the user
        doc_result = supabase.table('documents').select('id').eq('id', document_id).eq('user_id', request.user_id).execute()
        if not doc_result.data:
            return ResponseUtils.forbidden('You do not have access to this document')
        
        # Get sessions for this document
        result = supabase.table('sessions').select('*').eq('document_id', document_id).range(offset, offset + limit - 1).execute()
        
        return ResponseUtils.success({
            'sessions': result.data
        })
        
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(str(e))


@session_bp.route('/<session_id>', methods=['GET'])
@require_auth
def get_session(session_id):
    """
    Get a specific session.
    
    Args:
        session_id: UUID of session
    
    Returns:
        Session object with messages
    """
    try:
        db = SessionLocal()
        session_service = SessionService(db)
        
        # Get session
        session = session_service.get_session(
            session_id=UUID(session_id),
            user_id=request.user_id
        )
        
        return ResponseUtils.success(session.to_dict(include_messages=True))
        
    except ValueError as e:
        return ResponseUtils.not_found(str(e))
    
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        return ResponseUtils.internal_error(str(e))
    
    finally:
        db.close()


@session_bp.route('/<session_id>', methods=['PATCH'])
@require_auth
def update_session(session_id):
    """
    Update session title.
    
    Args:
        session_id: UUID of session
    
    Body:
        {
            "title": "New title"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return ResponseUtils.validation_error('Title is required')
        
        db = SessionLocal()
        session_service = SessionService(db)
        
        # Update session
        session = session_service.update_session_title(
            session_id=UUID(session_id),
            user_id=request.user_id,
            title=data['title']
        )
        
        return ResponseUtils.success(
            session.to_dict(),
            message='Session updated successfully'
        )
        
    except ValueError as e:
        return ResponseUtils.not_found(str(e))
    
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        return ResponseUtils.internal_error(str(e))
    
    finally:
        db.close()


@session_bp.route('/<session_id>', methods=['DELETE'])
@require_auth
def delete_session(session_id):
    """
    Delete a session and all its messages.
    
    Args:
        session_id: UUID of session
    """
    try:
        from supabase import create_client
        from app.config import Config
        
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # Verify session exists and get document_id
        session_result = supabase.table('sessions').select('document_id').eq('id', session_id).execute()
        if not session_result.data:
            return ResponseUtils.not_found('Session not found')
        
        document_id = session_result.data[0]['document_id']
        
        # Verify document belongs to user
        doc_result = supabase.table('documents').select('id').eq('id', document_id).eq('user_id', request.user_id).execute()
        if not doc_result.data:
            return ResponseUtils.forbidden('You do not have access to this session')
        
        print(f"🗑️ Deleting session {session_id}...")
        
        # 1. Delete all messages for this session
        msg_delete = supabase.table('chat_messages').delete().eq('session_id', session_id).execute()
        print(f"  🗑️ Deleted messages for session")
        
        # 2. Delete session record
        supabase.table('sessions').delete().eq('id', session_id).execute()
        print(f"✅ Session {session_id} deleted successfully")
        
        return ResponseUtils.success(message='Session deleted successfully')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(f'Failed to delete session: {str(e)}')
