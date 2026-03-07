import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.property import PropertyStatus
from src.persistence.repositories.favorite_repository import favorite_repository
from src.persistence.repositories.property_repository import property_repository
from src.api.schemas.property_schemas import PropertyListItem


class FavoriteService:

    async def add(
        self, db: AsyncSession, user_id: uuid.UUID, property_id: uuid.UUID
    ):
        # Verificar que la propiedad existe y está activa
        prop = await property_repository.get_by_id(db, property_id)
        if not prop or prop.status != PropertyStatus.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propiedad no encontrada",
            )

        # Verificar que no está ya en favoritos
        if await favorite_repository.exists(db, user_id, property_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La propiedad ya está en tus favoritos",
            )

        return await favorite_repository.add(db, user_id, property_id)

    async def remove(
        self, db: AsyncSession, user_id: uuid.UUID, property_id: uuid.UUID
    ) -> None:
        removed = await favorite_repository.remove(db, user_id, property_id)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La propiedad no está en tus favoritos",
            )

    async def get_my_favorites(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> list[PropertyListItem]:
        favorites = await favorite_repository.get_by_user(db, user_id)
        return [PropertyListItem.from_property(f.property) for f in favorites]


favorite_service = FavoriteService()
