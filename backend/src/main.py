from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.core.config import get_settings
from src.core.database import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verificar conexión a DB
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: None)
    yield
    # Shutdown: cerrar conexión
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="propiedades-rd API",
        description="Plataforma inmobiliaria para República Dominicana",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
