import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.persistence.models.owner import Owner


class OwnerRepository:

    async def get_by_user_id(self, db: AsyncSession, user_id: uuid.UUID) -> Owner | None:
        result = await db.execute(
            select(Owner)
            .options(selectinload(Owner.user))
            .where(Owner.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, user_id: uuid.UUID, first_name: str, last_name: str, **kwargs) -> Owner:
        owner = Owner(user_id=user_id, first_name=first_name, last_name=last_name, **kwargs)
        db.add(owner)
        await db.flush()
        await db.refresh(owner)
        return owner

    async def update(self, db: AsyncSession, owner: Owner, **kwargs) -> Owner:
        for field, value in kwargs.items():
            if hasattr(owner, field) and value is not None:
                setattr(owner, field, value)
        await db.flush()
        await db.refresh(owner)
        return owner


owner_repository = OwnerRepository()
