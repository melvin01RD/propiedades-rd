import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import get_settings
from src.core.database import engine
from src.api.routes.auth_router import router as auth_router
from src.api.routes.catalog_router import router as catalog_router
from src.api.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

settings = get_settings()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(lambda c: None)
    yield
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

    # Middlewares (orden importa — el último agregado es el primero en ejecutarse)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Routers
    app.include_router(auth_router)
    app.include_router(catalog_router)

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
