"""
PropertyRepository — acceso centralizado a la tabla properties.

Métodos:
    get_all(db, filters)        → Page[Property] con filtros dinámicos
    get_by_id(db, id)           → Property | None
    create(db, data)            → Property
    update(db, id, data)        → Property | None
    soft_delete(db, id)         → bool
    get_by_agent(db, agent_id)  → list[Property]
    get_by_owner(db, owner_id)  → list[Property]
"""

import uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.persistence.models import (
    Property, PropertyStatus, PropertyType,
    OperationType, Province, Sector, Amenity
)


# ── Filtros ────────────────────────────────────────────────────────────────────

@dataclass
class PropertyFilter:
    # Tipo y operación
    operation_type: OperationType | None = None
    property_type:  PropertyType | None  = None

    # Precio
    price_min: float | None = None
    price_max: float | None = None

    # Ubicación
    province_id: int | None = None
    sector_id:   int | None = None

    # Características
    bedrooms_min:     int | None = None
    bathrooms_min:    int | None = None
    parking_spots_min: int | None = None
    area_min:         float | None = None
    area_max:         float | None = None

    # Amenidades (lista de slugs: ["piscina", "gimnasio"])
    amenity_slugs: list[str] = field(default_factory=list)

    # Estado y destacados
    status:      PropertyStatus = PropertyStatus.active
    is_featured: bool | None    = None

    # Paginación
    page:  int = 1
    limit: int = 20

    # Orden: "price_asc" | "price_desc" | "created_at_desc" | "created_at_asc"
    order_by: str = "created_at_desc"


# ── Resultado paginado ─────────────────────────────────────────────────────────

