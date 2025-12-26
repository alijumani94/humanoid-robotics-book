"""Chat endpoints for RAG chatbot."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    ChatHistoryItem,
    ChunkReference,
)
from app.models.database import User, ChatHistory
from app.services.db_service import get_db
from app.services.rag_service import process_question
from app.utils.validators import validate_input
from app.api.middleware.rate_limit import limiter
from fastapi import Request
from datetime import datetime
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_or_create_user_id(request_user_id: UUID = None) -> UUID:
    """Get or create user ID for session tracking."""
    if request_user_id:
        return request_user_id
    return uuid4()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")  # Per-user rate limit
async def chat(
    request: Request,
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Process a chat question and return an answer.

    Args:
        chat_request: ChatRequest with question and optional selected_text
        db: Database session

    Returns:
        ChatResponse with answer and sources
    """
    try:
        # Validate input
        is_valid, error_msg = validate_input(
            chat_request.question,
            chat_request.selected_text
        )

        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Get or create user
        user_id = get_or_create_user_id(chat_request.user_id)

        # Process question through RAG pipeline
        logger.info(f"Processing question: {chat_request.question[:50]}...")

        rag_response = await process_question(
            question=chat_request.question,
            selected_text=chat_request.selected_text,
        )

        # Store in chat history
        chat_id = uuid4()
        chunks_used = [UUID(chunk.chunk_id) for chunk in rag_response.chunks]

        chat_history = ChatHistory(
            chat_id=chat_id,
            user_id=user_id,
            question=chat_request.question,
            answer=rag_response.answer,
            selected_text=chat_request.selected_text,
            retrieval_mode=rag_response.retrieval_mode,
            chunks_used=chunks_used,
        )

        db.add(chat_history)
        await db.commit()

        # Format response
        sources = [
            ChunkReference(
                chunk_id=UUID(chunk.chunk_id),
                chapter_title=chunk.chapter_title,
                section_title=chunk.section_title,
                score=chunk.score,
                text_preview=chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
            )
            for chunk in rag_response.chunks
        ]

        return ChatResponse(
            chat_id=chat_id,
            answer=rag_response.answer,
            sources=sources,
            retrieval_mode=rag_response.retrieval_mode,
            timestamp=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="An error occurred processing your question")


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: UUID,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    Get chat history for a user.

    Args:
        user_id: User ID
        limit: Maximum number of history items to return
        db: Database session

    Returns:
        ChatHistoryResponse with history items
    """
    try:
        # Query chat history
        stmt = (
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
        )

        result = await db.execute(stmt)
        history_records = result.scalars().all()

        # Format response
        history = [
            ChatHistoryItem(
                chat_id=record.chat_id,
                question=record.question,
                answer=record.answer,
                timestamp=record.created_at,
                retrieval_mode=record.retrieval_mode,
            )
            for record in history_records
        ]

        return ChatHistoryResponse(
            user_id=user_id,
            history=history,
            total=len(history),
        )

    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chat history")
