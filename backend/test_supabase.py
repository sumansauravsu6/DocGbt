"""
Test Supabase connection and setup
"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("🔍 Testing Supabase Setup...\n")

# Test 1: Check environment variables
print("1. Environment Variables:")
print(f"   SUPABASE_URL: {'✅ Set' if SUPABASE_URL else '❌ Missing'}")
print(f"   SUPABASE_KEY: {'✅ Set' if SUPABASE_KEY else '❌ Missing'}")
print()

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials in .env file")
    exit(1)

# Test 2: Test REST API connection
print("2. Testing REST API connection...")
try:
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    # Try to query users table
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/users?limit=1",
        headers=headers
    )
    
    if response.status_code == 200:
        print("   ✅ REST API connection successful")
        print(f"   ✅ Users table exists and is accessible")
    elif response.status_code == 401:
        print("   ❌ Authentication failed - check your SUPABASE_KEY")
    else:
        print(f"   ⚠️  Response: {response.status_code}")
        print(f"   Message: {response.text}")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")

print()

# Test 3: Check all tables
print("3. Checking database tables...")
tables = ['users', 'documents', 'sessions', 'chat_messages']

for table in tables:
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table}?limit=0",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"   ✅ {table} table exists")
        elif response.status_code == 404:
            print(f"   ❌ {table} table not found")
        else:
            print(f"   ⚠️  {table}: {response.status_code}")
    except Exception as e:
        print(f"   ❌ {table}: {e}")

print()

# Test 4: Check storage bucket
print("4. Testing Storage bucket...")
try:
    # List buckets
    response = requests.get(
        f"{SUPABASE_URL}/storage/v1/bucket",
        headers=headers
    )
    
    if response.status_code == 200:
        buckets = response.json()
        bucket_names = [b['name'] for b in buckets]
        
        if 'document' in bucket_names:
            print("   ✅ 'document' bucket exists")
            
            # Get bucket details
            doc_bucket = next(b for b in buckets if b['name'] == 'document')
            print(f"   ✅ Bucket is {'public' if doc_bucket.get('public') else 'private'}")
        else:
            print("   ❌ 'document' bucket not found")
            print(f"   Available buckets: {', '.join(bucket_names) if bucket_names else 'None'}")
    else:
        print(f"   ⚠️  Storage API response: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"   ❌ Storage check failed: {e}")

print()
print("=" * 50)
print("✅ Supabase setup verification complete!")
print("=" * 50)
