# Spec 001: RAG Chatbot for E-Book Website

**Status:** Draft
**Created:** 2025-12-26
**Author:** Spec-Kit Plus
**Priority:** High

---

## 1. Purpose & Scope

Implement a Retrieval-Augmented Generation (RAG) chatbot embedded within the e-book website to assist users with book-related questions.

### Key Capabilities
- Answer user questions strictly about the book's content
- Support context-aware answers based on user-selected text
- Use OpenAI Agents/ChatKit SDK for reasoning and response generation
- Use FastAPI as the backend API layer
- Use Qdrant Cloud (Free Tier) for vector similarity search
- Use Neon Serverless Postgres for metadata, users, and chat history

### Constraints
- The chatbot is an assistive feature and must not act as a general-purpose AI
- Must operate within strict grounding rules to prevent hallucination

---

## 2. Grounding & Knowledge Rules (Hard Constraints)

| Rule | Description | Enforcement Level |
|------|-------------|-------------------|
| Content Boundary | The chatbot **MUST NOT** answer questions outside the book's content | HARD |
| Grounding Requirement | All responses **MUST** be grounded in retrieved passages | HARD |
| Fallback Message | If no relevant context is found, reply with: *"This question cannot be answered from the book's content."* | HARD |
| No Hallucination | Hallucination is strictly forbidden | HARD |
| No External Sources | The chatbot **MUST NOT** use external knowledge sources | HARD |

---

## 3. Retrieval Rules (RAG Behavior)

### 3.1 Default Retrieval Mode
- Retrieve relevant chunks from Qdrant using semantic similarity
- Use embeddings generated from the book content only
- Rank and filter results before passing context to the agent
- Top-K retrieval with configurable threshold

### 3.2 Selected-Text Mode
When the user selects text from the book:

1. The chatbot **MUST** restrict retrieval to the selected text only
2. No other book sections may be used
3. If the selected text does not contain the answer, the chatbot must say so explicitly

**Selection Workflow:**
```
User selects text → Frontend sends selection + question → Backend restricts RAG scope → Agent responds only from selection
```

---

## 4. Agent & Reasoning Constraints

### OpenAI Agent Behavior
1. **Input:** Receive only retrieved context as input
2. **No Inference:** Never infer beyond provided text
3. **Citation:** Prefer direct citations or paraphrases
4. **Internal CoT:** Chain-of-thought must remain internal
5. **Output:** Final response must be concise, clear, and factual

### System Prompt Structure
- Define strict boundaries
- Enforce grounding rules
- Prevent prompt injection
- Include fallback instructions

---

## 5. Data Storage & Privacy

### 5.1 Neon Postgres Schema

**Tables:**
- `users` - User sessions (anonymous or authenticated)
- `chat_history` - Question, answer, timestamps, user_id
- `book_metadata` - Book info, chapter structure
- `chunks` - Chunk text, chunk_id, metadata references

### 5.2 Qdrant Collections

**Structure:**
- Collection: `book_embeddings`
- Vectors: Embeddings of book chunks
- Payload: chunk_id, chapter, section, page_reference

**Privacy Rules:**
- No user-private data stored in Qdrant
- No raw book content logged unnecessarily
- Chat history retention policy: 30 days (configurable)

---

## 6. API Architecture

### 6.1 Architecture Principle
FastAPI acts as the single backend interface. The frontend must never directly access:
- Qdrant
- OpenAI APIs
- Neon database

