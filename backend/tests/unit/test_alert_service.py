import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from src.services.alert_service import AlertService
from src.api.schemas.alert_schemas import AlertCreate, AlertUpdate, AlertFilters
from src.persistence.models.property import OperationType


# ── Helpers ───────────────────────────────────────────────────────

def make_alert(user_id):
    alert = MagicMock()
    alert.id = uuid.uuid4()
    alert.user_id = user_id
    alert.name = "Alerta test"
    alert.filters = {}
    alert.is_active = True
    return alert


def make_create_data(name="Mi alerta"):
    return AlertCreate(
        name=name,
        filters=AlertFilters(operation_type=OperationType.sale, price_max=200000.0),
    )


def make_update_data(**kwargs):
    return AlertUpdate(**kwargs)


# ── Tests: create ─────────────────────────────────────────────────

class TestCreate:

    @pytest.mark.asyncio
    async def test_create_happy_path(self, mock_db, mock_user):
        """Alerta con filtros se crea correctamente."""
        alert = make_alert(mock_user.id)

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.create = AsyncMock(return_value=alert)

            service = AlertService()
            result = await service.create(mock_db, make_create_data(), mock_user.id)

            assert result == alert
            call_payload = mock_repo.create.call_args[0][2]
            assert "filters" in call_payload
            assert "name" in call_payload

    @pytest.mark.asyncio
    async def test_create_serializes_filters(self, mock_db, mock_user):
        """Los filtros se serializan a dict con exclude_none=True."""
        alert = make_alert(mock_user.id)
        data = make_create_data()

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.create = AsyncMock(return_value=alert)

            service = AlertService()
            await service.create(mock_db, data, mock_user.id)

            payload = mock_repo.create.call_args[0][2]
            # Los campos None no deben estar en el dict de filtros
            assert None not in payload["filters"].values()


# ── Tests: update ─────────────────────────────────────────────────

class TestUpdate:

    @pytest.mark.asyncio
    async def test_update_own_alert(self, mock_db, mock_user):
        """Dueño actualiza su alerta correctamente."""
        alert = make_alert(mock_user.id)
        updated = make_alert(mock_user.id)
        updated.is_active = False

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=alert)
            mock_repo.update = AsyncMock(return_value=updated)

            service = AlertService()
            result = await service.update(
                mock_db, alert.id, make_update_data(is_active=False), mock_user
            )

            assert result == updated
            mock_repo.update.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_foreign_alert_raises_403(self, mock_db, mock_user):
        """Intentar actualizar alerta ajena lanza 403."""
        other_user_id = uuid.uuid4()
        alert = make_alert(other_user_id)  # dueño distinto

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=alert)

            service = AlertService()
            with pytest.raises(HTTPException) as exc:
                await service.update(
                    mock_db, alert.id, make_update_data(is_active=False), mock_user
                )

            assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_update_nonexistent_alert_raises_404(self, mock_db, mock_user):
        """Actualizar alerta inexistente lanza 404."""
        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)

            service = AlertService()
            with pytest.raises(HTTPException) as exc:
                await service.update(
                    mock_db, uuid.uuid4(), make_update_data(is_active=False), mock_user
                )

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_filters_serialized_when_present(self, mock_db, mock_user):
        """Si filters viene en el payload, se serializa con model_dump(exclude_none=True)."""
        alert = make_alert(mock_user.id)
        updated = make_alert(mock_user.id)
        new_filters = AlertFilters(operation_type=OperationType.rent)
        data = AlertUpdate(filters=new_filters)

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=alert)
            mock_repo.update = AsyncMock(return_value=updated)

            service = AlertService()
            await service.update(mock_db, alert.id, data, mock_user)

            payload = mock_repo.update.call_args[0][2]
            assert isinstance(payload["filters"], dict)
            assert None not in payload["filters"].values()


# ── Tests: delete ─────────────────────────────────────────────────

class TestDelete:

    @pytest.mark.asyncio
    async def test_delete_own_alert(self, mock_db, mock_user):
        """Dueño elimina su alerta correctamente."""
        alert = make_alert(mock_user.id)

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=alert)
            mock_repo.delete = AsyncMock()

            service = AlertService()
            await service.delete(mock_db, alert.id, mock_user)

            mock_repo.delete.assert_awaited_once_with(mock_db, alert)

    @pytest.mark.asyncio
    async def test_delete_foreign_alert_raises_403(self, mock_db, mock_user):
        """Intentar eliminar alerta ajena lanza 403."""
        alert = make_alert(uuid.uuid4())  # dueño distinto

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=alert)

            service = AlertService()
            with pytest.raises(HTTPException) as exc:
                await service.delete(mock_db, alert.id, mock_user)

            assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_nonexistent_alert_raises_404(self, mock_db, mock_user):
        """Eliminar alerta inexistente lanza 404."""
        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)

            service = AlertService()
            with pytest.raises(HTTPException) as exc:
                await service.delete(mock_db, uuid.uuid4(), mock_user)

            assert exc.value.status_code == 404


# ── Tests: get_my_alerts ──────────────────────────────────────────

class TestGetMyAlerts:

    @pytest.mark.asyncio
    async def test_get_my_alerts_returns_list(self, mock_db, mock_user):
        """Retorna la lista de alertas del usuario."""
        alerts = [make_alert(mock_user.id), make_alert(mock_user.id)]

        with patch("src.services.alert_service.alert_repository") as mock_repo:
            mock_repo.get_by_user = AsyncMock(return_value=alerts)

            service = AlertService()
            result = await service.get_my_alerts(mock_db, mock_user.id)

            assert result == alerts
            mock_repo.get_by_user.assert_awaited_once_with(mock_db, mock_user.id)
