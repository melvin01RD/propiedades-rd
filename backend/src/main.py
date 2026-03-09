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
from src.api.routes.property_router import router as property_router
from src.api.routes.favorite_router import router as favorite_router
from src.api.routes.alert_router import router as alert_router
from src.api.routes.profile_router import agents_router, owners_router
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
        title="Propiedades RD API",
        description="API REST para plataforma inmobiliaria de República Dominicana",
        version="0.2.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "Autenticación",
                "description": "Registro, login y perfil del usuario",
            },
            {
                "name": "Catálogos",
                "description": "Provincias, sectores y amenidades de RD",
            },
            {
                "name": "Propiedades",
                "description": "Gestión completa de propiedades inmobiliarias",
            },
            {
                "name": "Favoritos",
                "description": "Gestión de propiedades guardadas por el usuario",
            },
            {
                "name": "Alertas",
                "description": "Alertas de búsqueda personalizadas por filtros",
            },
            {
                "name": "Estado del servidor",
                "description": "Monitoreo y salud de la API",
            },
        ],
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
    app.include_router(property_router)
    app.include_router(favorite_router)
    app.include_router(alert_router)
    app.include_router(agents_router)
    app.include_router(owners_router)

    @app.get("/", tags=["Estado del servidor"])
    async def root():
        return {
            "api": "propiedades-rd API",
            "version": "0.1.0",
            "description": "Plataforma inmobiliaria para República Dominicana",
            "links": {
                "docs":   "/docs",
                "redoc":  "/redoc",
                "health": "/health",
            },
        }

    @app.get("/health", tags=["Estado del servidor"])
    async def health_check():
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
