"""
Document routes.
Handles document upload, retrieval, and deletion.
"""
from flask import Blueprint, request
from app.middleware.auth_middleware import require_auth
from app.services.document_service import DocumentService
from app.database import SessionLocal
from app.utils.response_utils import ResponseUtils
from uuid import UUID

# Create blueprint
document_bp = Blueprint('documents', __name__)


@document_bp.route('/upload', methods=['POST'])
@require_auth
def upload_document():
    """
    Upload a new document.
    
    Expects multipart/form-data with 'file' field.
    
    Returns:
        Document object with id, name, file_url, etc.
    """
    try:
        print(f"🔍 Upload request received")
        print(f"👤 User ID: {request.user_id}")
        
        # Ensure user exists in database
        from app.utils.user_utils import ensure_user_exists
        ensure_user_exists(request.user_id, getattr(request, 'user_email', None))
        
        # Check if file is present
        if 'file' not in request.files:
            print("❌ No file in request")
            return ResponseUtils.validation_error('No file provided')
        
        file = request.files['file']
        print(f"✅ File received: {file.filename}")
        
        if file.filename == '':
            return ResponseUtils.validation_error('No file selected')
        
        # Read file data
        file_data = file.read()
        filename = file.filename
        print(f"📄 File size: {len(file_data)} bytes")
        
        # Get authenticated user ID from Clerk
        user_id = request.user_id
        print(f"👤 User ID: {user_id}")
        
        # Use Supabase REST API directly
        from app.utils.file_utils import FileUtils
        from app.utils.pdf_utils import PDFUtils
        from app.services.vector_service import VectorService
        from supabase import create_client
        from app.config import Config
        import uuid
        from datetime import datetime
        
        # Upload file to storage
        file_utils = FileUtils()
        file_url = file_utils.upload_to_supabase(file_data, filename, user_id)
        print(f"📤 File uploaded to: {file_url}")
        
        # Extract text from PDF
        pdf_utils = PDFUtils()
        pages = pdf_utils.extract_text_from_pdf(file_data)
        extracted_text = ' '.join([page['text'] for page in pages])
        print(f"📝 Extracted {len(extracted_text)} characters of text from {len(pages)} pages")
        
        # Create document ID
        document_id = str(uuid.uuid4())
        
        # Create embeddings and store in Qdrant
        try:
            vector_service = VectorService()
            
            # Chunk the text using config settings
            chunks = pdf_utils.chunk_text(
                extracted_text, 
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP
            )
            print(f"🔪 Split into {len(chunks)} chunks")
            
            # Prepare chunks in the format expected by VectorService
            chunk_dicts = [
                {
                    'page_number': i // 3,  # Rough estimate of page
                    'chunk_id': i,
                    'text': chunk
                }
                for i, chunk in enumerate(chunks)
            ]
            
            # Store in vector database
            vector_service.add_document_chunks(
                document_id=document_id,
                chunks=chunk_dicts
            )
            print(f"✅ Stored {len(chunks)} chunks in Qdrant cloud")
        except Exception as e:
            print(f"❌ ERROR creating embeddings: {str(e)}")
            import traceback
            traceback.print_exc()
            # Don't fail the entire upload, but log the error
        
        # Create document record in Supabase via REST API
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        document_data = {
            'id': document_id,
            'user_id': user_id,
            'name': filename,
            'file_url': file_url,
            'file_size': len(file_data),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('documents').insert(document_data).execute()
        print(f"✅ Document record created in database")
        
        return ResponseUtils.created(
            result.data[0] if result.data else document_data,
            message='Document uploaded successfully'
        )
        
    except ValueError as e:
        print(f"❌ Validation error: {str(e)}")
        return ResponseUtils.validation_error(str(e))
    
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(f'Failed to upload document: {str(e)}')


@document_bp.route('', methods=['GET'])
@require_auth
def get_documents():
    """
    Get all documents for current user.
    
    Query params:
        limit: Max number of results (default 100)
        offset: Pagination offset (default 0)
    
    Returns:
        List of document objects
    """
    try:
        from supabase import create_client
        from app.config import Config
        
        # Get pagination params
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        # Use Supabase REST API
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # Get documents for user
        result = supabase.table('documents').select('*').eq('user_id', request.user_id).range(offset, offset + limit - 1).execute()
        
        # Get total count
        count_result = supabase.table('documents').select('*', count='exact').eq('user_id', request.user_id).execute()
        
        return ResponseUtils.success({
            'documents': result.data,
            'total': count_result.count
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(str(e))


@document_bp.route('/<document_id>', methods=['GET'])
@require_auth
def get_document(document_id):
    """
    Get a specific document.
    
    Args:
        document_id: UUID of document
    
    Returns:
        Document object with sessions
    """
    try:
        db = SessionLocal()
        document_service = DocumentService(db)
        
        # Get document
        document = document_service.get_document(
            document_id=UUID(document_id),
            user_id=request.user_id
        )
        
        return ResponseUtils.success(document.to_dict(include_sessions=True))
        
    except ValueError as e:
        return ResponseUtils.not_found(str(e))
    
    except PermissionError as e:
        return ResponseUtils.forbidden(str(e))
    
    except Exception as e:
        return ResponseUtils.internal_error(str(e))
    
    finally:
        db.close()


@document_bp.route('/<document_id>', methods=['DELETE'])
@require_auth
def delete_document(document_id):
    """
    Delete a document.
    
    Deletes document, embeddings, file from storage, all sessions, and all messages.
    
    Args:
        document_id: UUID of document
    """
    try:
        from supabase import create_client
        from app.config import Config
        from app.services.vector_service import VectorService
        import os
        
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # Verify document belongs to user
        doc_result = supabase.table('documents').select('*').eq('id', document_id).eq('user_id', request.user_id).execute()
        if not doc_result.data:
            return ResponseUtils.not_found('Document not found')
        
        document = doc_result.data[0]
        
        print(f"🗑️ Deleting document {document_id}...")
        
        # 1. Delete all messages for all sessions of this document
        sessions_result = supabase.table('sessions').select('id').eq('document_id', document_id).execute()
        if sessions_result.data:
            session_ids = [s['id'] for s in sessions_result.data]
            for session_id in session_ids:
                msg_delete = supabase.table('chat_messages').delete().eq('session_id', session_id).execute()
                print(f"  🗑️ Deleted messages for session {session_id}")
        
        # 2. Delete all sessions for this document
        sessions_delete = supabase.table('sessions').delete().eq('document_id', document_id).execute()
        print(f"  🗑️ Deleted {len(sessions_result.data) if sessions_result.data else 0} sessions")
        
        # 3. Delete embeddings from Qdrant
        try:
            vector_service = VectorService()
            vector_service.delete_document_chunks(document_id)
            print(f"  🗑️ Deleted embeddings from Qdrant cloud")
        except Exception as e:
            print(f"  ⚠️ Failed to delete embeddings: {e}")
        
        # 4. Delete file from Supabase storage
        try:
            file_path = document['file_url'].split('/')[-1]  # Extract filename
            supabase.storage.from_('documents').remove([file_path])
            print(f"  🗑️ Deleted file from storage")
        except Exception as e:
            print(f"  ⚠️ Failed to delete file: {e}")
        
        # 5. Delete document record
        supabase.table('documents').delete().eq('id', document_id).execute()
        print(f"✅ Document {document_id} deleted successfully")
        
        return ResponseUtils.success(message='Document deleted successfully')
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseUtils.internal_error(f'Failed to delete document: {str(e)}')
