# tests/unit/test_failures.py
import pytest
from fastapi import HTTPException

from app.api.routes.chat import chat
from app.providers.base import LLMProviderError
from app.schemas.chat import ChatRequest
from tests.fakes import FakeLLMProvider
from app.services.assistant_service import AssistantService


@pytest.mark.parametrize("scenario", ["timeout", "429", "no_choices"])
@pytest.mark.asyncio
async def test_provider_failures_map_to_502(scenario):
    service = AssistantService(FakeLLMProvider(scenario))

    with pytest.raises(HTTPException) as exc:
        await chat(ChatRequest(question="¿Qué es FastAPI?"), service)

    assert exc.value.status_code == 502
    assert "sk-or" not in str(exc.value.detail)