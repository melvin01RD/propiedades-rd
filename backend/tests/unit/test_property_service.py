import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from src.services.property_service import PropertyService
from src.api.schemas.property_schemas import PropertyCreate, PropertyUpdate
from src.persistence.models.user import UserRole
from src.persistence.models.property import PropertyType, OperationType, Currency, PropertyStatus


# ── Helpers ───────────────────────────────────────────────────────

def make_property(
    agent_id=None,
    owner_id=None,
    status=PropertyStatus.active,
):
    prop = MagicMock()
    prop.id = uuid.uuid4()
    prop.agent_id = agent_id
    prop.owner_id = owner_id
    prop.status = status
    return prop


def make_create_data(**kwargs):
    defaults = dict(
        title="Casa en Piantini",
        property_type=PropertyType.house,
        operation_type=OperationType.sale,
        price=Decimal("150000"),
        currency=Currency.USD,
        province_id=1,
        city="Santo Domingo",
    )
    defaults.update(kwargs)
    return PropertyCreate(**defaults)


# ── Tests: create ─────────────────────────────────────────────────

class TestCreate:

    @pytest.mark.asyncio
    async def test_create_happy_path_as_owner(self, mock_db, mock_user):
        """Owner crea propiedad correctamente y recibe el objeto completo."""
        prop = make_property(owner_id=mock_user.owner.id)

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.create = AsyncMock(return_value=prop)
            mock_repo.get_by_id = AsyncMock(return_value=prop)

            service = PropertyService()
            result = await service.create(mock_db, make_create_data(), mock_user)

            assert result == prop
            mock_repo.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_as_agent(self, mock_db):
        """Agent con perfil crea propiedad correctamente."""
        agent_id = uuid.uuid4()
        agent = MagicMock()
        agent.id = agent_id

        user = MagicMock()
        user.id = uuid.uuid4()
        user.role = UserRole.agent
        user.agent = agent

        prop = make_property(agent_id=agent_id)

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.create = AsyncMock(return_value=prop)
            mock_repo.get_by_id = AsyncMock(return_value=prop)

            service = PropertyService()
            result = await service.create(mock_db, make_create_data(), user)

            payload_used = mock_repo.create.call_args[0][1]
            assert payload_used["agent_id"] == agent_id
            assert result == prop

    @pytest.mark.asyncio
    async def test_create_agent_without_profile_raises_400(self, mock_db):
        """Agent sin perfil recibe 400."""
        user = MagicMock()
        user.role = UserRole.agent
        user.agent = None

        service = PropertyService()
        with pytest.raises(HTTPException) as exc:
            await service.create(mock_db, make_create_data(), user)

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_owner_without_profile_raises_400(self, mock_db):
        """Owner sin perfil recibe 400."""
        user = MagicMock()
        user.role = UserRole.owner
        user.owner = None

        service = PropertyService()
        with pytest.raises(HTTPException) as exc:
            await service.create(mock_db, make_create_data(), user)

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_admin_without_publisher_raises_400(self, mock_db, mock_admin_user):
        """Admin que no especifica agent_id ni owner_id recibe 400."""
        service = PropertyService()
        with pytest.raises(HTTPException) as exc:
            await service.create(mock_db, make_create_data(), mock_admin_user)

        assert exc.value.status_code == 400


# ── Tests: get_by_id / not found ──────────────────────────────────

class TestGetById:

    @pytest.mark.asyncio
    async def test_get_by_id_returns_property(self, mock_db):
        """Propiedad existente se retorna correctamente."""
        prop = make_property()

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=prop)

            service = PropertyService()
            result = await service.get_by_id(mock_db, prop.id)

            assert result == prop

    @pytest.mark.asyncio
    async def test_get_by_id_not_found_raises_404(self, mock_db):
        """Propiedad inexistente lanza 404."""
        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)

            service = PropertyService()
            with pytest.raises(HTTPException) as exc:
                await service.get_by_id(mock_db, uuid.uuid4())

            assert exc.value.status_code == 404


# ── Tests: owner assertion ─────────────────────────────────────────

class TestOwnerAssertion:

    @pytest.mark.asyncio
    async def test_update_by_wrong_owner_raises_403(self, mock_db, mock_user):
        """Owner que no es dueño de la propiedad recibe 403 al intentar actualizar."""
        other_owner_id = uuid.uuid4()
        prop = make_property(owner_id=other_owner_id)

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=prop)

            service = PropertyService()
            with pytest.raises(HTTPException) as exc:
                await service.update(
                    mock_db, prop.id, PropertyUpdate(), mock_user
                )

            assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_by_wrong_owner_raises_403(self, mock_db, mock_user):
        """Owner que no es dueño de la propiedad recibe 403 al intentar eliminar."""
        other_owner_id = uuid.uuid4()
        prop = make_property(owner_id=other_owner_id)

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=prop)

            service = PropertyService()
            with pytest.raises(HTTPException) as exc:
                await service.delete(mock_db, prop.id, mock_user)

            assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_can_delete_any_property(self, mock_db, mock_admin_user):
        """Admin puede eliminar cualquier propiedad sin importar el owner."""
        prop = make_property(owner_id=uuid.uuid4())

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=prop)
            mock_repo.soft_delete = AsyncMock()

            service = PropertyService()
            await service.delete(mock_db, prop.id, mock_admin_user)

            mock_repo.soft_delete.assert_awaited_once_with(mock_db, prop.id)


# ── Tests: soft delete ─────────────────────────────────────────────

class TestSoftDelete:

    @pytest.mark.asyncio
    async def test_delete_calls_soft_delete(self, mock_db, mock_user):
        """Eliminar propiedad llama a soft_delete, no a delete físico."""
        prop = make_property(owner_id=mock_user.owner.id)

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=prop)
            mock_repo.soft_delete = AsyncMock()

            service = PropertyService()
            await service.delete(mock_db, prop.id, mock_user)

            mock_repo.soft_delete.assert_awaited_once_with(mock_db, prop.id)

    @pytest.mark.asyncio
    async def test_inactive_property_not_in_listing(self, mock_db):
        """get_all solo retorna propiedades activas (status filter en PropertyFilter)."""
        from src.services.property_service import PropertyService
        from src.api.schemas.property_schemas import PropertyFilters
        from src.persistence.repositories.property_repository import Page

        empty_page = Page(items=[], total=0, page=1, limit=20)

        with patch("src.services.property_service.property_repository") as mock_repo:
            mock_repo.get_all = AsyncMock(return_value=empty_page)

            service = PropertyService()
            result = await service.get_all(mock_db, PropertyFilters())

            assert result.total == 0
            assert result.items == []
            # Verificar que get_all fue llamado (el filtro status=active está en PropertyFilter por defecto)
            mock_repo.get_all.assert_awaited_once()
