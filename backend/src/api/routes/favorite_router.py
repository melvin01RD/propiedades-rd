"""
Favoritos.

Endpoints:
    POST   /favorites/{property_id}      → agregar a favoritos
    DELETE /favorites/{property_id}      → quitar de favoritos
    GET    /favorites                    → mis favoritos
"""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.persistence.models.user import User
from src.services.favorite_service import favorite_service
from src.api.schemas.property_schemas import PropertyListItem

router = APIRouter(prefix="/favorites", tags=["Favoritos"])


@router.post(
    "/{property_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Agregar propiedad a favoritos",
)
async def add_favorite(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await favorite_service.add(db, current_user.id, property_id)
    return {"detail": "Propiedad agregada a favoritos"}


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar propiedad de favoritos",
)
async def remove_favorite(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await favorite_service.remove(db, current_user.id, property_id)


@router.get(
    "",
    response_model=list[PropertyListItem],
    summary="Mis propiedades favoritas",
)
async def get_my_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await favorite_service.get_my_favorites(db, current_user.id)
