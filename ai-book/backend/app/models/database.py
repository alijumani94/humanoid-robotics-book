"""SQLAlchemy database models."""

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, ARRAY, Float, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class User(Base):
    """User sessions table."""
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_token = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_active = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class BookMetadata(Base):
    """Book metadata table."""
    __tablename__ = "book_metadata"

    book_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    version = Column(String(50))
    total_chapters = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Chunk(Base):
    """Text chunks table."""
    __tablename__ = "chunks"

    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("book_metadata.book_id"))
    chapter_num = Column(Integer, nullable=False)
    chapter_title = Column(String(500), nullable=False)
    section_title = Column(String(500))
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    token_count = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())


class ChatHistory(Base):
    """Chat history table."""
    __tablename__ = "chat_history"

    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    selected_text = Column(Text)
    retrieval_mode = Column(String(50), nullable=False)  # 'default' or 'selected'
    chunks_used = Column(ARRAY(UUID(as_uuid=True)))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Feedback(Base):
    """Feedback table."""
    __tablename__ = "feedback"

    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chat_history.chat_id"))
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comment = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
