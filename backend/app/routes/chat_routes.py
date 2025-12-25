"""
Chat routes.
Handles chat messages and AI responses.
"""
from flask import Blueprint, request
from app.middleware.auth_middleware import require_auth
from app.services.chat_service import ChatService
from app.database import SessionLocal
from app.utils.response_utils import ResponseUtils
from uuid import UUID
import json

# Create blueprint
chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/sessions/<session_id>/messages', methods=['POST'])
@require_auth
def send_message(session_id):
    """
    Send a message and get AI response.
    
    Args:
        session_id: UUID of session
    
    Body:
        {
            "message": "User message content"
        }
    
    Returns:
        {
            "user_message": {...},
            "assistant_message": {...}
        }
    """
    try:
        from supabase import create_client
        from app.config import Config
        from app.services.vector_service import VectorService
        from app.services.rag_service import RAGService
        from datetime import datetime
        import uuid
        
        data = request.get_json()
        
        if not data or 'message' not in data:
            return ResponseUtils.validation_error('Message is required')
        
        message = data['message'].strip()
        
        if not message:
            return ResponseUtils.validation_error('Message cannot be empty')
        
        # Use Supabase REST API
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # Get session to find document_id
        session_result = supabase.table('sessions').select('*').eq('id', session_id).execute()
        if not session_result.data:
            return ResponseUtils.not_found('Session not found')
        
        session = session_result.data[0]
        document_id = session['document_id']
        
        # Verify the document belongs to the user
        doc_result = supabase.table('documents').select('id').eq('id', document_id).eq('user_id', request.user_id).execute()
        if not doc_result.data:
            return ResponseUtils.forbidden('You do not have access to this document')
        
        print(f"💬 User message: {message}")
        print(f"📄 Document ID: {document_id}")
        
        # Check if this is the first message in the session and auto-name it
        messages_count = supabase.table('chat_messages').select('id', count='exact').eq('session_id', session_id).execute()
        if messages_count.count == 0:
            # This is the first message, update session title
            session_title = message[:50] + ('...' if len(message) > 50 else '')
            supabase.table('sessions').update({
                'title': session_title,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', session_id).execute()
            print(f"📝 Updated session title to: {session_title}")
        
        # Save user message
        # Get last 6 messages for conversation context (BEFORE saving current message)
        previous_messages = supabase.table('chat_messages')\
            .select('role, content, created_at')\
            .eq('session_id', session_id)\
            .order('created_at', desc=False)\
            .execute()
        
        # Get the last 6 messages (3 exchanges) for context
        conversation_history = []
        if previous_messages.data and len(previous_messages.data) > 0:
            # Take last 6 messages for context
            conversation_history = previous_messages.data[-6:] if len(previous_messages.data) > 6 else previous_messages.data
            print(f"💭 Using {len(conversation_history)} previous messages for context")
            for i, msg in enumerate(conversation_history):
                print(f"  {i+1}. {msg['role']}: {msg['content'][:50]}...")
        
        # Save user message AFTER fetching history
        user_message_data = {
            'id': str(uuid.uuid4()),
            'session_id': session_id,
            'role': 'user',
            'content': message,
            'created_at': datetime.utcnow().isoformat()
        }
        user_msg_result = supabase.table('chat_messages').insert(user_message_data).execute()
        
        # Use RAG to get relevant context and generate response
        try:
            vector_service = VectorService()
            rag_service = RAGService(vector_service)
            
            # Search for relevant chunks (increased for better coverage)
            relevant_chunks = vector_service.search(message, document_id, top_k=8)
            print(f"🔍 Found {len(relevant_chunks)} relevant chunks")
            
            # Debug: Print chunks
            for i, chunk in enumerate(relevant_chunks):
                print(f"📄 Chunk {i+1}: {chunk['text'][:100]}...")
            
            # Generate response with context
            context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
            print(f"📝 Context length: {len(context)} characters")
            print(f"📝 Context preview: {context[:200]}...")
            
            # Stream response and collect full text
            ai_response = ""
            
            def generate():
                nonlocal ai_response
                try:
                    for chunk in rag_service.generate_response_stream(message, context, conversation_history):
                        ai_response += chunk
                        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                    
                    # Save assistant message after streaming completes
                    assistant_message_data = {
                        'id': str(uuid.uuid4()),
                        'session_id': session_id,
                        'role': 'assistant',
                        'content': ai_response,
                        'created_at': datetime.utcnow().isoformat()
                    }
                    assistant_msg_result = supabase.table('chat_messages').insert(assistant_message_data).execute()
                    
                    # Send complete message data
                    yield f"data: {json.dumps({'done': True, 'message': assistant_msg_result.data[0]})}\n\n"
                    
                except Exception as e:
                    print(f"⚠️ Streaming error: {str(e)}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            from flask import Response
            return Response(generate(), mimetype='text/event-stream')
            
        except Exception as e:
            print(f"⚠️ RAG error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback non-streaming response
            ai_response = "I apologize, but I'm having trouble accessing the document content. Please try again."
            assistant_message_data = {
                'id': str(uuid.uuid4()),
                'session_id': session_id,
                'role': 'assistant',
                'content': ai_response,
                'created_at': datetime.utcnow().isoformat()
            }
            assistant_msg_result = supabase.table('chat_messages').insert(assistant_message_data).execute()
            
            return ResponseUtils.success({
                'user_message': user_msg_result.data[0],
                'assistant_message': assistant_msg_result.data[0]
            })
        
    except ValueError as e:
        return ResponseUtils.not_found(str(e))
    
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(f'Failed to send message: {str(e)}')


@chat_bp.route('/sessions/<session_id>/messages', methods=['GET'])
@require_auth
def get_messages(session_id):
    """
    Get all messages for a session.
    
    Args:
        session_id: UUID of session
    
    Query params:
        limit: Max number of results (default 100)
        offset: Pagination offset (default 0)
    
    Returns:
        List of message objects
    """
    try:
        from supabase import create_client
        from app.config import Config
        
        # Get pagination params
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Use Supabase REST API
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # Get messages
        result = supabase.table('chat_messages').select('*').eq('session_id', session_id).order('created_at').range(offset, offset + limit - 1).execute()
        
        return ResponseUtils.success({
            'messages': result.data
        })
        
    except ValueError as e:
        return ResponseUtils.not_found(str(e))
    
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(str(e))


@chat_bp.route('/sessions/<session_id>/clear', methods=['DELETE'])
@require_auth
def clear_session_history(session_id):
    """
    Clear all messages in a session.
    
    Args:
        session_id: UUID of session
    """
    try:
        db = SessionLocal()
        chat_service = ChatService(db)
        
        # Clear history
        deleted_count = chat_service.clear_session_history(
            session_id=UUID(session_id),
            user_id=request.user_id
        )
        
        return ResponseUtils.success({
            'deleted_count': deleted_count
        }, message='Session history cleared')
        
    except ValueError as e:
        return ResponseUtils.not_found(str(e))
    
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        return ResponseUtils.internal_error(str(e))
    
    finally:
        db.close()
