-- Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Reset Tokens Table
CREATE TABLE reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create RFM Analysis Table
CREATE TABLE rfm_analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    segment_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    record_count INTEGER NOT NULL,
    column_mapping JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create RFM Segments Table
CREATE TABLE rfm_segments (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES rfm_analyses(id) ON DELETE CASCADE,
    segment_name VARCHAR(100) NOT NULL,
    customer_count INTEGER NOT NULL,
    avg_recency FLOAT,
    avg_frequency FLOAT,
    avg_monetary FLOAT,
    total_monetary FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create AI Insights Table
CREATE TABLE ai_insights (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES rfm_analyses(id) ON DELETE CASCADE,
    insight_text TEXT NOT NULL,
    model_used VARCHAR(50) DEFAULT 'gpt-4-turbo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_rfm_analyses_user_id ON rfm_analyses(user_id);
CREATE INDEX idx_rfm_segments_analysis_id ON rfm_segments(analysis_id);
CREATE INDEX idx_ai_insights_analysis_id ON ai_insights(analysis_id); 