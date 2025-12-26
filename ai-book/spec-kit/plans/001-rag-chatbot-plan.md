# Plan 001: RAG Chatbot Implementation Plan

**Spec Reference:** 001-rag-chatbot.md
**Status:** Active
**Created:** 2025-12-26
**Estimated Duration:** Phased approach

---

## Executive Summary

This plan outlines the implementation strategy for a RAG (Retrieval-Augmented Generation) chatbot integrated into the Docusaurus e-book website. The system will use FastAPI backend, Qdrant for vector search, Neon Postgres for data persistence, and OpenAI for AI capabilities.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Docusaurus)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │ Chat Widget  │  │ Text Selector│  │ Book Reader UI  │   │
│  └──────┬───────┘  └──────┬───────┘  └─────────────────┘   │
└─────────┼──────────────────┼──────────────────────────────┘
          │                  │
          └──────────┬───────┘
                     │ HTTPS
          ┌──────────▼───────────┐
          │   FastAPI Backend    │
          │  ┌────────────────┐  │
          │  │ Chat Endpoint  │  │
          │  │ Auth/Rate Limit│  │
          │  │ RAG Orchestrator│ │
          │  └────────────────┘  │
          └──┬────────┬────────┬─┘
             │        │        │
    ┌────────▼──┐ ┌──▼─────┐ ┌▼──────────┐
    │  OpenAI   │ │ Qdrant │ │   Neon    │
    │  Agents   │ │ Vector │ │ Postgres  │
    │   API     │ │   DB   │ │  Database │
    └───────────┘ └────────┘ └───────────┘
```

---

## Phase 1: Foundation & Setup

### 1.1 Environment Setup
**Goal:** Establish development environment and service accounts

- [ ] Set up Python 3.11+ environment
- [ ] Create FastAPI project structure
- [ ] Configure environment variables (.env)
- [ ] Set up version control (.gitignore for secrets)

### 1.2 Service Provisioning
**Goal:** Create and configure external services

#### Qdrant Cloud
- [ ] Create Qdrant Cloud free tier account
- [ ] Create collection: `book_embeddings`
- [ ] Configure vector dimensions (1536 for text-embedding-3-small)
- [ ] Get API key and cluster URL

#### Neon Postgres
- [ ] Create Neon serverless Postgres account
- [ ] Create database: `ebook_chatbot`
- [ ] Get connection string
- [ ] Set up connection pooling

#### OpenAI API
- [ ] Get OpenAI API key
- [ ] Set up billing/limits
- [ ] Test API access

### 1.3 Database Schema Design
**Goal:** Design and implement Postgres schema

```sql
-- Users table (anonymous sessions)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW()
);

-- Book metadata
CREATE TABLE book_metadata (
    book_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500),
    version VARCHAR(50),
    total_chapters INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chunks (text segments)