### 6.2 API Endpoints

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/api/chat` | POST | Submit question | `{ question, context?, selected_text? }` | `{ answer, sources, metadata }` |
| `/api/chat/history` | GET | Retrieve chat history | Query params: `user_id, limit` | `{ history[] }` |
| `/api/health` | GET | Health check | - | `{ status, services }` |
| `/api/feedback` | POST | User feedback on response | `{ chat_id, rating, comment? }` | `{ success }` |

### 6.3 Request Validation
- All inputs sanitized
- Max question length: 500 characters
- Selected text max: 5000 characters
- User session validation

---

## 7. Security & Abuse Prevention

### 7.1 Rate Limiting
- Per IP: 20 requests/minute
- Per user session: 10 requests/minute
- Burst allowance: 5 additional requests

### 7.2 Abuse Prevention
The chatbot must refuse:
- System prompt extraction attempts
- Attempts to bypass content restrictions
- Requests for training data or internal logic
- Prompt injection patterns

### 7.3 Input Sanitization
- Strip HTML/JavaScript
- Detect and block injection attempts
- Validate selected text is from book content

---

## 8. UX & Response Guidelines

### 8.1 Response Quality
Responses must:
- Be short and relevant (max 300 words)
- Use simple language
- Avoid unnecessary verbosity
- Remain neutral and instructional

### 8.2 Context Attribution
When applicable, mention:
- Chapter name
- Section title
- Page reference (if available)

**Example:**
> "According to Chapter 2: Robot Locomotion, humanoid robots use..."

### 8.3 Error States
- **No context found:** "This question cannot be answered from the book's content."
- **Ambiguous question:** "Could you please rephrase your question? I need more context."
- **Rate limit:** "You're asking too many questions. Please wait a moment."
- **Service error:** "I'm having trouble right now. Please try again."

---

## 9. Technology Stack

| Component | Technology | Purpose |
|-----------|----------|---------|
| Frontend | Docusaurus + React | E-book website with chat widget |
| Backend | FastAPI (Python) | API server |
| Vector DB | Qdrant Cloud (Free Tier) | Semantic search |
| Database | Neon Serverless Postgres | Metadata, history, users |
| AI Agent | OpenAI Agents/ChatKit SDK | RAG reasoning & response |
| Embeddings | OpenAI text-embedding-3-small | Vector generation |

---

## 10. Non-Functional Requirements

### 10.1 Performance
- Response time: < 3 seconds (p95)
- Retrieval latency: < 500ms
- Concurrent users: Support 50+

### 10.2 Reliability
- Uptime: 99% target
- Graceful degradation on service failures
- Retry logic for transient errors

### 10.3 Scalability
- Vector DB: Qdrant free tier limits
- Database: Neon free tier (monitor usage)
- API: Stateless design for horizontal scaling

---

## 11. Success Metrics

- User engagement: % of visitors who use chatbot
- Answer accuracy: User feedback ratings
- Retrieval precision: % of relevant chunks retrieved
- Error rate: < 5% of requests
- Average response time: < 2 seconds

---

## 12. Future Enhancements (Out of Scope for v1)

- Multi-book support
- Voice input/output
- Multi-language support
- User accounts with saved history
- Admin dashboard for analytics
- Fine-tuned embeddings model

---

## 13. Acceptance Criteria

- [ ] Chatbot answers questions grounded in book content only
- [ ] Selected-text mode restricts retrieval correctly
- [ ] No hallucination detected in testing
- [ ] Rate limiting prevents abuse
- [ ] Responses include chapter/section attribution
- [ ] Error states display correctly
- [ ] API endpoints secured and validated
- [ ] Chat history persists in database
- [ ] Vector search returns relevant results
- [ ] Response time meets performance targets

---

## 14. Dependencies & Risks

### Dependencies
- OpenAI API access and quota
- Qdrant Cloud free tier availability
- Neon Postgres free tier limits

### Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | High | Implement caching, optimize retrieval |
| Free tier limits | Medium | Monitor usage, plan upgrade path |
| Hallucination | High | Strict grounding rules, testing |
| Prompt injection | Medium | Input validation, system prompt hardening |

---

## 15. References

- OpenAI Agents Documentation
- Qdrant Cloud Setup Guide
- Neon Serverless Postgres Docs
- FastAPI Best Practices
- RAG Architecture Patterns
