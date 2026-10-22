# app/core/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Proveedor activo: "openrouter" | "bootstrap"
    llm_provider: str = "openrouter"

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_allowed_models: tuple[str, ...] = (
        "openai/gpt-4o-mini",
        "meta-llama/llama-3.3-70b-instruct",
    )
    openrouter_timeout: float = 30.0
    openrouter_app_url: str = "http://localhost:8000"
    openrouter_app_title: str = "ai-knowledge-assistant"


@lru_cache
def get_settings() -> Settings:
    return Settings()