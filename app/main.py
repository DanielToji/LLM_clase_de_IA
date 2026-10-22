# app/main.py
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.http_client = httpx.AsyncClient(
        base_url=settings.openrouter_base_url,
        timeout=settings.openrouter_timeout,
    )
    yield
    await app.state.http_client.aclose()


app = FastAPI(
    title="AI Knowledge Assistant",
    description="API evolutiva para el curso de Ingeniería de Sistemas de IA.",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(chat_router)