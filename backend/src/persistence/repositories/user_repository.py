import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.persistence.models.user import User


class UserRepository:

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, email: str, password_hash: str, role: str) -> User:
        user = User(email=email, password_hash=password_hash, role=role)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user


user_repository = UserRepository()
