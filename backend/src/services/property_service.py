"""
PropertyService — lógica de negocio para propiedades.

Responsabilidades:
    - Validar que el publicador (agente/owner) tiene perfil completo
    - Asignar agent_id u owner_id según el rol del usuario autenticado
    - Verificar ownership antes de modificar
    - Delegar persistencia al PropertyRepository
"""

import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.user import User, UserRole
from src.persistence.repositories.property_repository import (
    property_repository, PropertyFilter, Page
)
from src.api.schemas.property_schemas import (
    PropertyCreate, PropertyUpdate, PropertyListItem,
    PropertyPageResponse, PropertyFilters
)


class PropertyService:

    # ── Listado y detalle ──────────────────────────────────────────────

    async def get_all(
        self, db: AsyncSession, filters: PropertyFilters
    ) -> PropertyPageResponse:
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

    async def get_by_id(self, db: AsyncSession, property_id: uuid.UUID):
        prop = await property_repository.get_by_id(db, property_id)
        if not prop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Propiedad no encontrada",
            )
        return prop

    async def get_my_properties(
        self, db: AsyncSession, current_user: User
    ) -> list[PropertyListItem]:
        if current_user.role == UserRole.agent:
            if current_user.agent is None:
                return []
            props = await property_repository.get_by_agent(db, current_user.agent.id)
        elif current_user.role == UserRole.owner:
            if current_user.owner is None:
                return []
            props = await property_repository.get_by_owner(db, current_user.owner.id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo agentes y propietarios pueden ver sus propiedades",
            )
        return [PropertyListItem.from_property(p) for p in props]

    # ── Escritura ──────────────────────────────────────────────────────

    async def create(
        self, db: AsyncSession, data: PropertyCreate, current_user: User
    ):
        payload = data.model_dump()
        payload = self._assign_publisher(payload, current_user)

        prop = await property_repository.create(db, payload)
        return await property_repository.get_by_id(db, prop.id)

    async def update(
        self,
        db: AsyncSession,
        property_id: uuid.UUID,
        data: PropertyUpdate,
        current_user: User,
    ):
        prop = await self.get_by_id(db, property_id)
        self._assert_owner(prop, current_user)

        payload = data.model_dump(exclude_unset=True)
        updated = await property_repository.update(db, property_id, payload)
        return await property_repository.get_by_id(db, updated.id)

    async def delete(
        self, db: AsyncSession, property_id: uuid.UUID, current_user: User
    ) -> None:
        prop = await self.get_by_id(db, property_id)
        self._assert_owner(prop, current_user)
        await property_repository.soft_delete(db, property_id)

    # ── Helpers privados ───────────────────────────────────────────────

    def _assign_publisher(self, payload: dict, current_user: User) -> dict:
        """Asigna agent_id u owner_id según el rol. Nunca ambos."""
        if current_user.role == UserRole.agent:
            if current_user.agent is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario no tiene perfil de agente",
                )
            payload["agent_id"] = current_user.agent.id

        elif current_user.role == UserRole.owner:
            if current_user.owner is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El usuario no tiene perfil de propietario",
                )
            payload["owner_id"] = current_user.owner.id

        elif current_user.role == UserRole.admin:
            # Admin puede crear en nombre de cualquiera
            # agent_id u owner_id deben venir explícitos en el payload
            if not payload.get("agent_id") and not payload.get("owner_id"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Admin debe especificar agent_id u owner_id al crear una propiedad",
                )
        return payload

    def _assert_owner(self, prop, current_user: User) -> None:
        """Verifica que el usuario sea dueño de la propiedad o admin."""
        if current_user.role == UserRole.admin:
            return
        if current_user.role == UserRole.agent:
            if current_user.agent is None or prop.agent_id != current_user.agent.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permiso para modificar esta propiedad",
                )
        elif current_user.role == UserRole.owner:
            if current_user.owner is None or prop.owner_id != current_user.owner.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permiso para modificar esta propiedad",
                )


# Instancia singleton
property_service = PropertyService()
