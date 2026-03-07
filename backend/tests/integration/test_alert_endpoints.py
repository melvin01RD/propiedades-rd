"""
Integration tests — /alerts endpoints.
Todos los tests usan la DB real con rollback automático por fixture.
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy import select

from src.persistence.models.user import User
from src.persistence.models.owner import Owner


# ── Payload base ──────────────────────────────────────────────────

ALERT_PAYLOAD = {
    "name": "Alerta de integración",
    "filters": {
        "operation_type": "sale",
        "price_max": 300000,
    },
}


# ── Fixtures locales ──────────────────────────────────────────────

@pytest_asyncio.fixture
async def other_user_headers(async_client, db_session):
    """Segundo usuario para verificar restricciones de propiedad."""
    email = f"alert_other_{uuid.uuid4().hex[:8]}@test.com"
    resp = await async_client.post("/auth/register", json={
        "email": email, "password": "Integration123!", "role": "owner",
    })
    assert resp.status_code == 200

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    owner = Owner(user=user, first_name="Other", last_name="Alert")
    db_session.add(owner)
    await db_session.flush()

    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest_asyncio.fixture
async def test_alert(async_client, auth_headers):
    """Crea una alerta y retorna su body completo."""
    resp = await async_client.post("/alerts", json=ALERT_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── POST /alerts ──────────────────────────────────────────────────

class TestCreateAlert:

    @pytest.mark.asyncio
    async def test_create_alert_happy_path(self, async_client, auth_headers):
        """Usuario autenticado crea alerta → 201 con AlertResponse."""
        resp = await async_client.post("/alerts", json=ALERT_PAYLOAD, headers=auth_headers)

        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == ALERT_PAYLOAD["name"]
        assert "id" in body
        assert body["is_active"] is True

    @pytest.mark.asyncio
    async def test_create_alert_without_auth_returns_403(self, async_client):
        """Sin token retorna 403."""
        resp = await async_client.post("/alerts", json=ALERT_PAYLOAD)

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_create_alert_missing_filters_returns_422(self, async_client, auth_headers):
        """Payload sin filters (campo requerido) retorna 422."""
        payload = {k: v for k, v in ALERT_PAYLOAD.items() if k != "filters"}
        resp = await async_client.post("/alerts", json=payload, headers=auth_headers)

        assert resp.status_code == 422


# ── GET /alerts ───────────────────────────────────────────────────

class TestListAlerts:

    @pytest.mark.asyncio
    async def test_list_alerts_authenticated(self, async_client, auth_headers, test_alert):
        """Usuario autenticado recibe sus alertas."""
        resp = await async_client.get("/alerts", headers=auth_headers)

        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert any(a["id"] == test_alert["id"] for a in body)

    @pytest.mark.asyncio
    async def test_list_alerts_empty_for_new_user(self, async_client, other_user_headers):
        """Usuario sin alertas recibe lista vacía."""
        resp = await async_client.get("/alerts", headers=other_user_headers)

        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_alerts_without_auth_returns_403(self, async_client):
        """Sin token retorna 403."""
        resp = await async_client.get("/alerts")

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_list_alerts_isolated_between_users(
        self, async_client, auth_headers, other_user_headers, test_alert
    ):
        """Alertas de un usuario no aparecen en la lista de otro."""
        resp = await async_client.get("/alerts", headers=other_user_headers)

        assert resp.status_code == 200
        ids = [a["id"] for a in resp.json()]
        assert test_alert["id"] not in ids


# ── PUT /alerts/{alert_id} ────────────────────────────────────────

class TestUpdateAlert:

    @pytest.mark.asyncio
    async def test_owner_can_update_alert(self, async_client, auth_headers, test_alert):
        """Dueño puede actualizar su alerta → 200."""
        alert_id = test_alert["id"]
        resp = await async_client.put(
            f"/alerts/{alert_id}",
            json={"name": "Alerta actualizada", "is_active": False},
            headers=auth_headers,
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Alerta actualizada"
        assert body["is_active"] is False

    @pytest.mark.asyncio
    async def test_other_user_cannot_update_returns_403(
        self, async_client, other_user_headers, test_alert
    ):
        """Otro usuario no puede actualizar alerta ajena → 403."""
        alert_id = test_alert["id"]
        resp = await async_client.put(
            f"/alerts/{alert_id}",
            json={"name": "Intento de modificación"},
            headers=other_user_headers,
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_alert_without_auth_returns_403(self, async_client, test_alert):
        """Sin token retorna 403."""
        resp = await async_client.put(
            f"/alerts/{test_alert['id']}",
            json={"name": "Sin auth"},
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_nonexistent_alert_returns_404(self, async_client, auth_headers):
        """UUID inexistente retorna 404."""
        resp = await async_client.put(
            f"/alerts/{uuid.uuid4()}",
            json={"name": "No existe"},
            headers=auth_headers,
        )

        assert resp.status_code == 404


# ── DELETE /alerts/{alert_id} ─────────────────────────────────────

class TestDeleteAlert:

    @pytest.mark.asyncio
    async def test_owner_can_delete_alert(self, async_client, auth_headers, test_alert):
        """Dueño elimina su alerta → 204."""
        alert_id = test_alert["id"]
        resp = await async_client.delete(f"/alerts/{alert_id}", headers=auth_headers)

        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_other_user_cannot_delete_returns_403(
        self, async_client, other_user_headers, test_alert
    ):
        """Otro usuario no puede eliminar alerta ajena → 403."""
        alert_id = test_alert["id"]
        resp = await async_client.delete(f"/alerts/{alert_id}", headers=other_user_headers)

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_alert_without_auth_returns_403(self, async_client, test_alert):
        """Sin token retorna 403."""
        resp = await async_client.delete(f"/alerts/{test_alert['id']}")

        assert resp.status_code == 403
