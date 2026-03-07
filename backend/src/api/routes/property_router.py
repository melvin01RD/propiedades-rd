"""
CRUD de propiedades.

Endpoints:
    GET    /properties              → listado con filtros y paginación
    POST   /properties              → crear propiedad
    GET    /properties/{id}         → detalle
    PUT    /properties/{id}         → actualizar
    DELETE /properties/{id}         → soft delete (status → inactive)
    GET    /properties/me           → mis propiedades (agente u owner autenticado)
"""

import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.persistence.models.user import User, UserRole
from src.services.property_service import property_service
from src.api.schemas.property_schemas import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyListItem,
    PropertyPageResponse,
    PropertyFilters,
)

router = APIRouter(prefix="/properties", tags=["Propiedades"])


# ── GET /properties ────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=PropertyPageResponse,
    summary="Listado de propiedades con filtros",
)
async def list_properties(
    filters: PropertyFilters = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await property_service.get_all(db, filters)


# ── GET /properties/me ────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=list[PropertyListItem],
    summary="Mis propiedades",
)
async def my_properties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await property_service.get_my_properties(db, current_user)


# ── GET /properties/{id} ───────────────────────────────────────────────────────

@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Detalle de una propiedad",
)
async def get_property(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await property_service.get_by_id(db, property_id)


# ── POST /properties ───────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear propiedad",
)
async def create_property(
    data: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await property_service.create(db, data, current_user)


# ── PUT /properties/{id} ───────────────────────────────────────────────────────

@router.put(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Actualizar propiedad",
)
async def update_property(
    property_id: uuid.UUID,
    data: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await property_service.update(db, property_id, data, current_user)


# ── DELETE /properties/{id} ────────────────────────────────────────────────────

@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar propiedad (soft delete)",
)
async def delete_property(
    property_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await property_service.delete(db, property_id, current_user)
