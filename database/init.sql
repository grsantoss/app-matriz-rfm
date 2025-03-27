-- Initialization script for Matriz RFM database

-- Create auth database
CREATE DATABASE auth_db;
\c auth_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reset tokens table
CREATE TABLE IF NOT EXISTS reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, token)
);

-- Create main application database
CREATE DATABASE app_db;
\c app_db;

-- Users table (mirror from auth)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis table
CREATE TABLE IF NOT EXISTS analyses (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID format
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_name VARCHAR(255),
    file_size INTEGER,  -- in bytes
    total_customers INTEGER,
    has_error BOOLEAN DEFAULT FALSE,
    error_message TEXT
);

-- Customer segments table
CREATE TABLE IF NOT EXISTS customer_segments (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(36) NOT NULL REFERENCES analyses(analysis_id) ON DELETE CASCADE,
    segment_name VARCHAR(255) NOT NULL,
    customer_count INTEGER NOT NULL,
    percentage FLOAT NOT NULL,
    avg_recency FLOAT,
    avg_frequency FLOAT,
    avg_monetary FLOAT,
    total_revenue FLOAT,
    revenue_percentage FLOAT
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_analyses_analysis_id ON analyses(analysis_id);
CREATE INDEX idx_customer_segments_analysis_id ON customer_segments(analysis_id);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres; 