from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, get_current_user
from src.persistence.models.user import User
from src.services.profile_service import ProfileService
from src.api.schemas.profile_schemas import (
    AgentProfileCreate,
    AgentProfileUpdate,
    AgentProfileResponse,
    OwnerProfileCreate,
    OwnerProfileUpdate,
    OwnerProfileResponse,
)


# ── Agent ──────────────────────────────────────────────────────────────────

async def get_agent_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentProfileResponse:
    return await ProfileService(db).get_agent_profile(current_user)


async def create_agent_me(
    data: AgentProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentProfileResponse:
    return await ProfileService(db).create_agent_profile(data, current_user)


async def update_agent_me(
    data: AgentProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AgentProfileResponse:
    return await ProfileService(db).update_agent_profile(data, current_user)


# ── Owner ──────────────────────────────────────────────────────────────────

async def get_owner_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OwnerProfileResponse:
    return await ProfileService(db).get_owner_profile(current_user)


async def create_owner_me(
    data: OwnerProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OwnerProfileResponse:
    return await ProfileService(db).create_owner_profile(data, current_user)


async def update_owner_me(
    data: OwnerProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OwnerProfileResponse:
    return await ProfileService(db).update_owner_profile(data, current_user)
