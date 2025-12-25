"""
User utility functions.
"""
from supabase import create_client
from app.config import Config
from datetime import datetime


def ensure_user_exists(user_id: str, email: str = None):
    """
    Ensure user exists in Supabase users table.
    Creates user if they don't exist.
    
    Args:
        user_id: Clerk user ID
        email: User email (optional)
    """
    try:
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
        
        # Check if user exists
        result = supabase.table('users').select('id').eq('id', user_id).execute()
        
        if not result.data:
            # User doesn't exist, create them
            user_data = {
                'id': user_id,
                'email': email,
                'created_at': datetime.utcnow().isoformat()
            }
            supabase.table('users').insert(user_data).execute()
            print(f"✅ Created user in database: {user_id}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error ensuring user exists: {str(e)}")
        return False
