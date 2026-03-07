"""
Schemas de respuesta para catálogos:
- Province
- Sector
- Amenity (agrupado por categoría)
"""

from pydantic import BaseModel
from src.persistence.models.amenity import AmenityCategory


class ProvinceResponse(BaseModel):
    id:   int
    name: str
    code: str

    model_config = {"from_attributes": True}


class SectorResponse(BaseModel):
    id:          int
    name:        str
    province_id: int

    model_config = {"from_attributes": True}


class AmenityResponse(BaseModel):
    id:       int
    name:     str
    slug:     str
    category: AmenityCategory
    icon:     str | None

    model_config = {"from_attributes": True}


class AmenitiesByCategoryResponse(BaseModel):
    category: AmenityCategory
    items:    list[AmenityResponse]
