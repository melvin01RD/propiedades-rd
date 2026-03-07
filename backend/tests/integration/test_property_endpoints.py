"""
Integration tests — /properties endpoints.
Todos los tests usan la DB real con rollback automático por fixture.
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy import select

from src.persistence.models.user import User
from src.persistence.models.owner import Owner


# ── Payload base ──────────────────────────────────────────────────

PROPERTY_PAYLOAD = {
    "title": "Casa de integración test",
    "property_type": "house",
    "operation_type": "sale",
    "price": "150000",
    "currency": "USD",
    "province_id": 1,
    "city": "Santo Domingo",
}


# ── Fixtures locales ──────────────────────────────────────────────

@pytest_asyncio.fixture
async def owner_headers(async_client, db_session):
    """Registra usuario + crea perfil Owner. El backref user=user_obj
    conecta la relación en el identity map sin lazy load."""
    email = f"owner_{uuid.uuid4().hex[:8]}@test.com"
    resp = await async_client.post("/auth/register", json={
        "email": email, "password": "Integration123!", "role": "owner",
    })
    assert resp.status_code == 200

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    owner = Owner(user=user, first_name="Test", last_name="Owner")
    db_session.add(owner)
    await db_session.flush()

    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest_asyncio.fixture
async def other_owner_headers(async_client, db_session):
    """Segundo owner, sin propiedades propias."""
    email = f"other_{uuid.uuid4().hex[:8]}@test.com"
    resp = await async_client.post("/auth/register", json={
        "email": email, "password": "Integration123!", "role": "owner",
    })
    assert resp.status_code == 200

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    owner = Owner(user=user, first_name="Other", last_name="Owner")
    db_session.add(owner)
    await db_session.flush()

    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest_asyncio.fixture
async def test_property(async_client, owner_headers):
    """Crea una propiedad como owner y retorna el body completo."""
    resp = await async_client.post("/properties", json=PROPERTY_PAYLOAD, headers=owner_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── POST /properties ──────────────────────────────────────────────

class TestCreateProperty:

    @pytest.mark.asyncio
    async def test_create_happy_path_as_owner(self, async_client, owner_headers):
        """Owner autenticado crea propiedad → 201 con PropertyResponse."""
        resp = await async_client.post("/properties", json=PROPERTY_PAYLOAD, headers=owner_headers)

        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == PROPERTY_PAYLOAD["title"]
        assert body["property_type"] == "house"
        assert "id" in body
        assert "province" in body

    @pytest.mark.asyncio
    async def test_create_without_auth_returns_403(self, async_client):
        """Sin token retorna 403."""
        resp = await async_client.post("/properties", json=PROPERTY_PAYLOAD)

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_create_missing_required_field_returns_422(self, async_client, owner_headers):
        """Payload sin título retorna 422."""
        payload = {k: v for k, v in PROPERTY_PAYLOAD.items() if k != "title"}
        resp = await async_client.post("/properties", json=payload, headers=owner_headers)

        assert resp.status_code == 422


# ── GET /properties ───────────────────────────────────────────────

class TestListProperties:

    @pytest.mark.asyncio
    async def test_list_is_public(self, async_client):
        """El listado no requiere autenticación."""
        resp = await async_client.get("/properties")

        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert "page" in body
        assert "pages" in body
        assert "has_next" in body

    @pytest.mark.asyncio
    async def test_list_with_filters(self, async_client):
        """Filtros de query params son aceptados sin error."""
        resp = await async_client.get(
            "/properties",
            params={"operation_type": "sale", "price_min": "50000", "page": 1, "limit": 5},
        )

        assert resp.status_code == 200
        assert resp.json()["limit"] == 5

    @pytest.mark.asyncio
    async def test_list_invalid_order_by_still_returns_200(self, async_client):
        """Un order_by desconocido usa el default (created_at_desc) sin error."""
        resp = await async_client.get("/properties", params={"order_by": "inexistente"})

        assert resp.status_code == 200


# ── GET /properties/{id} ──────────────────────────────────────────

class TestGetProperty:

    @pytest.mark.asyncio
    async def test_get_existing_property(self, async_client, test_property):
        """Propiedad existente retorna 200 con sus datos."""
        prop_id = test_property["id"]
        resp = await async_client.get(f"/properties/{prop_id}")

        assert resp.status_code == 200
        assert resp.json()["id"] == prop_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_property_returns_404(self, async_client):
        """UUID inexistente retorna 404."""
        resp = await async_client.get(f"/properties/{uuid.uuid4()}")

        assert resp.status_code == 404


# ── PUT /properties/{id} ──────────────────────────────────────────

class TestUpdateProperty:

    @pytest.mark.asyncio
    async def test_owner_can_update(self, async_client, test_property, owner_headers):
        """El owner puede actualizar su propiedad."""
        prop_id = test_property["id"]
        resp = await async_client.put(
            f"/properties/{prop_id}",
            json={"title": "Título actualizado por owner"},
            headers=owner_headers,
        )

        assert resp.status_code == 200
        assert resp.json()["title"] == "Título actualizado por owner"

    @pytest.mark.asyncio
    async def test_other_user_cannot_update_returns_403(
        self, async_client, test_property, other_owner_headers
    ):
        """Otro usuario recibe 403 al intentar actualizar."""
        prop_id = test_property["id"]
        resp = await async_client.put(
            f"/properties/{prop_id}",
            json={"title": "Intento de hackeo"},
            headers=other_owner_headers,
        )

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_without_auth_returns_403(self, async_client, test_property):
        """Sin token retorna 403."""
        resp = await async_client.put(
            f"/properties/{test_property['id']}",
            json={"title": "Sin auth"},
        )

        assert resp.status_code == 403


# ── DELETE /properties/{id} ───────────────────────────────────────

class TestDeleteProperty:

    @pytest.mark.asyncio
    async def test_owner_can_delete(self, async_client, test_property, owner_headers):
        """El owner elimina su propiedad → 204."""
        prop_id = test_property["id"]
        resp = await async_client.delete(f"/properties/{prop_id}", headers=owner_headers)

        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_other_user_cannot_delete_returns_403(
        self, async_client, test_property, other_owner_headers
    ):
        """Otro usuario recibe 403 al intentar eliminar."""
        prop_id = test_property["id"]
        resp = await async_client.delete(f"/properties/{prop_id}", headers=other_owner_headers)

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_without_auth_returns_403(self, async_client, test_property):
        """Sin token retorna 403."""
        resp = await async_client.delete(f"/properties/{test_property['id']}")

        assert resp.status_code == 403
