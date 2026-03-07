"""
Fixtures de integración.

Estrategia de aislamiento: cada test abre una transacción en la conexión,
sobreescribe get_db para que todos los requests del test usen esa misma
sesión, y al finalizar hace rollback. La DB queda limpia sin DELETE manual.
"""

import uuid
import pytest_asyncio
import httpx
from unittest.mock import patch
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from src.core.config import get_settings
from src.core.dependencies import get_db

settings = get_settings()

# Engine sin pool — ideal para tests (evita conexiones colgadas entre tests)
test_engine = create_async_engine(settings.database_url, poolclass=NullPool)


class _NoRateLimitMiddleware(BaseHTTPMiddleware):
    """Reemplaza RateLimitMiddleware para que no interfiera con los tests."""
    async def dispatch(self, request, call_next):
        return await call_next(request)


@pytest_asyncio.fixture
async def db_session():
    """
    Sesión de DB con rollback automático.
    Abre una transacción a nivel de conexión y la revierte al terminar
    el test, sin importar si pasó o falló.
    """
    async with test_engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()


@pytest_asyncio.fixture
async def async_client(db_session):
    """
    HTTP client con la app completa levantada en ASGI.
    - get_db sobreescrito: todos los requests usan db_session (sin commit)
    - RateLimitMiddleware deshabilitado para evitar falsos 429 en tests
    """
    from src.main import create_app

    async def _override_get_db():
        yield db_session  # sin commit — el rollback lo controla db_session

    with patch("src.main.RateLimitMiddleware", _NoRateLimitMiddleware):
        app = create_app()

    app.dependency_overrides[get_db] = _override_get_db

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


@pytest_asyncio.fixture
async def auth_headers(async_client):
    """
    Registra un usuario de prueba con email único y retorna los headers
    de Authorization listos para usar en requests protegidos.
    """
    unique_email = f"integration_{uuid.uuid4().hex[:8]}@test.com"
    resp = await async_client.post("/auth/register", json={
        "email": unique_email,
        "password": "Integration123!",
        "role": "owner",
    })
    assert resp.status_code == 200, f"auth_headers setup failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
