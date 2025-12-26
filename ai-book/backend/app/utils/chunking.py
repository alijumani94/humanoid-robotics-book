"""Text chunking utilities for preparing book content."""

from typing import List, Dict
from app.config import settings
from app.utils.embeddings import count_tokens
import re


class TextChunk:
    """Represents a chunk of text with metadata."""

    def __init__(
        self,
        text: str,
        chapter_num: int,
        chapter_title: str,
        section_title: str = None,
        chunk_index: int = 0,
    ):
        self.text = text
        self.chapter_num = chapter_num
        self.chapter_title = chapter_title
        self.section_title = section_title
        self.chunk_index = chunk_index
        self.token_count = count_tokens(text)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "chapter_num": self.chapter_num,
            "chapter_title": self.chapter_title,
            "section_title": self.section_title,
            "chunk_index": self.chunk_index,
            "token_count": self.token_count,
        }


def chunk_text(
    text: str,
    chapter_num: int,
    chapter_title: str,
    section_title: str = None,
    chunk_size: int = None,
    overlap: int = None,
) -> List[TextChunk]:
    """
    Chunk text into smaller segments with overlap.

    Args:
        text: Text to chunk
        chapter_num: Chapter number
        chapter_title: Chapter title
        section_title: Section title (optional)
        chunk_size: Maximum tokens per chunk (defaults to config)
        overlap: Token overlap between chunks (defaults to config)

    Returns:
        List of TextChunk objects
    """
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_index = 0

    for paragraph in paragraphs:
        para_tokens = count_tokens(paragraph)

        # If single paragraph exceeds chunk size, split it
        if para_tokens > chunk_size:
            if current_chunk:
                # Save current chunk
                chunk_text_str = '\n\n'.join(current_chunk)
                chunks.append(
                    TextChunk(
                        text=chunk_text_str,
                        chapter_num=chapter_num,
                        chapter_title=chapter_title,
                        section_title=section_title,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
                current_chunk = []
                current_tokens = 0

            # Split large paragraph by sentences
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                sent_tokens = count_tokens(sentence)

                if current_tokens + sent_tokens > chunk_size and current_chunk:
                    chunk_text_str = ' '.join(current_chunk)
                    chunks.append(
                        TextChunk(
                            text=chunk_text_str,
                            chapter_num=chapter_num,
                            chapter_title=chapter_title,
                            section_title=section_title,
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1

                    # Keep overlap
                    overlap_text = current_chunk[-1] if current_chunk else ""
                    current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                    current_tokens = count_tokens(' '.join(current_chunk))
                else:
                    current_chunk.append(sentence)
                    current_tokens += sent_tokens

        # Normal paragraph processing
        elif current_tokens + para_tokens > chunk_size:
            # Save current chunk
            if current_chunk:
                chunk_text_str = '\n\n'.join(current_chunk)
                chunks.append(
                    TextChunk(
                        text=chunk_text_str,
                        chapter_num=chapter_num,
                        chapter_title=chapter_title,
                        section_title=section_title,
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1

            # Start new chunk with overlap
            if overlap > 0 and current_chunk:
                overlap_text = current_chunk[-1]
                current_chunk = [overlap_text, paragraph]
                current_tokens = count_tokens('\n\n'.join(current_chunk))
            else:
                current_chunk = [paragraph]
                current_tokens = para_tokens
        else:
            current_chunk.append(paragraph)
            current_tokens += para_tokens

    # Add final chunk
    if current_chunk:
        chunk_text_str = '\n\n'.join(current_chunk)
        chunks.append(
            TextChunk(
                text=chunk_text_str,
                chapter_num=chapter_num,
                chapter_title=chapter_title,
                section_title=section_title,
                chunk_index=chunk_index,
            )
        )

    return chunks


def add_context_to_chunk(chunk: TextChunk) -> str:
    """
    Add contextual headers to chunk text for better retrieval.

    Args:
        chunk: TextChunk object

    Returns:
        Enhanced chunk text with context
    """
    context_parts = [chunk.chapter_title]

    if chunk.section_title:
        context_parts.append(chunk.section_title)

    header = " - ".join(context_parts)
    return f"{header}\n\n{chunk.text}"
