"""RAG orchestration service - coordinates retrieval and generation."""

from app.services.retrieval_service import (
    search_similar_chunks,
    search_in_selected_text,
    ChunkResult,
)
from app.services.agent_service import generate_response
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RAGResponse:
    """Represents a complete RAG response."""

    def __init__(
        self,
        answer: str,
        chunks: List[ChunkResult],
        retrieval_mode: str,
    ):
        self.answer = answer
        self.chunks = chunks
        self.retrieval_mode = retrieval_mode

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "answer": self.answer,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "retrieval_mode": self.retrieval_mode,
        }


async def process_question(
    question: str,
    selected_text: Optional[str] = None,
) -> RAGResponse:
    """
    Process a user question through the full RAG pipeline.

    Args:
        question: User's question
        selected_text: Optional selected text from the book

    Returns:
        RAGResponse object with answer and metadata
    """
    try:
        # Determine retrieval mode
        if selected_text:
            retrieval_mode = "selected"
            logger.info(f"Using selected-text mode for question: {question[:50]}...")

            # Retrieve from selected text only
            chunk = await search_in_selected_text(question, selected_text)
            chunks = [chunk] if chunk else []

        else:
            retrieval_mode = "default"
            logger.info(f"Using default retrieval mode for question: {question[:50]}...")

            # Retrieve from full book
            chunks = await search_similar_chunks(question)

        # Check if we have any context
        if not chunks:
            logger.warning(f"No relevant context found for question: {question[:50]}...")
            return RAGResponse(
                answer="This question cannot be answered from the book's content.",
                chunks=[],
                retrieval_mode=retrieval_mode,
            )

        # Generate response using agent
        answer = await generate_response(question, chunks)

        # Validate response (basic check for grounding)
        if _seems_hallucinated(answer, chunks):
            logger.warning(f"Potential hallucination detected, returning fallback")
            answer = "This question cannot be answered from the book's content."
            chunks = []

        return RAGResponse(
            answer=answer,
            chunks=chunks,
            retrieval_mode=retrieval_mode,
        )

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise


def _seems_hallucinated(answer: str, chunks: List[ChunkResult]) -> bool:
    """
    Basic heuristic to detect potential hallucination.

    This is a simple check - in production you might want more sophisticated validation.

    Args:
        answer: Generated answer
        chunks: Source chunks

    Returns:
        bool: True if answer seems hallucinated
    """
    # If answer is the fallback message, it's not hallucinated
    if "cannot be answered from the book" in answer.lower():
        return False

    # Check if answer is suspiciously short (might indicate confusion)
    if len(answer.split()) < 10:
        return True

    # Check if answer contains any text from the chunks (basic grounding check)
    # This is a very basic check - you might want to use more sophisticated methods
    combined_context = " ".join([chunk.text.lower() for chunk in chunks])

    # Extract key terms from answer (simple heuristic)
    answer_words = set(answer.lower().split())
    context_words = set(combined_context.split())

    # Check overlap - if there's very little overlap, might be hallucinated
    common_words = answer_words.intersection(context_words)

    # Filter out common stop words for better signal
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "is", "are", "was", "were", "be", "been", "being"}
    meaningful_common = common_words - stop_words

    # If less than 3 meaningful words overlap, might be hallucinated
    if len(meaningful_common) < 3:
        logger.warning(f"Low overlap between answer and context: {len(meaningful_common)} words")
        return True

    return False


async def validate_retrieval_quality(chunks: List[ChunkResult], threshold: float = 0.6) -> bool:
    """
    Validate if retrieved chunks are of sufficient quality.

    Args:
        chunks: Retrieved chunks
        threshold: Minimum average score

    Returns:
        bool: True if quality is sufficient
    """
    if not chunks:
        return False

    avg_score = sum(chunk.score for chunk in chunks) / len(chunks)
    return avg_score >= threshold
