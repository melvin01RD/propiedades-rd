"""
Integration tests — /favorites endpoints.
Todos los tests usan la DB real con rollback automático por fixture.
"""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy import select

from src.persistence.models.user import User
from src.persistence.models.owner import Owner
from src.persistence.models.property import Property, PropertyStatus


# ── Fixtures locales ──────────────────────────────────────────────

@pytest_asyncio.fixture
async def owner_headers(async_client, db_session):
    """Registra usuario + crea perfil Owner."""
    email = f"fav_owner_{uuid.uuid4().hex[:8]}@test.com"
    resp = await async_client.post("/auth/register", json={
        "email": email, "password": "Integration123!", "role": "owner",
    })
    assert resp.status_code == 200

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    owner = Owner(user=user, first_name="Fav", last_name="Owner")
    db_session.add(owner)
    await db_session.flush()

    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest_asyncio.fixture
async def active_property(async_client, owner_headers, db_session):
    """Crea una propiedad y la activa para que pueda ser agregada a favoritos."""
    create_resp = await async_client.post("/properties", json={
        "title": "Propiedad para favoritos",
        "property_type": "house",
        "operation_type": "sale",
        "price": "120000",
        "currency": "USD",
        "province_id": 1,
        "city": "Santiago",
    }, headers=owner_headers)
    assert create_resp.status_code == 201, create_resp.text
    prop_id = create_resp.json()["id"]

    # Activar la propiedad (por defecto queda en draft)
    activate_resp = await async_client.put(
        f"/properties/{prop_id}",
        json={"status": "active"},
        headers=owner_headers,
    )
    assert activate_resp.status_code == 200, activate_resp.text

    return activate_resp.json()


@pytest_asyncio.fixture
async def second_user_headers(async_client, db_session):
    """Segundo usuario (owner) para probar sus favoritos independientes."""
    email = f"fav_second_{uuid.uuid4().hex[:8]}@test.com"
    resp = await async_client.post("/auth/register", json={
        "email": email, "password": "Integration123!", "role": "owner",
    })
    assert resp.status_code == 200

    result = await db_session.execute(select(User).where(User.email == email))
    user = result.scalar_one()

    owner = Owner(user=user, first_name="Second", last_name="User")
    db_session.add(owner)
    await db_session.flush()

    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── POST /favorites/{property_id} ─────────────────────────────────

class TestAddFavorite:

    @pytest.mark.asyncio
    async def test_add_favorite_happy_path(self, async_client, auth_headers, active_property):
        """Usuario autenticado agrega propiedad activa a favoritos → 201."""
        prop_id = active_property["id"]
        resp = await async_client.post(f"/favorites/{prop_id}", headers=auth_headers)

        assert resp.status_code == 201
        assert "detail" in resp.json()

    @pytest.mark.asyncio
    async def test_add_favorite_nonexistent_property_returns_404(self, async_client, auth_headers):
        """Propiedad inexistente retorna 404."""
        resp = await async_client.post(f"/favorites/{uuid.uuid4()}", headers=auth_headers)

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_add_favorite_without_auth_returns_403(self, async_client, active_property):
        """Sin token retorna 403."""
        prop_id = active_property["id"]
        resp = await async_client.post(f"/favorites/{prop_id}")

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_add_favorite_duplicate_returns_409(self, async_client, auth_headers, active_property):
        """Agregar la misma propiedad dos veces retorna 409."""
        prop_id = active_property["id"]

        first = await async_client.post(f"/favorites/{prop_id}", headers=auth_headers)
        assert first.status_code == 201

        second = await async_client.post(f"/favorites/{prop_id}", headers=auth_headers)
        assert second.status_code == 409


# ── DELETE /favorites/{property_id} ───────────────────────────────

class TestRemoveFavorite:

    @pytest.mark.asyncio
    async def test_remove_favorite_happy_path(self, async_client, auth_headers, active_property):
        """Usuario elimina favorito existente → 204."""
        prop_id = active_property["id"]

        await async_client.post(f"/favorites/{prop_id}", headers=auth_headers)
        resp = await async_client.delete(f"/favorites/{prop_id}", headers=auth_headers)

        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_remove_favorite_not_in_list_returns_404(self, async_client, auth_headers, active_property):
        """Eliminar favorito que no existe retorna 404."""
        prop_id = active_property["id"]
        resp = await async_client.delete(f"/favorites/{prop_id}", headers=auth_headers)

        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_favorite_without_auth_returns_403(self, async_client, active_property):
        """Sin token retorna 403."""
        prop_id = active_property["id"]
        resp = await async_client.delete(f"/favorites/{prop_id}")

        assert resp.status_code == 403


# ── GET /favorites ────────────────────────────────────────────────

class TestListFavorites:

    @pytest.mark.asyncio
    async def test_list_favorites_authenticated(self, async_client, auth_headers, active_property):
        """Usuario autenticado obtiene su lista de favoritos."""
        prop_id = active_property["id"]
        await async_client.post(f"/favorites/{prop_id}", headers=auth_headers)

        resp = await async_client.get("/favorites", headers=auth_headers)

        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert any(item["id"] == prop_id for item in body)

    @pytest.mark.asyncio
    async def test_list_favorites_empty_for_new_user(self, async_client, second_user_headers):
        """Nuevo usuario sin favoritos recibe lista vacía."""
        resp = await async_client.get("/favorites", headers=second_user_headers)

        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_list_favorites_without_auth_returns_403(self, async_client):
        """Sin token retorna 403."""
        resp = await async_client.get("/favorites")

        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_list_favorites_isolated_between_users(
        self, async_client, auth_headers, second_user_headers, active_property
    ):
        """Favoritos de un usuario no aparecen en la lista de otro."""
        prop_id = active_property["id"]

        # auth_headers agrega el favorito
        await async_client.post(f"/favorites/{prop_id}", headers=auth_headers)

        # second_user_headers no debe verlo
        resp = await async_client.get("/favorites", headers=second_user_headers)
        assert resp.status_code == 200
        assert resp.json() == []
