from pydantic import BaseModel
from typing import Optional
import uuid


# ── Agent ──────────────────────────────────────────────────────────────────

class AgentProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    phone: Optional[str] = None
    license_number: Optional[str] = None
    agency_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class AgentProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    license_number: Optional[str] = None
    agency_name: Optional[str] = None
    bio: Optional[str] = None


class AgentProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    agency_name: Optional[str] = None
    bio: Optional[str] = None


# ── Owner ──────────────────────────────────────────────────────────────────

class OwnerProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class OwnerProfileCreate(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None


class OwnerProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
