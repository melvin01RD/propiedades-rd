import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from src.services.auth_service import AuthService
from src.api.schemas.auth import RegisterRequest, LoginRequest
from src.persistence.models.user import UserRole


# ── Helpers ───────────────────────────────────────────────────────

def make_register_data(email="nuevo@example.com", password="Secure123!", role=UserRole.owner):
    return RegisterRequest(email=email, password=password, role=role)


def make_login_data(email="test@example.com", password="Breathofthewild2024@@"):
    return LoginRequest(email=email, password=password)


# ── Tests: register ───────────────────────────────────────────────

class TestRegister:

    @pytest.mark.asyncio
    async def test_register_happy_path(self, mock_db, mock_user):
        """Usuario nuevo se registra correctamente y recibe token."""
        with patch("src.services.auth_service.user_repository") as mock_repo, \
             patch("src.services.auth_service.hash_password", return_value="hashed"), \
             patch("src.services.auth_service.create_access_token", return_value="token123"):

            mock_repo.get_by_email = AsyncMock(return_value=None)
            mock_repo.create = AsyncMock(return_value=mock_user)

            service = AuthService(mock_db)
            result = await service.register(make_register_data())

            assert result.access_token == "token123"
            assert result.token_type == "bearer"
            mock_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises_400(self, mock_db, mock_user):
        """Email ya registrado lanza HTTP 400."""
        with patch("src.services.auth_service.user_repository") as mock_repo:
            mock_repo.get_by_email = AsyncMock(return_value=mock_user)

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc:
                await service.register(make_register_data(email="test@example.com"))

            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_register_admin_role_blocked_by_schema(self):
        """El schema bloquea role=admin antes de llegar al service."""
        with pytest.raises(Exception):
            RegisterRequest(email="x@x.com", password="Secure123!", role="admin")


# ── Tests: login ──────────────────────────────────────────────────

class TestLogin:

    @pytest.mark.asyncio
    async def test_login_happy_path(self, mock_db, mock_user):
        """Credenciales correctas retornan token."""
        with patch("src.services.auth_service.user_repository") as mock_repo, \
             patch("src.services.auth_service.verify_password", return_value=True), \
             patch("src.services.auth_service.create_access_token", return_value="token123"):

            mock_repo.get_by_email = AsyncMock(return_value=mock_user)

            service = AuthService(mock_db)
            result = await service.login(make_login_data())

            assert result.access_token == "token123"

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises_401(self, mock_db, mock_user):
        """Password incorrecto lanza HTTP 401."""
        with patch("src.services.auth_service.user_repository") as mock_repo, \
             patch("src.services.auth_service.verify_password", return_value=False):

            mock_repo.get_by_email = AsyncMock(return_value=mock_user)

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc:
                await service.login(make_login_data(password="wrong"))

            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_user_not_found_raises_401(self, mock_db):
        """Usuario inexistente lanza HTTP 401 (no revela si existe o no)."""
        with patch("src.services.auth_service.user_repository") as mock_repo:
            mock_repo.get_by_email = AsyncMock(return_value=None)

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc:
                await service.login(make_login_data())

            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user_raises_403(self, mock_db, mock_user):
        """Usuario inactivo lanza HTTP 403 (cuenta deshabilitada)."""
        mock_user.is_active = False

        with patch("src.services.auth_service.user_repository") as mock_repo, \
             patch("src.services.auth_service.verify_password", return_value=True):

            mock_repo.get_by_email = AsyncMock(return_value=mock_user)

            service = AuthService(mock_db)
            with pytest.raises(HTTPException) as exc:
                await service.login(make_login_data())

            assert exc.value.status_code == 403
