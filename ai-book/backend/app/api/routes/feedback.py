"""Feedback endpoint for user ratings."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import FeedbackRequest, FeedbackResponse
from app.models.database import Feedback
from app.services.db_service import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback_request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit feedback for a chat response.

    Args:
        feedback_request: FeedbackRequest with rating and optional comment
        db: Database session

    Returns:
        FeedbackResponse indicating success
    """
    try:
        # Create feedback record
        feedback = Feedback(
            chat_id=feedback_request.chat_id,
            rating=feedback_request.rating,
            comment=feedback_request.comment,
        )

        db.add(feedback)
        await db.commit()

        logger.info(f"Feedback submitted for chat {feedback_request.chat_id}: {feedback_request.rating}/5")

        return FeedbackResponse(
            success=True,
            message="Thank you for your feedback!"
        )

    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Error submitting feedback")
