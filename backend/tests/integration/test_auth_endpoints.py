"""
Integration tests — /auth endpoints.

Todos los tests usan la DB real (Neon) con rollback automático por fixture.
No se persiste ningún dato entre tests.
"""

import pytest


# ── Helpers ───────────────────────────────────────────────────────

def register_payload(**kwargs):
    defaults = {
        "email": "nuevo@integration.com",
        "password": "Secure123!",
        "role": "owner",
    }
    defaults.update(kwargs)
    return defaults


def login_payload(**kwargs):
    defaults = {
        "email": "nuevo@integration.com",
        "password": "Secure123!",
    }
    defaults.update(kwargs)
    return defaults


# ── POST /auth/register ───────────────────────────────────────────

class TestRegister:

    @pytest.mark.asyncio
    async def test_register_happy_path(self, async_client):
        """Registro exitoso retorna access_token con token_type bearer."""
        resp = await async_client.post("/auth/register", json=register_payload())

        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert len(body["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_register_duplicate_email_returns_400(self, async_client):
        """Registrar el mismo email dos veces retorna 400."""
        payload = register_payload(email="dup@integration.com")

        first = await async_client.post("/auth/register", json=payload)
        assert first.status_code == 200

        second = await async_client.post("/auth/register", json=payload)
        assert second.status_code == 400

    @pytest.mark.asyncio
    async def test_register_admin_role_blocked_returns_422(self, async_client):
        """El schema rechaza role=admin antes de llegar al service → 422."""
        resp = await async_client.post("/auth/register", json=register_payload(role="admin"))

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_weak_password_returns_422(self, async_client):
        """Password de menos de 8 caracteres retorna 422."""
        resp = await async_client.post("/auth/register", json=register_payload(password="short"))

        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email_returns_422(self, async_client):
        """Email inválido retorna 422."""
        resp = await async_client.post("/auth/register", json=register_payload(email="notanemail"))

        assert resp.status_code == 422


# ── POST /auth/login ──────────────────────────────────────────────

class TestLogin:

    @pytest.mark.asyncio
    async def test_login_happy_path(self, async_client):
        """Login con credenciales correctas retorna access_token."""
        email = "login_test@integration.com"
        password = "Secure123!"

        await async_client.post("/auth/register", json=register_payload(email=email, password=password))

        resp = await async_client.post("/auth/login", json=login_payload(email=email, password=password))

        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password_returns_401(self, async_client):
        """Password incorrecto retorna 401."""
        email = "wrongpass@integration.com"
        await async_client.post("/auth/register", json=register_payload(email=email))

        resp = await async_client.post("/auth/login", json=login_payload(email=email, password="WrongPass99!"))

        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user_returns_401(self, async_client):
        """Usuario inexistente retorna 401 (no revela si el email existe)."""
        resp = await async_client.post("/auth/login", json=login_payload(email="nobody@integration.com"))

        assert resp.status_code == 401


# ── GET /auth/me ──────────────────────────────────────────────────

class TestMe:

    @pytest.mark.asyncio
    async def test_me_with_valid_token_returns_user(self, async_client, auth_headers):
        """Token válido retorna datos del usuario autenticado."""
        resp = await async_client.get("/auth/me", headers=auth_headers)

        assert resp.status_code == 200
        body = resp.json()
        assert "email" in body
        assert "role" in body
        assert body["is_active"] is True
        assert body["role"] == "owner"

    @pytest.mark.asyncio
    async def test_me_without_token_returns_403(self, async_client):
        """Sin token retorna 403 (HTTPBearer requiere Authorization header)."""
        resp = await async_client.get("/auth/me")

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_me_with_invalid_token_returns_401(self, async_client):
        """Token inválido retorna 401."""
        resp = await async_client.get("/auth/me", headers={"Authorization": "Bearer tokenbasura"})

        assert resp.status_code == 401
