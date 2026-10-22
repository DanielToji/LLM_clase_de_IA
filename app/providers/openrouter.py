# app/providers/openrouter.py
import httpx

from app.core.config import Settings
from app.providers.base import (
    LLMMessage,
    LLMProvider,
    LLMProviderError,
    LLMResult,
)


class OpenRouterProvider(LLMProvider):
    name = "openrouter"

    def __init__(
        self,
        settings: Settings,
        client: httpx.AsyncClient,
    ) -> None:
        self._settings = settings
        self._client = client

    def _headers(self) -> dict[str, str]:
        if not self._settings.openrouter_api_key:
            raise LLMProviderError("missing_api_key")

        return {
            "Authorization": f"Bearer {self._settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self._settings.openrouter_app_url,
            "X-Title": self._settings.openrouter_app_title,
        }

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
        temperature: float = 0.3,
        top_p: float = 1.0,
        max_tokens: int = 300,
    ) -> LLMResult:
        payload = {
            "model": model or self._settings.openrouter_model,
            "messages": [
                {"role": m.role, "content": m.content} for m in messages
            ],
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }

        try:
            response = await self._client.post(
                "/chat/completions",
                json=payload,
                headers=self._headers(),
            )
        except httpx.TimeoutException as exc:
            raise LLMProviderError("timeout") from exc
        except httpx.HTTPError as exc:
            raise LLMProviderError("transport_error") from exc

        if response.status_code >= 400:
            # No se propaga el cuerpo del proveedor al cliente.
            raise LLMProviderError(f"provider_status_{response.status_code}")

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError("malformed_response") from exc

        if not isinstance(content, str) or not content.strip():
            raise LLMProviderError("empty_content")

        usage = data.get("usage") or {}

        return LLMResult(
            content=content,
            model=data.get("model") or payload["model"],
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
        )