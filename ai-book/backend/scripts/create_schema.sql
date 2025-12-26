-- Create database schema for RAG chatbot

-- Users table (anonymous sessions)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW()
);

-- Book metadata
CREATE TABLE IF NOT EXISTS book_metadata (
    book_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    version VARCHAR(50),
    total_chapters INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chunks (text segments)
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES book_metadata(book_id),
    chapter_num INT NOT NULL,
    chapter_title VARCHAR(500) NOT NULL,
    section_title VARCHAR(500),
    chunk_text TEXT NOT NULL,
    chunk_index INT NOT NULL,
    token_count INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat history
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    selected_text TEXT,
    retrieval_mode VARCHAR(50) NOT NULL,
    chunks_used UUID[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chat_history(chat_id),
    rating INT CHECK (rating >= 1 AND rating <= 5) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_chunks_book_chapter ON chunks(book_id, chapter_num);
CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_feedback_chat ON feedback(chat_id);
CREATE INDEX IF NOT EXISTS idx_users_session ON users(session_token);

-- Comments
COMMENT ON TABLE users IS 'User sessions for tracking chat history';
COMMENT ON TABLE book_metadata IS 'Metadata about the book';
COMMENT ON TABLE chunks IS 'Text chunks from the book for RAG retrieval';
COMMENT ON TABLE chat_history IS 'History of all chat interactions';
COMMENT ON TABLE feedback IS 'User feedback on chat responses';
