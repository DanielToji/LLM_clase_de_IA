# app/api/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_assistant_service
from app.providers.base import LLMProviderError
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.assistant_service import AssistantService


router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    responses={502: {"description": "Fallo controlado del proveedor LLM"}},
)
async def chat(
    payload: ChatRequest,
    service: AssistantService = Depends(get_assistant_service),
) -> ChatResponse:
    try:
        return await service.answer(payload)
    except LLMProviderError as exc:
        # Se registra el motivo, se devuelve un mensaje genérico.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="El proveedor del modelo no está disponible.",
        ) from exc