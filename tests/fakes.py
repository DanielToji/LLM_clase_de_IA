# tests/fakes.py
import httpx

from app.providers.base import LLMMessage, LLMProvider, LLMProviderError, LLMResult


class FakeLLMProvider(LLMProvider):
    """Permite simular éxito, timeout, 429 y JSON sin choices."""

    name = "fake"

    def __init__(self, scenario: str = "ok") -> None:
        self.scenario = scenario
        self.calls = 0

    async def generate(self, messages, **kwargs) -> LLMResult:
        self.calls += 1
        if self.scenario == "timeout":
            raise LLMProviderError("timeout")
        if self.scenario == "429":
            raise LLMProviderError("provider_status_429")
        if self.scenario == "no_choices":
            raise LLMProviderError("malformed_response")
        return LLMResult(content="respuesta simulada", model="fake-1")