-- Enable pgcrypto for UUID generation if needed, though gen_random_uuid() is standard in Postgres 13+
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index on email for faster authentication lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create documents table (migrating from documents.json)
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    size VARCHAR(50) NOT NULL,
    uploaded_at VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index on user_id for fast filtering in tenant isolation
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);

-- Create intent_logs table for Telemetry Logging Guard
CREATE TABLE IF NOT EXISTS intent_logs (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    predicted_intent VARCHAR(50) NOT NULL,
    ground_truth VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Create session_audit table for persistent session audit validation logging
CREATE TABLE IF NOT EXISTS session_audit (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    steps JSONB NOT NULL,
    chart_b64 TEXT,
    warnings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create token_usage table for tracking token count and estimated cost per node/session
CREATE TABLE IF NOT EXISTS token_usage (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    node_name VARCHAR(100) NOT NULL,
    model_name VARCHAR(150) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cost NUMERIC(10, 6) NOT NULL DEFAULT 0.000000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_token_usage_session_id ON token_usage(session_id);