CREATE TABLE chunks (
    chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES book_metadata(book_id),
    chapter_num INT,
    chapter_title VARCHAR(500),
    section_title VARCHAR(500),
    chunk_text TEXT,
    chunk_index INT,
    token_count INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chat history
CREATE TABLE chat_history (
    chat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    question TEXT,
    answer TEXT,
    selected_text TEXT,
    retrieval_mode VARCHAR(50), -- 'default' or 'selected'
    chunks_used UUID[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback
CREATE TABLE feedback (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chat_history(chat_id),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_chunks_book_chapter ON chunks(book_id, chapter_num);
CREATE INDEX idx_chat_history_user ON chat_history(user_id, created_at DESC);
CREATE INDEX idx_feedback_chat ON feedback(chat_id);
```

---

## Phase 2: Backend Development

### 2.1 FastAPI Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Environment config
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── chat.py         # Chat endpoints
│   │   │   ├── health.py       # Health check
│   │   │   └── feedback.py     # Feedback endpoints
│   │   └── middleware/
│   │       ├── rate_limit.py   # Rate limiting
│   │       └── auth.py         # Session auth
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py      # RAG orchestration
│   │   ├── retrieval_service.py # Qdrant queries
│   │   ├── agent_service.py    # OpenAI agent calls
│   │   └── db_service.py       # Database operations
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic models
│   │   └── database.py         # SQLAlchemy models
│   │
│   └── utils/
│       ├── __init__.py
│       ├── embeddings.py       # Embedding generation
│       ├── chunking.py         # Text chunking
│       └── validators.py       # Input validation
│
├── tests/
│   ├── test_api.py
│   ├── test_rag.py
│   └── test_retrieval.py
│
├── requirements.txt
├── .env.example
└── README.md
```

### 2.2 Core Services Implementation Order

#### 2.2.1 Database Service (`db_service.py`)
- [ ] Set up SQLAlchemy engine
- [ ] Implement connection pooling
- [ ] Create CRUD operations for all tables
- [ ] Add transaction management

#### 2.2.2 Embedding Service (`embeddings.py`)
- [ ] OpenAI embeddings client setup
- [ ] Batch embedding generation
- [ ] Error handling and retries
- [ ] Cost tracking

#### 2.2.3 Retrieval Service (`retrieval_service.py`)
- [ ] Qdrant client setup
- [ ] Semantic search implementation
- [ ] Result ranking and filtering
- [ ] Selected-text mode logic

#### 2.2.4 Agent Service (`agent_service.py`)
- [ ] OpenAI Agents SDK integration
- [ ] System prompt engineering
- [ ] Context injection
- [ ] Response parsing

#### 2.2.5 RAG Orchestration (`rag_service.py`)
- [ ] Coordinate retrieval → agent → response flow
- [ ] Implement grounding rules
- [ ] Handle fallback cases
- [ ] Add logging and telemetry

### 2.3 API Endpoints

#### `/api/chat` (POST)
```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
):
    # 1. Validate input
    # 2. Get/create user session
    # 3. Determine retrieval mode
    # 4. Retrieve relevant chunks
    # 5. Generate response via agent
    # 6. Store in chat_history
    # 7. Return response with sources
```

#### `/api/chat/history` (GET)
```python
@router.get("/chat/history")
async def get_history(
    user_id: UUID,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    # Return recent chat history for user
```

#### `/api/health` (GET)
```python
@router.get("/health")
async def health_check():
    # Check Qdrant, Neon, OpenAI connectivity
    # Return service status
```

#### `/api/feedback` (POST)
```python
@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    session: Session = Depends(get_session)
):
    # Store user feedback
```

---

## Phase 3: Data Preparation & Ingestion

### 3.1 Book Content Extraction
**Goal:** Extract text from existing book chapters

- [ ] Read all markdown files from `docs/book-chapters/`
- [ ] Parse chapter structure (titles, sections)
- [ ] Extract clean text content
- [ ] Preserve metadata (chapter, section, hierarchy)

### 3.2 Chunking Strategy
**Goal:** Split content into optimal chunks for RAG

**Approach:**
- Chunk size: 500-800 tokens
- Overlap: 100 tokens
- Preserve semantic boundaries (paragraphs, sections)
- Include chapter/section context in metadata

```python
def chunk_book_content(chapter_text, chapter_metadata):
    """
    Smart chunking that:
    - Respects paragraph boundaries
    - Adds chapter/section headers to chunks
    - Maintains semantic coherence
    """
    # Implementation details in chunking.py
```

### 3.3 Embedding Generation
**Goal:** Create vector embeddings for all chunks

- [ ] Generate embeddings using `text-embedding-3-small`
- [ ] Batch processing (100 chunks per batch)
- [ ] Store embeddings in Qdrant
- [ ] Store chunk metadata in Neon Postgres
- [ ] Link chunks to embeddings via chunk_id

### 3.4 Ingestion Pipeline
**Script:** `scripts/ingest_book.py`

```python
async def ingest_book():
    # 1. Extract chapters from markdown
    # 2. Chunk content
    # 3. Generate embeddings
    # 4. Upload to Qdrant
    # 5. Store metadata in Postgres
    # 6. Verify integrity
```

---

## Phase 4: Frontend Integration

### 4.1 Chat Widget Component
**Location:** `src/components/ChatWidget/`

**Features:**
- Collapsible chat interface
- Message history display
- Input field with validation
- Loading states
- Error handling

**Files:**
```
src/components/ChatWidget/
├── index.tsx              # Main widget component
├── ChatMessage.tsx        # Individual message
├── ChatInput.tsx          # Input field
├── ChatHistory.tsx        # Message list
├── styles.module.css      # Styling
└── hooks/
    └── useChat.ts         # Chat API hook
```

### 4.2 Text Selection Feature
**Goal:** Allow users to select text and ask questions about it

```typescript
// Text selection handler
const handleTextSelection = () => {
  const selectedText = window.getSelection()?.toString();
  if (selectedText && selectedText.length > 0) {
    setSelectedContext(selectedText);
    openChatWidget();
  }
};
```

### 4.3 API Client
**Location:** `src/services/chatApi.ts`

```typescript
export const chatApi = {
  sendMessage: async (question: string, selectedText?: string) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, selected_text: selectedText })
    });
    return response.json();
  },

  getHistory: async () => {
    // Fetch chat history
  },

  submitFeedback: async (chatId: string, rating: number) => {
    // Submit feedback
  }
};
```

### 4.4 Docusaurus Integration
- [ ] Add chat widget to theme layout
- [ ] Configure CORS for API calls
- [ ] Add environment variables for API URL
- [ ] Style integration with existing theme

---

## Phase 5: Security & Optimization

### 5.1 Rate Limiting
**Implementation:** `app/api/middleware/rate_limit.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to endpoints
@limiter.limit("20/minute")  # Per IP
async def chat_endpoint():
    ...
```

### 5.2 Input Validation & Sanitization
- [ ] Max question length: 500 chars
- [ ] Max selected text: 5000 chars
- [ ] Strip HTML/JS from input
- [ ] Detect prompt injection patterns

### 5.3 Prompt Engineering
**System Prompt Template:**
```
You are a helpful assistant for a robotics textbook.

RULES:
1. Answer ONLY based on the provided context
2. If the context doesn't contain the answer, say: "This question cannot be answered from the book's content."
3. Do NOT use external knowledge
4. Keep answers concise (max 300 words)
5. Cite the chapter/section when possible

CONTEXT:
{retrieved_chunks}

USER QUESTION:
{user_question}
```

### 5.4 Caching Strategy
- [ ] Cache embeddings for common queries
- [ ] Cache OpenAI responses (1 hour TTL)
- [ ] Implement Redis if needed for scale

---

## Phase 6: Testing & Quality Assurance

### 6.1 Unit Tests
- [ ] Test retrieval service
- [ ] Test agent service
- [ ] Test RAG orchestration
- [ ] Test API endpoints

### 6.2 Integration Tests
- [ ] End-to-end chat flow
- [ ] Selected-text mode
- [ ] Rate limiting
- [ ] Error handling

### 6.3 Grounding Tests
**Critical:** Verify no hallucination

Test cases:
- [ ] Question outside book scope → Rejection
- [ ] Ambiguous question → Clarification request
- [ ] Selected text without answer → Appropriate response
- [ ] Valid question → Accurate, grounded answer

### 6.4 Performance Testing
- [ ] Response time < 3s (p95)
- [ ] Concurrent user load (50+ users)
- [ ] Vector search latency
- [ ] Database query optimization

---

## Phase 7: Deployment

### 7.1 Backend Deployment
**Options:**
- Vercel (serverless functions)
- Railway
- Render
- AWS Lambda + API Gateway

**Steps:**
- [ ] Containerize FastAPI app (Docker)
- [ ] Set up environment variables
- [ ] Configure CORS for frontend domain
- [ ] Deploy and test

### 7.2 Database Migration
- [ ] Run schema creation scripts on Neon
- [ ] Ingest book content
- [ ] Verify data integrity

### 7.3 Frontend Deployment
- [ ] Build Docusaurus with chat widget
- [ ] Configure API endpoint URLs
- [ ] Deploy to Vercel/current host
- [ ] Test end-to-end

### 7.4 Monitoring
- [ ] Set up logging (structured logs)
- [ ] Error tracking (Sentry)
- [ ] Usage analytics
- [ ] Cost monitoring (OpenAI API usage)

---

## Phase 8: Iteration & Improvement

### 8.1 User Feedback Loop
- [ ] Collect ratings on responses
- [ ] Analyze common failure cases
- [ ] Improve retrieval logic
- [ ] Refine system prompts

### 8.2 Performance Optimization
- [ ] Optimize vector search parameters
- [ ] Improve chunking strategy
- [ ] Reduce latency bottlenecks
- [ ] Optimize costs

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| OpenAI API rate limits | Implement exponential backoff, caching |
| Qdrant free tier limits | Monitor usage, optimize queries, plan upgrade |
| Hallucination | Strict system prompts, grounding tests, user feedback |
| Slow response time | Async processing, caching, optimized retrieval |
| Prompt injection | Input validation, system prompt hardening |

---

## Success Criteria

- [ ] All grounding rules enforced (no hallucination)
- [ ] Response time < 3s (p95)
- [ ] Rate limiting works correctly
- [ ] Selected-text mode functions properly
- [ ] Chat history persists
- [ ] User feedback collection works
- [ ] Deployment successful and stable

---

## Dependencies

### Python Packages
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
qdrant-client==1.7.0
openai==1.10.0
python-dotenv==1.0.0
slowapi==0.1.9
pydantic==2.5.0
tiktoken==0.5.2
```

### Frontend Packages
```
@docusaurus/core
@docusaurus/preset-classic
react
react-dom
```

---

## Timeline Overview

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1. Foundation & Setup | Day 1 | None |
| 2. Backend Development | Days 2-4 | Phase 1 |
| 3. Data Preparation | Day 5 | Phase 2 |
| 4. Frontend Integration | Days 6-7 | Phase 2 |
| 5. Security & Optimization | Day 8 | Phase 2, 4 |
| 6. Testing | Days 9-10 | All previous |
| 7. Deployment | Day 11 | All previous |
| 8. Iteration | Ongoing | Phase 7 |

---

## Next Steps

1. Review and approve this plan
2. Generate detailed task breakdown
3. Begin Phase 1: Foundation & Setup
4. Set up development environment
5. Provision external services
