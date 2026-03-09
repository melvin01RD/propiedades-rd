import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from src.services.profile_service import ProfileService
from src.persistence.models.user import User, UserRole
from src.persistence.models.agent import Agent
from src.persistence.models.owner import Owner
from src.api.schemas.profile_schemas import (
    AgentProfileCreate,
    AgentProfileUpdate,
    OwnerProfileCreate,
    OwnerProfileUpdate,
)


# ── Helpers ────────────────────────────────────────────────────────────────

def make_user(role: UserRole) -> User:
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.role = role
    return user


def make_agent(user_id: uuid.UUID) -> Agent:
    agent = MagicMock(spec=Agent)
    agent.id = uuid.uuid4()
    agent.user_id = user_id
    agent.first_name = "Juan"
    agent.last_name = "Pérez"
    agent.phone = "809-555-0001"
    agent.license_number = "LIC-001"
    agent.agency_name = "Inmobiliaria RD"
    agent.bio = "Agente con 5 años de experiencia"
    agent.avatar_url = None
    return agent


def make_owner(user_id: uuid.UUID) -> Owner:
    owner = MagicMock(spec=Owner)
    owner.id = uuid.uuid4()
    owner.user_id = user_id
    owner.first_name = "María"
    owner.last_name = "González"
    owner.phone = "809-555-0002"
    owner.avatar_url = None
    return owner


# ── Agent: GET ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_agent_profile_happy_path():
    user = make_user(UserRole.agent)
    agent = make_agent(user.id)
    db = AsyncMock()

    with patch("src.services.profile_service.agent_repository.get_by_user_id", return_value=agent):
        service = ProfileService(db)
        result = await service.get_agent_profile(user)

    assert result.user_id == agent.user_id
    assert result.first_name == "Juan"


@pytest.mark.asyncio
async def test_get_agent_profile_wrong_role_raises_403():
    user = make_user(UserRole.owner)
    db = AsyncMock()

    service = ProfileService(db)
    with pytest.raises(HTTPException) as exc:
        await service.get_agent_profile(user)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_agent_profile_not_found_raises_404():
    user = make_user(UserRole.agent)
    db = AsyncMock()

    with patch("src.services.profile_service.agent_repository.get_by_user_id", return_value=None):
        service = ProfileService(db)
        with pytest.raises(HTTPException) as exc:
            await service.get_agent_profile(user)

    assert exc.value.status_code == 404


# ── Agent: POST ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_agent_profile_happy_path():
    user = make_user(UserRole.agent)
    agent = make_agent(user.id)
    db = AsyncMock()
    data = AgentProfileCreate(first_name="Juan", last_name="Pérez", phone="809-555-0001")

    with patch("src.services.profile_service.agent_repository.get_by_user_id", return_value=None), \
         patch("src.services.profile_service.agent_repository.create", return_value=agent):
        service = ProfileService(db)
        result = await service.create_agent_profile(data, user)

    assert result.first_name == "Juan"


@pytest.mark.asyncio
async def test_create_agent_profile_duplicate_raises_409():
    user = make_user(UserRole.agent)
    agent = make_agent(user.id)
    db = AsyncMock()
    data = AgentProfileCreate(first_name="Juan", last_name="Pérez")

    with patch("src.services.profile_service.agent_repository.get_by_user_id", return_value=agent):
        service = ProfileService(db)
        with pytest.raises(HTTPException) as exc:
            await service.create_agent_profile(data, user)

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_create_agent_profile_wrong_role_raises_403():
    user = make_user(UserRole.owner)
    db = AsyncMock()
    data = AgentProfileCreate(first_name="Juan", last_name="Pérez")

    service = ProfileService(db)
    with pytest.raises(HTTPException) as exc:
        await service.create_agent_profile(data, user)

    assert exc.value.status_code == 403


