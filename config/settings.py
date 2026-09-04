import os
from typing import Literal, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, computed_field, model_validator

# Always force load .env into environment
load_dotenv(dotenv_path=".env", override=True)


class Settings(BaseSettings):
    """
    Application Settings for Nykaa Fashion AI Wishlist Discovery Engine.
    All runtime model names, strategies, depths, and scoring weights must be loaded from environment variables.
    Hardcoded model names in code are strictly prohibited by architecture guidelines.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server & Environment Settings
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Groq LLM Inference
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: Optional[str] = Field(default=None, alias="GROQ_MODEL")

    # Embeddings & Vector Store
    embedding_model: Optional[str] = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    vector_db_url: Optional[str] = Field(default="sqlite:///./data/discovery_engine.db", alias="VECTOR_DB_URL")

    # Retrieval Strategy
    retrieval_strategy: Literal["vector", "hybrid"] = Field(default="hybrid", alias="RETRIEVAL_STRATEGY")
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")

    # Chunking
    chunk_size: int = Field(default=400, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")

    # Research Prioritisation Scoring Weights (Must sum to 1.0)
    weight_frequency: float = Field(default=0.20, alias="WEIGHT_FREQUENCY")
    weight_metric_relevance: float = Field(default=0.25, alias="WEIGHT_METRIC_RELEVANCE")
    weight_pain: float = Field(default=0.20, alias="WEIGHT_PAIN")
    weight_evidence: float = Field(default=0.15, alias="WEIGHT_EVIDENCE")
    weight_cross_source: float = Field(default=0.10, alias="WEIGHT_CROSS_SOURCE")
    weight_solvability: float = Field(default=0.10, alias="WEIGHT_SOLVABILITY")

    @computed_field
    @property
    def is_groq_configured(self) -> bool:
        """Returns True if Groq API key is present and non-empty."""
        return bool(self.groq_api_key and self.groq_api_key.strip())

    def get_stack_transparency(self) -> dict:
        """Returns live runtime configuration for PM Chrome Stack Transparency panel."""
        return {
            "embedding_model": self.embedding_model or "Not configured",
            "retrieval_strategy": self.retrieval_strategy,
            "retrieval_top_k": self.retrieval_top_k,
            "groq_model": self.groq_model or "Not configured",
            "is_groq_configured": self.is_groq_configured,
            "vector_db_url": self.vector_db_url or "Not configured",
        }


# Global Singleton Instance
settings = Settings()
