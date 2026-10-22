# app/api/deps.py
from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.providers.base import LLMProvider
from app.providers.openrouter import OpenRouterProvider
from app.services.assistant_service import AssistantService



def get_provider(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> LLMProvider:
    if settings.llm_provider == "bootstrap":
        return _BootstrapAdapter()
    return OpenRouterProvider(settings, request.app.state.http_client)


def get_assistant_service(
    provider: LLMProvider = Depends(get_provider),
) -> AssistantService:
    return AssistantService(provider)