# ── Agent: PUT ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_agent_profile_happy_path():
    user = make_user(UserRole.agent)
    agent = make_agent(user.id)
    updated_agent = make_agent(user.id)
    updated_agent.agency_name = "Nueva Agencia"
    db = AsyncMock()
    data = AgentProfileUpdate(agency_name="Nueva Agencia")

    with patch("src.services.profile_service.agent_repository.get_by_user_id", return_value=agent), \
         patch("src.services.profile_service.agent_repository.update", return_value=updated_agent):
        service = ProfileService(db)
        result = await service.update_agent_profile(data, user)

    assert result.agency_name == "Nueva Agencia"


@pytest.mark.asyncio
async def test_update_agent_profile_not_found_raises_404():
    user = make_user(UserRole.agent)
    db = AsyncMock()
    data = AgentProfileUpdate(bio="Nuevo bio")

    with patch("src.services.profile_service.agent_repository.get_by_user_id", return_value=None):
        service = ProfileService(db)
        with pytest.raises(HTTPException) as exc:
            await service.update_agent_profile(data, user)

    assert exc.value.status_code == 404


# ── Owner: GET ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_owner_profile_happy_path():
    user = make_user(UserRole.owner)
    owner = make_owner(user.id)
    db = AsyncMock()

    with patch("src.services.profile_service.owner_repository.get_by_user_id", return_value=owner):
        service = ProfileService(db)
        result = await service.get_owner_profile(user)

    assert result.first_name == "María"


@pytest.mark.asyncio
async def test_get_owner_profile_wrong_role_raises_403():
    user = make_user(UserRole.agent)
    db = AsyncMock()

    service = ProfileService(db)
    with pytest.raises(HTTPException) as exc:
        await service.get_owner_profile(user)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_get_owner_profile_not_found_raises_404():
    user = make_user(UserRole.owner)
    db = AsyncMock()

    with patch("src.services.profile_service.owner_repository.get_by_user_id", return_value=None):
        service = ProfileService(db)
        with pytest.raises(HTTPException) as exc:
            await service.get_owner_profile(user)

    assert exc.value.status_code == 404


# ── Owner: POST ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_owner_profile_happy_path():
    user = make_user(UserRole.owner)
    owner = make_owner(user.id)
    db = AsyncMock()
    data = OwnerProfileCreate(first_name="María", last_name="González")

    with patch("src.services.profile_service.owner_repository.get_by_user_id", return_value=None), \
         patch("src.services.profile_service.owner_repository.create", return_value=owner):
        service = ProfileService(db)
        result = await service.create_owner_profile(data, user)

    assert result.first_name == "María"


@pytest.mark.asyncio
async def test_create_owner_profile_duplicate_raises_409():
    user = make_user(UserRole.owner)
    owner = make_owner(user.id)
    db = AsyncMock()
    data = OwnerProfileCreate(first_name="María", last_name="González")

    with patch("src.services.profile_service.owner_repository.get_by_user_id", return_value=owner):
        service = ProfileService(db)
        with pytest.raises(HTTPException) as exc:
            await service.create_owner_profile(data, user)

    assert exc.value.status_code == 409


# ── Owner: PUT ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_owner_profile_happy_path():
    user = make_user(UserRole.owner)
    owner = make_owner(user.id)
    updated_owner = make_owner(user.id)
    updated_owner.phone = "809-999-9999"
    db = AsyncMock()
    data = OwnerProfileUpdate(phone="809-999-9999")

    with patch("src.services.profile_service.owner_repository.get_by_user_id", return_value=owner), \
         patch("src.services.profile_service.owner_repository.update", return_value=updated_owner):
        service = ProfileService(db)
        result = await service.update_owner_profile(data, user)

    assert result.phone == "809-999-9999"


@pytest.mark.asyncio
async def test_update_owner_profile_not_found_raises_404():
    user = make_user(UserRole.owner)
    db = AsyncMock()
    data = OwnerProfileUpdate(phone="809-000-0000")

    with patch("src.services.profile_service.owner_repository.get_by_user_id", return_value=None):
        service = ProfileService(db)
        with pytest.raises(HTTPException) as exc:
            await service.update_owner_profile(data, user)

    assert exc.value.status_code == 404
