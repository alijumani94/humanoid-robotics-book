"""Agent service for generating responses using OpenAI."""

from openai import AsyncOpenAI
from app.config import settings
from app.services.retrieval_service import ChunkResult
from typing import List
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)

# System prompt template
SYSTEM_PROMPT = """You are a helpful assistant for a robotics and humanoid robotics textbook.

STRICT RULES:
1. Answer ONLY using the provided context from the book
2. If the context doesn't contain the answer, you MUST respond EXACTLY with: "This question cannot be answered from the book's content."
3. Never use external knowledge or information not in the context
4. Keep answers concise (maximum 300 words)
5. Always cite the chapter/section when possible
6. Be precise and factual

Format your responses like:
"According to [Chapter Title], [answer with relevant details]"

If you cannot answer based on the provided context, you MUST say:
"This question cannot be answered from the book's content."

Do not make up information. Do not guess. Do not use knowledge outside the provided context."""

USER_PROMPT_TEMPLATE = """CONTEXT FROM THE BOOK:
{context}

USER QUESTION:
{question}

Please answer the question using ONLY the context provided above. If the context doesn't contain the answer, respond with: "This question cannot be answered from the book's content." """


async def generate_response(
    question: str,
    chunks: List[ChunkResult],
) -> str:
    """
    Generate a response using OpenAI agent with retrieved context.

    Args:
        question: User's question
        chunks: Retrieved chunks to use as context

    Returns:
        Generated response text
    """
    if not chunks:
        return "This question cannot be answered from the book's content."

    try:
        # Format context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            chapter_info = chunk.chapter_title
            if chunk.section_title:
                chapter_info += f" - {chunk.section_title}"

            context_parts.append(f"[Source {i}] {chapter_info}:\n{chunk.text}")

        context = "\n\n".join(context_parts)

        # Create user prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )

        # Call OpenAI
        response = await client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_response_tokens,
        )

        answer = response.choices[0].message.content.strip()

        logger.info(f"Generated response for question: {question[:50]}...")
        return answer

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise


async def check_openai_health() -> bool:
    """
    Check if OpenAI API is accessible.

    Returns:
        bool: True if healthy
    """
    try:
        # Simple test call
        await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5,
        )
        return True
    except Exception as e:
        logger.error(f"OpenAI health check failed: {e}")
        return False
