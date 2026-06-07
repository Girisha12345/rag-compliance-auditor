from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise RAG Workflow Application"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    api_prefix: str = "/api"
    data_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "data")
    reports_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "reports")
    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "policy_corpus"
    embedding_provider: Literal["local", "openai"] = "local"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    flashrank_model: str = "ms-marco-MiniLM-L-12-v2"
    max_context_tokens: int = 6000
    audit_min_input_chars: int = 100
    chunk_token_limit: int = 512


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    return settings
