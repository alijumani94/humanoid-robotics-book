"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    question: str = Field(..., max_length=500, description="User's question")
    selected_text: Optional[str] = Field(None, max_length=5000, description="Selected text from book")
    user_id: Optional[UUID4] = Field(None, description="User session ID")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is forward kinematics?",
                "selected_text": None,
                "user_id": None
            }
        }


class ChunkReference(BaseModel):
    """Reference to a source chunk."""
    chunk_id: UUID4
    chapter_title: str
    section_title: Optional[str] = None
    score: float
    text_preview: str = Field(..., description="First 200 chars of chunk")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    chat_id: UUID4
    answer: str
    sources: List[ChunkReference]
    retrieval_mode: str = Field(..., description="'default' or 'selected'")
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": "123e4567-e89b-12d3-a456-426614174000",
                "answer": "According to Chapter 2: Robot Locomotion...",
                "sources": [
                    {
                        "chunk_id": "123e4567-e89b-12d3-a456-426614174001",
                        "chapter_title": "Chapter 2: Robot Locomotion",
                        "section_title": "Forward Kinematics",
                        "score": 0.89,
                        "text_preview": "Forward kinematics is the process of..."
                    }
                ],
                "retrieval_mode": "default",
                "timestamp": "2025-12-26T10:00:00"
            }
        }


class ChatHistoryItem(BaseModel):
    """Single chat history item."""
    chat_id: UUID4
    question: str
    answer: str
    timestamp: datetime
    retrieval_mode: str


class ChatHistoryResponse(BaseModel):
    """Response schema for chat history endpoint."""
    user_id: UUID4
    history: List[ChatHistoryItem]
    total: int


class FeedbackRequest(BaseModel):
    """Request schema for feedback endpoint."""
    chat_id: UUID4
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": "123e4567-e89b-12d3-a456-426614174000",
                "rating": 5,
                "comment": "Very helpful answer!"
            }
        }


class FeedbackResponse(BaseModel):
    """Response schema for feedback endpoint."""
    success: bool
    message: str


class HealthCheckResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str
    services: dict
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "services": {
                    "database": "connected",
                    "qdrant": "connected",
                    "openai": "connected"
                },
                "timestamp": "2025-12-26T10:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Generic error response schema."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
