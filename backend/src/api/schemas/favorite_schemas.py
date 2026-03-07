from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel
from src.api.schemas.property_schemas import PropertyListItem


class FavoriteResponse(BaseModel):
    property_id: uuid.UUID
    created_at:  datetime

    model_config = {"from_attributes": True}


class FavoriteDetailResponse(BaseModel):
    property_id: uuid.UUID
    created_at:  datetime
    property:    PropertyListItem

    model_config = {"from_attributes": True}
