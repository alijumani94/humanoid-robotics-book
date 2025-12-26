"""Script to ingest book content into Qdrant and Postgres."""

import asyncio
import sys
import os
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.utils.chunking import chunk_text, add_context_to_chunk
from app.utils.embeddings import generate_embeddings_batch
from app.services.retrieval_service import upload_chunk_to_qdrant, qdrant_client
from app.services.db_service import AsyncSessionLocal, init_db
from app.models.database import BookMetadata, Chunk
from qdrant_client.models import Distance, VectorParams
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_book_content(docs_path: str) -> list:
    """
    Extract content from markdown files in docs/book-chapters/.

    Args:
        docs_path: Path to docs directory

    Returns:
        List of chapter dictionaries
    """
    chapters = []
    book_chapters_path = Path(docs_path) / "book-chapters"

    if not book_chapters_path.exists():
        logger.error(f"Book chapters directory not found: {book_chapters_path}")
        return chapters

    # Find all chapter markdown files
    chapter_files = sorted(book_chapters_path.glob("chapter_*.md"))

    for i, chapter_file in enumerate(chapter_files, 1):
        logger.info(f"Reading {chapter_file.name}...")

        try:
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title from first heading
            lines = content.split('\n')
            title = "Unknown Chapter"

            for line in lines:
                if line.startswith('# '):
                    title = line.replace('# ', '').strip()
                    break

            chapters.append({
                "chapter_num": i,
                "title": title,
                "content": content,
                "file_path": str(chapter_file)
            })

            logger.info(f"Extracted: {title}")

        except Exception as e:
            logger.error(f"Error reading {chapter_file}: {e}")

    return chapters


async def create_collection_if_not_exists():
    """Create Qdrant collection if it doesn't exist."""
    try:
        collections = qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]

        if "book_embeddings" not in collection_names:
            logger.info("Creating Qdrant collection: book_embeddings")

            qdrant_client.create_collection(
                collection_name="book_embeddings",
                vectors_config=VectorParams(
                    size=settings.vector_dimension,
                    distance=Distance.COSINE
                )
            )

            logger.info("Collection created successfully")
        else:
            logger.info("Collection 'book_embeddings' already exists")

    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise


async def ingest_book(docs_path: str):
    """
    Main ingestion function.

    Args:
        docs_path: Path to docs directory
    """
    logger.info("Starting book ingestion...")

    # Initialize database
    await init_db()

    # Create Qdrant collection
    await create_collection_if_not_exists()

    # Extract book content
    chapters = extract_book_content(docs_path)

    if not chapters:
        logger.error("No chapters found to ingest")
        return

    logger.info(f"Found {len(chapters)} chapters")

    # Create book metadata
    async with AsyncSessionLocal() as db:
        book_id = uuid4()

        book_meta = BookMetadata(
            book_id=book_id,
            title="Humanoid Robotics Textbook",
            version="1.0",
            total_chapters=len(chapters)
        )

        db.add(book_meta)
        await db.commit()

        logger.info(f"Created book metadata: {book_id}")

    # Process each chapter
    total_chunks = 0

    for chapter in chapters:
        logger.info(f"\nProcessing: {chapter['title']}")

        # Chunk the chapter content
        chunks = chunk_text(
            text=chapter["content"],
            chapter_num=chapter["chapter_num"],
            chapter_title=chapter["title"],
        )

        logger.info(f"Created {len(chunks)} chunks")

        # Generate embeddings for all chunks
        chunk_texts = [add_context_to_chunk(chunk) for chunk in chunks]
        embeddings = await generate_embeddings_batch(chunk_texts)

        logger.info(f"Generated {len(embeddings)} embeddings")

        # Upload to Qdrant and Postgres
        async with AsyncSessionLocal() as db:
            for chunk, embedding in zip(chunks, embeddings):
                chunk_id = uuid4()

                # Upload to Qdrant
                await upload_chunk_to_qdrant(
                    chunk_id=chunk_id,
                    text=chunk.text,
                    embedding=embedding,
                    chapter_title=chunk.chapter_title,
                    section_title=chunk.section_title,
                )

                # Store in Postgres
                db_chunk = Chunk(
                    chunk_id=chunk_id,
                    book_id=book_id,
                    chapter_num=chunk.chapter_num,
                    chapter_title=chunk.chapter_title,
                    section_title=chunk.section_title,
                    chunk_text=chunk.text,
                    chunk_index=chunk.chunk_index,
                    token_count=chunk.token_count,
                )

                db.add(db_chunk)

            await db.commit()

        total_chunks += len(chunks)
        logger.info(f"Uploaded {len(chunks)} chunks for {chapter['title']}")

    logger.info(f"\n=== Ingestion Complete ===")
    logger.info(f"Total chapters: {len(chapters)}")
    logger.info(f"Total chunks: {total_chunks}")
    logger.info(f"Book ID: {book_id}")


if __name__ == "__main__":
    # Get docs path (default to ../docs relative to project root)
    if len(sys.argv) > 1:
        docs_path = sys.argv[1]
    else:
        # Default path
        project_root = Path(__file__).parent.parent.parent
        docs_path = project_root / "docs"

    if not Path(docs_path).exists():
        logger.error(f"Docs path not found: {docs_path}")
        sys.exit(1)

    logger.info(f"Using docs path: {docs_path}")

    # Run ingestion
    asyncio.run(ingest_book(str(docs_path)))
