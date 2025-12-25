-- Migration to remove foreign key constraint and make email optional
-- Run this in your Supabase SQL Editor

-- Step 1: Drop the foreign key constraint on documents table
ALTER TABLE documents 
DROP CONSTRAINT IF EXISTS documents_user_id_fkey;

-- Step 2: Make email optional in users table (if constraint exists)
ALTER TABLE users 
ALTER COLUMN email DROP NOT NULL;

-- Done! Now documents can be created without requiring the user to exist first.
-- The user will be auto-created on first upload.
