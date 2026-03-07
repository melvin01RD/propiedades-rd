from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password, verify_password, create_access_token
from src.persistence.repositories.user_repository import user_repository
from src.api.schemas.auth import RegisterRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: RegisterRequest) -> TokenResponse:
        existing = await user_repository.get_by_email(self.db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user = await user_repository.create(
            self.db,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role,
        )

        access_token = create_access_token(str(user.id))
        return TokenResponse(access_token=access_token)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await user_repository.get_by_email(self.db, data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disabled"
            )

        access_token = create_access_token(str(user.id))
        return TokenResponse(access_token=access_token)
