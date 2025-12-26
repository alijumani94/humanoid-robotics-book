"""Retrieval service for querying Qdrant vector database."""

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from app.config import settings
from app.utils.embeddings import generate_embedding
from typing import List, Dict, Optional
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

# Initialize Qdrant client
qdrant_client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
)

COLLECTION_NAME = "book_embeddings"


class ChunkResult:
    """Represents a retrieved chunk with score."""

    def __init__(
        self,
        chunk_id: UUID,
        text: str,
        chapter_title: str,
        section_title: Optional[str],
        score: float,
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.chapter_title = chapter_title
        self.section_title = section_title
        self.score = score

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "chunk_id": str(self.chunk_id),
            "text": self.text,
            "chapter_title": self.chapter_title,
            "section_title": self.section_title,
            "score": self.score,
        }


async def search_similar_chunks(
    query: str,
    top_k: int = None,
    score_threshold: float = None,
) -> List[ChunkResult]:
    """
    Search for similar chunks using semantic similarity.

    Args:
        query: User's question
        top_k: Number of results to return
        score_threshold: Minimum similarity score

    Returns:
        List of ChunkResult objects
    """
    top_k = top_k or settings.top_k_retrieval
    score_threshold = score_threshold or settings.similarity_threshold

    try:
        # Generate query embedding
        query_vector = await generate_embedding(query)

        # Search Qdrant
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            score_threshold=score_threshold,
        )

        # Convert to ChunkResult objects
        chunks = []
        for result in search_results:
            chunks.append(
                ChunkResult(
                    chunk_id=UUID(result.payload["chunk_id"]),
                    text=result.payload["text"],
                    chapter_title=result.payload["chapter_title"],
                    section_title=result.payload.get("section_title"),
                    score=result.score,
                )
            )

        logger.info(f"Retrieved {len(chunks)} chunks for query: {query[:50]}...")
        return chunks

    except Exception as e:
        logger.error(f"Error searching chunks: {e}")
        raise


async def search_in_selected_text(
    query: str,
    selected_text: str,
) -> Optional[ChunkResult]:
    """
    Search within selected text only (no vector search).

    This creates a virtual chunk from the selected text and returns it
    if it seems relevant to the query.

    Args:
        query: User's question
        selected_text: Text selected by user

    Returns:
        ChunkResult if relevant, None otherwise
    """
    try:
        # For selected text mode, we simply return the selected text as a chunk
        # The agent will determine if it contains the answer
        return ChunkResult(
            chunk_id=UUID("00000000-0000-0000-0000-000000000000"),  # Placeholder
            text=selected_text,
            chapter_title="Selected Text",
            section_title=None,
            score=1.0,  # Always max score for selected text
        )

    except Exception as e:
        logger.error(f"Error processing selected text: {e}")
        raise


async def upload_chunk_to_qdrant(
    chunk_id: UUID,
    text: str,
    embedding: List[float],
    chapter_title: str,
    section_title: Optional[str] = None,
) -> bool:
    """
    Upload a single chunk with embedding to Qdrant.

    Args:
        chunk_id: Unique chunk identifier
        text: Chunk text
        embedding: Vector embedding
        chapter_title: Chapter title
        section_title: Section title (optional)

    Returns:
        bool: True if successful
    """
    try:
        point = PointStruct(
            id=str(chunk_id),
            vector=embedding,
            payload={
                "chunk_id": str(chunk_id),
                "text": text,
                "chapter_title": chapter_title,
                "section_title": section_title,
            },
        )

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point],
        )

        return True

    except Exception as e:
        logger.error(f"Error uploading chunk to Qdrant: {e}")
        return False


async def check_qdrant_health() -> bool:
    """
    Check if Qdrant is healthy.

    Returns:
        bool: True if healthy
    """
    try:
        collections = qdrant_client.get_collections()
        return True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return False
