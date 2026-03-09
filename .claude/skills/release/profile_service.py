from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.persistence.models.user import User, UserRole
from src.persistence.repositories.agent_repository import agent_repository
from src.persistence.repositories.owner_repository import owner_repository
from src.api.schemas.profile_schemas import (
    AgentProfileCreate,
    AgentProfileUpdate,
    AgentProfileResponse,
    OwnerProfileCreate,
    OwnerProfileUpdate,
    OwnerProfileResponse,
)


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Agent ──────────────────────────────────────────────────────────────

    async def get_agent_profile(self, current_user: User) -> AgentProfileResponse:
        if current_user.role != UserRole.agent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los agentes tienen perfil de agente",
            )
        agent = await agent_repository.get_by_user_id(self.db, current_user.id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de agente no encontrado. Completa tu onboarding.",
            )
        return AgentProfileResponse.model_validate(agent)

    async def create_agent_profile(self, data: AgentProfileCreate, current_user: User) -> AgentProfileResponse:
        if current_user.role != UserRole.agent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los agentes pueden crear un perfil de agente",
            )
        existing = await agent_repository.get_by_user_id(self.db, current_user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El perfil de agente ya existe. Usa PUT para actualizarlo.",
            )
        agent = await agent_repository.create(
            self.db,
            user_id=current_user.id,
            **data.model_dump(exclude_none=True),
        )
        return AgentProfileResponse.model_validate(agent)

    async def update_agent_profile(self, data: AgentProfileUpdate, current_user: User) -> AgentProfileResponse:
        if current_user.role != UserRole.agent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los agentes pueden actualizar un perfil de agente",
            )
        agent = await agent_repository.get_by_user_id(self.db, current_user.id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado. Crea tu perfil primero con POST /agents/me.",
            )
        agent = await agent_repository.update(
            self.db,
            agent,
            **data.model_dump(exclude_none=True),
        )
        return AgentProfileResponse.model_validate(agent)

    # ── Owner ──────────────────────────────────────────────────────────────

    async def get_owner_profile(self, current_user: User) -> OwnerProfileResponse:
        if current_user.role != UserRole.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los propietarios tienen perfil de propietario",
            )
        owner = await owner_repository.get_by_user_id(self.db, current_user.id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil de propietario no encontrado. Completa tu onboarding.",
            )
        return OwnerProfileResponse.model_validate(owner)

    async def create_owner_profile(self, data: OwnerProfileCreate, current_user: User) -> OwnerProfileResponse:
        if current_user.role != UserRole.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los propietarios pueden crear un perfil de propietario",
            )
        existing = await owner_repository.get_by_user_id(self.db, current_user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El perfil de propietario ya existe. Usa PUT para actualizarlo.",
            )
        owner = await owner_repository.create(
            self.db,
            user_id=current_user.id,
            **data.model_dump(exclude_none=True),
        )
        return OwnerProfileResponse.model_validate(owner)

    async def update_owner_profile(self, data: OwnerProfileUpdate, current_user: User) -> OwnerProfileResponse:
        if current_user.role != UserRole.owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los propietarios pueden actualizar un perfil de propietario",
            )
        owner = await owner_repository.get_by_user_id(self.db, current_user.id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Perfil no encontrado. Crea tu perfil primero con POST /owners/me.",
            )
        owner = await owner_repository.update(
            self.db,
            owner,
            **data.model_dump(exclude_none=True),
        )
        return OwnerProfileResponse.model_validate(owner)
