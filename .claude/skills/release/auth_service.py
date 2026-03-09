import uuid
from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.persistence.repositories.user_repository import user_repository
from src.api.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest

# Blacklist en memoria. Almacena JTIs (jwt IDs) o tokens completos revocados.
# Compatible para migrar a Redis sin cambiar la interfaz pública del servicio.
_blacklist: set[str] = set()


def _blacklist_token(token: str) -> None:
    _blacklist.add(token)


def _is_blacklisted(token: str) -> bool:
    return token in _blacklist


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> TokenResponse:
        existing = await user_repository.get_by_email(self.db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = await user_repository.create(
            self.db,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
        )

        access_token = create_access_token(str(user.id))
        return TokenResponse(access_token=access_token)

    async def login(self, data: LoginRequest) -> tuple[TokenResponse, str]:
        """
        Retorna (TokenResponse, refresh_token).
        El caller (controller) es responsable de setear la cookie HttpOnly.
        """
        user = await user_repository.get_by_email(self.db, data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disabled",
            )

        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        return TokenResponse(access_token=access_token), refresh_token

    async def refresh(self, data: RefreshRequest) -> TokenResponse:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

        if _is_blacklisted(data.refresh_token):
            raise credentials_exception

        try:
            payload = decode_token(data.refresh_token)
            if payload.get("type") != "refresh":
                raise credentials_exception
            user_id: str = payload.get("sub")
            if not user_id:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = await user_repository.get_by_id(self.db, uuid.UUID(user_id))
        if not user or not user.is_active:
            raise credentials_exception

        # Rotación: invalida el refresh token usado, emite uno nuevo
        _blacklist_token(data.refresh_token)
        new_access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))
        return TokenResponse(access_token=new_access_token), new_refresh_token

    async def logout(self, refresh_token: str) -> None:
        """
        Invalida el refresh token. El access token expira solo (15 min).
        """
        if refresh_token and not _is_blacklisted(refresh_token):
            _blacklist_token(refresh_token)
