"""
Schemas de propiedades:
- PropertyCreate   → POST /properties
- PropertyUpdate   → PUT /properties/{id}
- PropertyResponse → respuesta completa
- PropertyListItem → respuesta en listado (más ligera)
- PropertyFilters  → query params para GET /properties
"""

import uuid
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from src.persistence.models.property import (
    PropertyType, OperationType, Currency, PropertyStatus
)
from src.api.schemas.catalog_schemas import (
    ProvinceResponse, SectorResponse, AmenityResponse
)


# ── Imagen embebida en la respuesta ───────────────────────────────────────────

class PropertyImageEmbed(BaseModel):
    id:                 uuid.UUID
    cloudinary_url:     str
    is_cover:           bool
    sort_order:         int

    model_config = {"from_attributes": True}


# ── Create ─────────────────────────────────────────────────────────────────────

class PropertyCreate(BaseModel):
    title:          str             = Field(..., min_length=5, max_length=200)
    description:    str | None      = None
    property_type:  PropertyType
    operation_type: OperationType
    price:          Decimal         = Field(..., gt=0)
    currency:       Currency        = Currency.USD

    bedrooms:       int | None      = Field(None, ge=0, le=50)
    bathrooms:      int | None      = Field(None, ge=0, le=50)
    parking_spots:  int | None      = Field(None, ge=0, le=50)
    area_m2:        Decimal | None  = Field(None, gt=0)
    floors:         int | None      = Field(None, ge=1, le=200)
    year_built:     int | None      = Field(None, ge=1800, le=2100)

    province_id:    int
    sector_id:      int | None      = None
    city:           str             = Field(..., min_length=2, max_length=100)
    address:        str | None      = Field(None, max_length=255)

    # IDs de amenidades a asociar
    amenity_ids:    list[int]       = Field(default_factory=list)

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v


# ── Update (todos los campos opcionales) ──────────────────────────────────────

class PropertyUpdate(BaseModel):
    title:          str | None      = Field(None, min_length=5, max_length=200)
    description:    str | None      = None
    property_type:  PropertyType | None  = None
    operation_type: OperationType | None = None
    price:          Decimal | None  = Field(None, gt=0)
    currency:       Currency | None = None

    bedrooms:       int | None      = Field(None, ge=0, le=50)
    bathrooms:      int | None      = Field(None, ge=0, le=50)
    parking_spots:  int | None      = Field(None, ge=0, le=50)
    area_m2:        Decimal | None  = Field(None, gt=0)
    floors:         int | None      = Field(None, ge=1, le=200)
    year_built:     int | None      = Field(None, ge=1800, le=2100)

    province_id:    int | None      = None
    sector_id:      int | None      = None
    city:           str | None      = Field(None, min_length=2, max_length=100)
    address:        str | None      = Field(None, max_length=255)

    status:         PropertyStatus | None = None
    is_featured:    bool | None     = None

    # None = no tocar amenidades, [] = eliminar todas, [1,2] = reemplazar
    amenity_ids:    list[int] | None = None


# ── Response completo ─────────────────────────────────────────────────────────

class PropertyResponse(BaseModel):
    id:             uuid.UUID
    title:          str
    description:    str | None
    property_type:  PropertyType
    operation_type: OperationType
    price:          Decimal
    currency:       Currency

    bedrooms:       int | None
    bathrooms:      int | None
    parking_spots:  int | None
    area_m2:        Decimal | None
    floors:         int | None
    year_built:     int | None

    country:        str
    city:           str
    address:        str | None
    province:       ProvinceResponse
    sector:         SectorResponse | None

    status:         PropertyStatus
    is_featured:    bool

    images:         list[PropertyImageEmbed]
    amenities:      list[AmenityResponse]

    model_config = {"from_attributes": True}


# ── Item en listado (más ligero, sin descripción larga) ───────────────────────

class PropertyListItem(BaseModel):
    id:             uuid.UUID
    title:          str
    property_type:  PropertyType
    operation_type: OperationType
    price:          Decimal
    currency:       Currency
    bedrooms:       int | None
    bathrooms:      int | None
    area_m2:        Decimal | None
    province:       ProvinceResponse
    sector:         SectorResponse | None
    is_featured:    bool
    cover_image:    str | None      = None  # URL de la imagen portada

    model_config = {"from_attributes": True}

    @classmethod
    def from_property(cls, prop) -> "PropertyListItem":
        cover = next((img.cloudinary_url for img in prop.images if img.is_cover), None)
        if not cover and prop.images:
            cover = prop.images[0].cloudinary_url
        return cls(
            id=prop.id,
            title=prop.title,
            property_type=prop.property_type,
            operation_type=prop.operation_type,
            price=prop.price,
            currency=prop.currency,
            bedrooms=prop.bedrooms,
            bathrooms=prop.bathrooms,
            area_m2=prop.area_m2,
            province=prop.province,
            sector=prop.sector,
            is_featured=prop.is_featured,
            cover_image=cover,
        )


# ── Respuesta paginada ─────────────────────────────────────────────────────────

class PropertyPageResponse(BaseModel):
    items:    list[PropertyListItem]
    total:    int
    page:     int
    limit:    int
    pages:    int
    has_next: bool
    has_prev: bool


# ── Query params (filtros) ─────────────────────────────────────────────────────

class PropertyFilters(BaseModel):
    operation_type:    OperationType | None  = None
    property_type:     PropertyType | None   = None
    price_min:         Decimal | None        = None
    price_max:         Decimal | None        = None
    province_id:       int | None            = None
    sector_id:         int | None            = None
    bedrooms_min:      int | None            = Field(None, ge=0)
    bathrooms_min:     int | None            = Field(None, ge=0)
    parking_spots_min: int | None            = Field(None, ge=0)
    area_min:          Decimal | None        = None
    area_max:          Decimal | None        = None
    amenity_slugs:     list[str]             = Field(default=[])
    is_featured:       bool | None           = None
    page:              int                   = Field(1, ge=1)
    limit:             int                   = Field(20, ge=1, le=100)
    order_by:          str                   = "created_at_desc"
