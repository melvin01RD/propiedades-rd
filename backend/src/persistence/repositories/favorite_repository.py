import uuid
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.persistence.models.favorite import Favorite
from src.persistence.models.property import Property


class FavoriteRepository:

    async def exists(
        self, db: AsyncSession, user_id: uuid.UUID, property_id: uuid.UUID
    ) -> bool:
        result = await db.execute(
            select(Favorite).where(
                and_(
                    Favorite.user_id == user_id,
                    Favorite.property_id == property_id,
                )
            )
        )
        return result.scalar_one_or_none() is not None

    async def add(
        self, db: AsyncSession, user_id: uuid.UUID, property_id: uuid.UUID
    ) -> Favorite:
        favorite = Favorite(user_id=user_id, property_id=property_id)
        db.add(favorite)
        await db.flush()
        return favorite

    async def remove(
        self, db: AsyncSession, user_id: uuid.UUID, property_id: uuid.UUID
    ) -> bool:
        result = await db.execute(
            select(Favorite).where(
                and_(
                    Favorite.user_id == user_id,
                    Favorite.property_id == property_id,
                )
            )
        )
        favorite = result.scalar_one_or_none()
        if not favorite:
            return False
        await db.delete(favorite)
        await db.flush()
        return True

    async def get_by_user(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[Favorite]:
        result = await db.execute(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .options(
                selectinload(Favorite.property).selectinload(Property.province),
                selectinload(Favorite.property).selectinload(Property.sector),
                selectinload(Favorite.property).selectinload(Property.images),
                selectinload(Favorite.property).selectinload(Property.amenities),
            )
            .order_by(Favorite.created_at.desc())
        )
        return list(result.scalars().all())


favorite_repository = FavoriteRepository()
