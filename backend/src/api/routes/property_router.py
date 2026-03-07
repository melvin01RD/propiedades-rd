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
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.persistence.models.user import User, UserRole
from src.persistence.models.property import PropertyStatus
from src.persistence.repositories.property_repository import (
    property_repository, PropertyFilter
)
from src.api.schemas.property_schemas import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyListItem,
    PropertyPageResponse,
    PropertyFilters,
)

router = APIRouter(prefix="/properties", tags=["Propiedades"])


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _get_property_or_404(property_id: uuid.UUID, db: AsyncSession):
    prop = await property_repository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Propiedad no encontrada",
        )
    return prop


def _assert_owner(prop, current_user: User):
    """Verifica que el usuario sea dueño de la propiedad o admin."""
    if current_user.role == UserRole.admin:
        return
    if current_user.role == UserRole.agent:
        if not hasattr(current_user, "agent") or prop.agent_id != current_user.agent.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso")
    elif current_user.role == UserRole.owner:
        if not hasattr(current_user, "owner") or prop.owner_id != current_user.owner.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso")


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
    repo_filter = PropertyFilter(
        operation_type=filters.operation_type,
        property_type=filters.property_type,
        price_min=float(filters.price_min) if filters.price_min else None,
        price_max=float(filters.price_max) if filters.price_max else None,
        province_id=filters.province_id,
        sector_id=filters.sector_id,
        bedrooms_min=filters.bedrooms_min,
        bathrooms_min=filters.bathrooms_min,
        parking_spots_min=filters.parking_spots_min,
        area_min=float(filters.area_min) if filters.area_min else None,
        area_max=float(filters.area_max) if filters.area_max else None,
        amenity_slugs=filters.amenity_slugs,
        is_featured=filters.is_featured,
        page=filters.page,
        limit=filters.limit,
        order_by=filters.order_by,
    )

    page = await property_repository.get_all(db, repo_filter)

    return PropertyPageResponse(
        items=[PropertyListItem.from_property(p) for p in page.items],
        total=page.total,
        page=page.page,
        limit=page.limit,
        pages=page.pages,
        has_next=page.has_next,
        has_prev=page.has_prev,
    )


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
    if current_user.role == UserRole.agent:
        if not hasattr(current_user, "agent"):
            return []
        props = await property_repository.get_by_agent(db, current_user.agent.id)
    elif current_user.role == UserRole.owner:
        if not hasattr(current_user, "owner"):
            return []
        props = await property_repository.get_by_owner(db, current_user.owner.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo agentes y propietarios pueden ver sus propiedades",
        )

    return [PropertyListItem.from_property(p) for p in props]


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
    return await _get_property_or_404(property_id, db)


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
    if current_user.role not in (UserRole.agent, UserRole.owner, UserRole.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin acceso")

    payload = data.model_dump()

    # Asignar publicador según el rol
    if current_user.role == UserRole.agent:
        if not hasattr(current_user, "agent"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario no tiene perfil de agente",
            )
        payload["agent_id"] = current_user.agent.id
    elif current_user.role == UserRole.owner:
        if not hasattr(current_user, "owner"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario no tiene perfil de propietario",
            )
        payload["owner_id"] = current_user.owner.id

    async with db.begin():
        prop = await property_repository.create(db, payload)

    return await _get_property_or_404(prop.id, db)


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
    prop = await _get_property_or_404(property_id, db)
    _assert_owner(prop, current_user)

    # Solo enviar campos que el usuario realmente mandó
    payload = data.model_dump(exclude_unset=True)

    async with db.begin():
        updated = await property_repository.update(db, property_id, payload)

    return await _get_property_or_404(updated.id, db)


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
    prop = await _get_property_or_404(property_id, db)
    _assert_owner(prop, current_user)

    async with db.begin():
        await property_repository.soft_delete(db, property_id)
