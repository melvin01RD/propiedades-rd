from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.services.auth_service import AuthService
from src.api.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserResponse
from src.persistence.models.user import User

_REFRESH_COOKIE = "refresh_token"
_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 días en segundos


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=True,         # Solo HTTPS en producción
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/auth",        # Cookie solo disponible en /auth/*
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=_REFRESH_COOKIE, path="/auth")


async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    service = AuthService(db)
    return await service.register(data)


async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    token_response, refresh_token = await service.login(data)
    _set_refresh_cookie(response, refresh_token)
    return token_response


async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Lee el refresh token desde cookie HttpOnly.
    También acepta body como fallback para clientes que no soporten cookies.
    """
    refresh_token = request.cookies.get(_REFRESH_COOKIE)

    if not refresh_token:
        # Fallback: leer desde body si el cliente no envía cookie
        try:
            body = await request.json()
            refresh_token = body.get("refresh_token", "")
        except Exception:
            refresh_token = ""

    service = AuthService(db)
    token_response, new_refresh_token = await service.refresh(
        RefreshRequest(refresh_token=refresh_token or "")
    )
    _set_refresh_cookie(response, new_refresh_token)
    return token_response


async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    refresh_token = request.cookies.get(_REFRESH_COOKIE, "")
    service = AuthService(db)
    await service.logout(refresh_token)
    _clear_refresh_cookie(response)
    return {"message": "Sesión cerrada correctamente"}


async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
    )
