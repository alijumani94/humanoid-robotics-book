"""Embedding generation utilities using OpenAI."""

from openai import AsyncOpenAI
from app.config import settings
from typing import List
import logging
import asyncio

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)

# Embedding model
EMBEDDING_MODEL = "text-embedding-3-small"


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text.

    Args:
        text: Text to embed

    Returns:
        List of floats representing the embedding vector
    """
    try:
        response = await client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """
    Generate embeddings for multiple texts in batches.

    Args:
        texts: List of texts to embed
        batch_size: Number of texts per batch

    Returns:
        List of embedding vectors
    """
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        try:
            response = await client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch,
                encoding_format="float"
            )

            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

            logger.info(f"Generated embeddings for batch {i // batch_size + 1} ({len(batch)} texts)")

            # Small delay to avoid rate limiting
            if i + batch_size < len(texts):
                await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    return all_embeddings


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for

    Returns:
        Number of tokens
    """
    import tiktoken

    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))
    except Exception as e:
        logger.warning(f"Error counting tokens: {e}. Using approximate count.")
        # Fallback: approximate 1 token per 4 characters
        return len(text) // 4
