"""
Test Supabase storage bucket
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("Testing Supabase Storage Bucket...")
print(f"URL: {SUPABASE_URL}")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # List all buckets
    buckets = supabase.storage.list_buckets()
    print(f"\n✅ Found {len(buckets)} bucket(s):")
    for bucket in buckets:
        print(f"   - {bucket.name} ({'public' if bucket.public else 'private'})")
    
    # Check if 'document' bucket exists
    bucket_names = [b.name for b in buckets]
    if 'document' in bucket_names:
        print(f"\n✅ 'document' bucket exists!")
    else:
        print(f"\n❌ 'document' bucket NOT found")
        print(f"   Available: {', '.join(bucket_names)}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