@dataclass
class Page:
    items: list[Any]
    total: int
    page:  int
    limit: int

    @property
    def pages(self) -> int:
        return max(1, (self.total + self.limit - 1) // self.limit)

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


# ── Repositorio ────────────────────────────────────────────────────────────────

class PropertyRepository:

    # Relaciones que siempre cargamos junto a la propiedad
    _EAGER = [
        selectinload(Property.province),
        selectinload(Property.sector),
        selectinload(Property.images),
        selectinload(Property.amenities),
    ]

    # ── Lectura ────────────────────────────────────────────────────────────────

    async def get_all(self, db: AsyncSession, filters: PropertyFilter) -> Page:
        """
        Retorna propiedades paginadas aplicando todos los filtros activos.
        Solo aplica condiciones cuyo valor no sea None.
        """
        conditions = self._build_conditions(filters)

        # Query de datos
        stmt = (
            select(Property)
            .where(and_(*conditions))
            .options(*self._EAGER)
            .offset((filters.page - 1) * filters.limit)
            .limit(filters.limit)
            .order_by(self._resolve_order(filters.order_by))
        )

        # Query de conteo (sin paginación ni eager loading)
        count_stmt = (
            select(func.count())
            .select_from(Property)
            .where(and_(*conditions))
        )

        # Si hay filtro por amenidades, hacemos subquery
        if filters.amenity_slugs:
            amenity_filter = self._amenity_subquery(filters.amenity_slugs)
            stmt       = stmt.where(amenity_filter)
            count_stmt = count_stmt.where(amenity_filter)

        results = await db.execute(stmt)
        total   = await db.scalar(count_stmt)

        return Page(
            items=list(results.scalars().all()),
            total=total or 0,
            page=filters.page,
            limit=filters.limit,
        )

    async def get_by_id(self, db: AsyncSession, property_id: uuid.UUID) -> Property | None:
        stmt = (
            select(Property)
            .where(Property.id == property_id)
            .options(*self._EAGER)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_agent(self, db: AsyncSession, agent_id: uuid.UUID) -> list[Property]:
        stmt = (
            select(Property)
            .where(Property.agent_id == agent_id)
            .options(*self._EAGER)
            .order_by(Property.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_owner(self, db: AsyncSession, owner_id: uuid.UUID) -> list[Property]:
        stmt = (
            select(Property)
            .where(Property.owner_id == owner_id)
            .options(*self._EAGER)
            .order_by(Property.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ── Escritura ──────────────────────────────────────────────────────────────

    async def create(self, db: AsyncSession, data: dict) -> Property:
        """
        Crea una propiedad. Si `amenity_ids` está en data, carga y asigna las amenidades.
        """
        amenity_ids: list[int] = data.pop("amenity_ids", [])

        prop = Property(**data)

        if amenity_ids:
            prop.amenities = await self._load_amenities(db, amenity_ids)

        db.add(prop)
        await db.flush()      # obtiene el ID antes del commit
        await db.refresh(prop)
        return prop

    async def update(
        self, db: AsyncSession, property_id: uuid.UUID, data: dict
    ) -> Property | None:
        prop = await self.get_by_id(db, property_id)
        if not prop:
            return None

        amenity_ids: list[int] | None = data.pop("amenity_ids", None)

        for key, value in data.items():
            setattr(prop, key, value)

        if amenity_ids is not None:
            prop.amenities = await self._load_amenities(db, amenity_ids)

        await db.flush()
        await db.refresh(prop)
        return prop

    async def soft_delete(self, db: AsyncSession, property_id: uuid.UUID) -> bool:
        """
        No elimina el registro — cambia el status a `inactive`.
        Preserva el historial y los favoritos existentes.
        """
        prop = await self.get_by_id(db, property_id)
        if not prop:
            return False

        prop.status = PropertyStatus.inactive
        await db.flush()
        return True

    # ── Helpers privados ───────────────────────────────────────────────────────

    def _build_conditions(self, filters: PropertyFilter) -> list:
        """Construye la lista de condiciones WHERE de forma dinámica."""
        c = []

        # Siempre filtramos por status
        c.append(Property.status == filters.status)

        if filters.operation_type:
            c.append(Property.operation_type == filters.operation_type)
        if filters.property_type:
            c.append(Property.property_type == filters.property_type)

        if filters.price_min is not None:
            c.append(Property.price >= filters.price_min)

        if filters.price_max is not None:
            c.append(Property.price <= filters.price_max)

        if filters.province_id is not None:
            c.append(Property.province_id == filters.province_id)

        if filters.sector_id is not None:
            c.append(Property.sector_id == filters.sector_id)

        if filters.bedrooms_min is not None:
            c.append(Property.bedrooms >= filters.bedrooms_min)

        if filters.bathrooms_min is not None:
            c.append(Property.bathrooms >= filters.bathrooms_min)

        if filters.parking_spots_min is not None:
            c.append(Property.parking_spots >= filters.parking_spots_min)

        if filters.area_min is not None:
            c.append(Property.area_m2 >= filters.area_min)

        if filters.area_max is not None:
            c.append(Property.area_m2 <= filters.area_max)

        if filters.is_featured is not None:
            c.append(Property.is_featured == filters.is_featured)

        return c

    def _amenity_subquery(self, slugs: list[str]):
        """
        Subquery: retorna solo propiedades que tengan TODAS las amenidades solicitadas.
        Usa COUNT para asegurar que se cumplen todas (AND, no OR).
        """
        from src.persistence.models.property_amenity import PropertyAmenity

        subq = (
            select(PropertyAmenity.property_id)
            .join(Amenity, Amenity.id == PropertyAmenity.amenity_id)
            .where(Amenity.slug.in_(slugs))
            .group_by(PropertyAmenity.property_id)
            .having(func.count(Amenity.id) == len(slugs))
            .scalar_subquery()
        )
        return Property.id.in_(subq)

    def _resolve_order(self, order_by: str):
        """Mapea el string de orden a la columna SQLAlchemy correspondiente."""
        options = {
            "price_asc":       Property.price.asc(),
            "price_desc":      Property.price.desc(),
            "created_at_desc": Property.created_at.desc(),
            "created_at_asc":  Property.created_at.asc(),
        }
        return options.get(order_by, Property.created_at.desc())

    async def _load_amenities(self, db: AsyncSession, ids: list[int]) -> list[Amenity]:
        result = await db.execute(select(Amenity).where(Amenity.id.in_(ids)))
        return list(result.scalars().all())


# Instancia lista para importar en servicios y endpoints
property_repository = PropertyRepository()
