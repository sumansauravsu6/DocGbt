"""Create a test user in Supabase for testing."""
from supabase import create_client
from app.config import Config
from datetime import datetime
import uuid

# Create Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)

# Create test user
user_data = {
    'id': 'test_user_123',
    'email': 'test@example.com',
    'created_at': datetime.utcnow().isoformat(),
    'updated_at': datetime.utcnow().isoformat()
}

try:
    result = supabase.table('users').insert(user_data).execute()
    print("✅ Test user created successfully!")
    print(f"User ID: {result.data[0]['id']}")
except Exception as e:
    print(f"❌ Error: {e}")
    # Try updating if user already exists
    try:
        result = supabase.table('users').update(user_data).eq('id', 'test_user_123').execute()
        print("✅ Test user already exists (updated)")
    except Exception as e2:
        print(f"❌ Update error: {e2}")
