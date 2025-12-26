# RAG Chatbot Backend

FastAPI backend for the RAG-powered e-book chatbot.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run database migrations:
```bash
python scripts/create_schema.py
```

5. Ingest book content:
```bash
python scripts/ingest_book.py
```

6. Run the server:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/chat` - Submit a question
- `GET /api/chat/history` - Get chat history
- `POST /api/feedback` - Submit feedback
- `GET /api/health` - Health check

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes and middleware
│   ├── services/     # Business logic
│   ├── models/       # Data models
│   └── utils/        # Utilities
├── scripts/          # Data ingestion scripts
└── tests/            # Tests
```

## Testing

```bash
pytest tests/
```

## Documentation

Interactive API docs available at: http://localhost:8000/docs
