-- DocGPT Database Schema for Supabase (PostgreSQL)
-- Execute this script in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
-- Note: Clerk handles authentication, we just store reference and metadata
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,  -- Clerk user_id
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Documents table (each document is a DocGPT)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    file_url TEXT NOT NULL,  -- Supabase Storage URL
    file_size BIGINT,  -- File size in bytes
    page_count INTEGER,  -- Number of pages in PDF
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- Sessions table (chat sessions per document)
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL DEFAULT 'New Chat',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sessions_document_id ON sessions(document_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources JSONB,  -- Store page numbers and chunk references
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at ASC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Users can only read their own data
CREATE POLICY users_select_policy ON users
    FOR SELECT
    USING (id = current_setting('app.current_user_id', TRUE));

CREATE POLICY users_insert_policy ON users
    FOR INSERT
    WITH CHECK (id = current_setting('app.current_user_id', TRUE));

-- Documents policies
CREATE POLICY documents_select_policy ON documents
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id', TRUE));

CREATE POLICY documents_insert_policy ON documents
    FOR INSERT
    WITH CHECK (user_id = current_setting('app.current_user_id', TRUE));

CREATE POLICY documents_delete_policy ON documents
    FOR DELETE
    USING (user_id = current_setting('app.current_user_id', TRUE));

-- Sessions policies (access through document ownership)
CREATE POLICY sessions_select_policy ON sessions
    FOR SELECT
    USING (
        document_id IN (
            SELECT id FROM documents
            WHERE user_id = current_setting('app.current_user_id', TRUE)
        )
    );

CREATE POLICY sessions_insert_policy ON sessions
    FOR INSERT
    WITH CHECK (
        document_id IN (
            SELECT id FROM documents
            WHERE user_id = current_setting('app.current_user_id', TRUE)
        )
    );

CREATE POLICY sessions_delete_policy ON sessions
    FOR DELETE
    USING (
        document_id IN (
            SELECT id FROM documents
            WHERE user_id = current_setting('app.current_user_id', TRUE)
        )
    );

-- Chat messages policies (access through session ownership)
CREATE POLICY chat_messages_select_policy ON chat_messages
    FOR SELECT
    USING (
        session_id IN (
            SELECT s.id FROM sessions s
            JOIN documents d ON s.document_id = d.id
            WHERE d.user_id = current_setting('app.current_user_id', TRUE)
        )
    );

CREATE POLICY chat_messages_insert_policy ON chat_messages
    FOR INSERT
    WITH CHECK (
        session_id IN (
            SELECT s.id FROM sessions s
            JOIN documents d ON s.document_id = d.id
            WHERE d.user_id = current_setting('app.current_user_id', TRUE)
        )
    );

-- Storage bucket for documents
-- Create this in Supabase Storage UI or via SQL:
-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('documents', 'documents', false);

-- Storage policies (create in Supabase Storage UI)
-- Allow authenticated users to upload: user_id = {user_id}/*
-- Allow users to read their own files: user_id = {user_id}/*

-- Create views for common queries
CREATE OR REPLACE VIEW document_with_session_count AS
SELECT 
    d.*,
    COUNT(s.id) as session_count
FROM documents d
LEFT JOIN sessions s ON d.id = s.document_id
GROUP BY d.id;

CREATE OR REPLACE VIEW session_with_message_count AS
SELECT 
    s.*,
    COUNT(cm.id) as message_count,
    MAX(cm.created_at) as last_message_at
FROM sessions s
LEFT JOIN chat_messages cm ON s.id = cm.session_id
GROUP BY s.id;
