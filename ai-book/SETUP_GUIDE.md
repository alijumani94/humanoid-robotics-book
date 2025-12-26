# RAG Chatbot Setup Guide

Complete setup guide for the RAG-powered e-book chatbot.

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for Docusaurus)
- **OpenAI API Key**
- **Qdrant Cloud Account** (Free Tier)
- **Neon Serverless Postgres** (Free Tier)

---

## Part 1: Backend Setup

### Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key

# Neon Postgres
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# App Config
ENVIRONMENT=development
API_RATE_LIMIT_PER_MINUTE=20
ALLOWED_ORIGINS=http://localhost:3000
```

### Step 4: Set Up Qdrant Cloud

1. Go to https://cloud.qdrant.io
2. Create a free tier account
3. Create a new cluster
4. Get your cluster URL and API key
5. Add to `.env`

### Step 5: Set Up Neon Postgres

1. Go to https://neon.tech
2. Create a free account
3. Create a new project and database
4. Copy the connection string
5. Add to `.env` (replace `postgresql://` with `postgresql+asyncpg://`)

### Step 6: Initialize Database

The database schema will be created automatically on first run, but you can also run:

```bash
# Using the SQL script
psql $DATABASE_URL < scripts/create_schema.sql
```

### Step 7: Ingest Book Content

```bash
cd backend
python scripts/ingest_book.py
```

This will:
- Extract all chapters from `docs/book-chapters/`
- Chunk the content
- Generate embeddings
- Upload to Qdrant and Postgres

Expected output:
```
INFO - Found 4 chapters
INFO - Processing: Chapter 1: Introduction
INFO - Created 15 chunks
INFO - Generated 15 embeddings
...
INFO - === Ingestion Complete ===
INFO - Total chapters: 4
INFO - Total chunks: 87
```

### Step 8: Run the Backend

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### Step 9: Test the API

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "qdrant": "connected",
    "openai": "connected"
  }
}
```

---

## Part 2: Frontend Setup

### Step 1: Install Dependencies

```bash
# From project root
npm install
```

### Step 2: Configure API URL

Create `.env` in project root:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

For production:

```env
REACT_APP_API_URL=https://your-backend-url.com/api
```

### Step 3: Run Development Server

```bash
npm start
```

The site will be available at: http://localhost:3000

### Step 4: Test the Chatbot

1. Open http://localhost:3000
2. Click the chat bubble in the bottom-right
3. Ask a question: "What is forward kinematics?"
4. Try selecting text from a chapter and asking a question

---

## Part 3: Deployment

### Deploy Backend

#### Option 1: Docker

```bash
cd backend

# Build image
docker build -t rag-chatbot-backend .

# Run container
docker run -p 8000:8000 --env-file .env rag-chatbot-backend
```

#### Option 2: Railway

1. Create account at https://railway.app
2. Create new project from GitHub repo
3. Add environment variables
4. Deploy

#### Option 3: Render

1. Create account at https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Add environment variables
5. Deploy

### Deploy Frontend

The frontend deploys with your existing Docusaurus site.

#### Vercel (Current Setup)

1. Add backend URL to Vercel environment variables:
   ```
   REACT_APP_API_URL=https://your-backend-url.com/api
   ```

2. Deploy:
   ```bash
   npm run build
   vercel deploy
   ```

---

## Part 4: Testing

### Test Backend Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Chat (replace with your actual endpoint)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is inverse kinematics?",
    "selected_text": null
  }'
```

### Test Grounding Rules

Ask questions that are:

1. **In scope**: "What are the main types of robot locomotion?"
   - Expected: Grounded answer with sources

2. **Out of scope**: "What's the weather today?"
   - Expected: "This question cannot be answered from the book's content."

3. **With selected text**: Select a paragraph about sensors, then ask "What sensors are mentioned here?"
   - Expected: Answer based only on selected text

---

## Part 5: Monitoring

### Check Logs

```bash
# Backend logs (if using uvicorn)
tail -f uvicorn.log

# Docker logs
docker logs -f <container-id>
```

### Monitor Usage

- **OpenAI**: Check usage at https://platform.openai.com/usage
- **Qdrant**: Check dashboard at https://cloud.qdrant.io
- **Neon**: Check dashboard at https://neon.tech

---

## Troubleshooting

### "Collection not found" error

Run the ingestion script:
```bash
python scripts/ingest_book.py
```

### CORS errors

Check `ALLOWED_ORIGINS` in backend `.env` matches your frontend URL.

### "Failed to connect to database"

1. Verify connection string in `.env`
2. Check Neon dashboard - database might be sleeping (free tier)
3. Ensure using `postgresql+asyncpg://` prefix

### Slow responses

1. Check OpenAI API status
2. Reduce `top_k_retrieval` in config
3. Check Qdrant query performance

### Rate limiting issues

Adjust in `.env`:
```env
API_RATE_LIMIT_PER_MINUTE=50
```

---

## Next Steps

1. **Add more content**: Ingest additional chapters
2. **Improve chunking**: Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP`
3. **Fine-tune prompts**: Edit system prompt in `agent_service.py`
4. **Add analytics**: Track usage and feedback
5. **Implement caching**: Add Redis for common queries

---

## Support

For issues or questions:
- Check the logs
- Review the API documentation at `/docs`
- See the project README
- File an issue on GitHub

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         Docusaurus Frontend                  │
│  ┌──────────────────────────────────────┐  │
│  │       ChatWidget Component            │  │
│  └──────────────────────────────────────┘  │
└─────────────────┬───────────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────────┐
│         FastAPI Backend                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   RAG    │  │Retrieval │  │  Agent   │  │
│  │Orchestr. │→ │ Service  │→ │ Service  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
└────┬────────────────┬────────────────┬──────┘
     │                │                │
┌────▼────┐    ┌──────▼──────┐   ┌────▼─────┐
│  Neon   │    │   Qdrant    │   │  OpenAI  │
│Postgres │    │   Vector    │   │   API    │
└─────────┘    └─────────────┘   └──────────┘
```

---

## Configuration Reference

### Backend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `QDRANT_URL` | Qdrant cluster URL | - | Yes |
| `QDRANT_API_KEY` | Qdrant API key | - | Yes |
| `DATABASE_URL` | Postgres connection string | - | Yes |
| `ENVIRONMENT` | Environment (development/production) | development | No |
| `API_RATE_LIMIT_PER_MINUTE` | Rate limit per IP | 20 | No |
| `ALLOWED_ORIGINS` | CORS allowed origins | http://localhost:3000 | No |
| `CHUNK_SIZE` | Max tokens per chunk | 600 | No |
| `CHUNK_OVERLAP` | Token overlap between chunks | 100 | No |
| `TOP_K_RETRIEVAL` | Number of chunks to retrieve | 5 | No |
| `SIMILARITY_THRESHOLD` | Minimum similarity score | 0.7 | No |

### Frontend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REACT_APP_API_URL` | Backend API URL | http://localhost:8000/api | Yes |

---

## Done! 🎉

Your RAG chatbot is now set up and ready to answer questions about your robotics textbook!
