"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str
    model_name: str = "gpt-4-turbo-preview"
    max_response_tokens: int = 500
    temperature: float = 0.3

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    vector_dimension: int = 1536
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7

    # Neon Postgres Configuration
    database_url: str

    # Application Configuration
    environment: str = "development"
    api_rate_limit_per_minute: int = 20
    api_rate_limit_per_user: int = 10
    allowed_origins: str = "http://localhost:3000"

    # Chunking Configuration
    chunk_size: int = 600
    chunk_overlap: int = 100

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
