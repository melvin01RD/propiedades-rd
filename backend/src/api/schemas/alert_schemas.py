from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from src.persistence.models.property import PropertyType, OperationType


class AlertFilters(BaseModel):
    operation_type: OperationType | None = None
    property_type:  PropertyType | None  = None
    price_min:      float | None         = None
    price_max:      float | None         = None
    province_id:    int | None           = None
    sector_id:      int | None           = None
    bedrooms_min:   int | None           = None
    bathrooms_min:  int | None           = None
    amenity_slugs:  list[str]            = Field(default_factory=list)


class AlertCreate(BaseModel):
    name:    str | None  = Field(None, max_length=100)
    filters: AlertFilters


class AlertUpdate(BaseModel):
    name:      str | None      = Field(None, max_length=100)
    is_active: bool | None     = None
    filters:   AlertFilters | None = None


class AlertResponse(BaseModel):
    id:                uuid.UUID
    name:              str | None
    filters:           dict
    is_active:         bool
    last_triggered_at: datetime | None
    created_at:        datetime

    model_config = {"from_attributes": True}
