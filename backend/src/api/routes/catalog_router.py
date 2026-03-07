"""
Endpoints de catálogos — solo lectura, públicos (no requieren auth).

GET /provinces
GET /provinces/{province_id}/sectors
GET /amenities
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db
from src.persistence.models import Province, Sector, Amenity
from src.persistence.models.amenity import AmenityCategory
from src.api.schemas.catalog_schemas import (
    ProvinceResponse,
    SectorResponse,
    AmenityResponse,
    AmenitiesByCategoryResponse,
)

router = APIRouter(prefix="/catalogs", tags=["Catálogos"])


@router.get(
    "/provinces",
    response_model=list[ProvinceResponse],
    summary="Lista las 32 provincias/DN de RD",
)
async def get_provinces(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Province).order_by(Province.name)
    )
    return result.scalars().all()


@router.get(
    "/provinces/{province_id}/sectors",
    response_model=list[SectorResponse],
    summary="Sectores de una provincia",
)
async def get_sectors_by_province(
    province_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Verificar que la provincia existe
    province = await db.get(Province, province_id)
    if not province:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provincia {province_id} no encontrada",
        )

    result = await db.execute(
        select(Sector)
        .where(Sector.province_id == province_id)
        .order_by(Sector.name)
    )
    return result.scalars().all()


@router.get(
    "/amenities",
    response_model=list[AmenitiesByCategoryResponse],
    summary="Amenidades agrupadas por categoría",
)
async def get_amenities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Amenity).order_by(Amenity.category, Amenity.name)
    )
    amenities = result.scalars().all()

    # Agrupar por categoría
    grouped: dict[AmenityCategory, list[Amenity]] = {}
    for amenity in amenities:
        grouped.setdefault(amenity.category, []).append(amenity)

    return [
        AmenitiesByCategoryResponse(
            category=category,
            items=items,
        )
        for category, items in grouped.items()
    ]
