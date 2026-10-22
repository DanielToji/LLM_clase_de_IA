# app/services/assistant_service.py
import time

from app.providers.base import LLMMessage, LLMProvider
from app.schemas.chat import ChatRequest, ChatResponse, Usage


class AssistantService:
    """Lógica de aplicación: mensajes, orquestación, contrato de salida."""

    SYSTEM_PROMPT = (
        "Eres un asistente técnico para aprendices de ingeniería de "
        "sistemas. Responde en español, con precisión técnica y ejemplos "
        "concretos. Si no sabes algo o la fuente no es verificable, dilo "
        "explícitamente y NO inventes referencias, DOIs ni publicaciones."
    )

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    async def answer(self, payload: ChatRequest) -> ChatResponse:
        started = time.perf_counter()

        result = await self._provider.generate(
            [
                LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                LLMMessage(role="user", content=payload.question),
            ],
            model=payload.model,
            temperature=payload.temperature,
            top_p=payload.top_p,
            max_tokens=payload.max_tokens,
        )

        return ChatResponse(
            answer=result.content,
            provider=self._provider.name,
            model=result.model,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
            usage=Usage(
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.total_tokens,
            ),
        )