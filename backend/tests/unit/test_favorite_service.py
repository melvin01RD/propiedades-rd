import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from src.services.favorite_service import FavoriteService
from src.persistence.models.property import PropertyStatus


# ── Helpers ───────────────────────────────────────────────────────

def make_active_property():
    prop = MagicMock()
    prop.id = uuid.uuid4()
    prop.status = PropertyStatus.active
    return prop


def make_inactive_property():
    prop = MagicMock()
    prop.id = uuid.uuid4()
    prop.status = PropertyStatus.inactive
    return prop


def make_favorite(user_id, property_id):
    fav = MagicMock()
    fav.user_id = user_id
    fav.property_id = property_id
    fav.property = MagicMock()
    return fav


# ── Tests: add ────────────────────────────────────────────────────

class TestAdd:

    @pytest.mark.asyncio
    async def test_add_happy_path(self, mock_db, mock_user):
        """Propiedad activa no duplicada se agrega correctamente."""
        prop = make_active_property()
        fav = make_favorite(mock_user.id, prop.id)

        with patch("src.services.favorite_service.property_repository") as mock_prop_repo, \
             patch("src.services.favorite_service.favorite_repository") as mock_fav_repo:

            mock_prop_repo.get_by_id = AsyncMock(return_value=prop)
            mock_fav_repo.exists = AsyncMock(return_value=False)
            mock_fav_repo.add = AsyncMock(return_value=fav)

            service = FavoriteService()
            result = await service.add(mock_db, mock_user.id, prop.id)

            assert result == fav
            mock_fav_repo.add.assert_awaited_once_with(mock_db, mock_user.id, prop.id)

    @pytest.mark.asyncio
    async def test_add_property_not_found_raises_404(self, mock_db, mock_user):
        """Propiedad inexistente lanza 404."""
        with patch("src.services.favorite_service.property_repository") as mock_prop_repo:
            mock_prop_repo.get_by_id = AsyncMock(return_value=None)

            service = FavoriteService()
            with pytest.raises(HTTPException) as exc:
                await service.add(mock_db, mock_user.id, uuid.uuid4())

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_add_inactive_property_raises_404(self, mock_db, mock_user):
        """Propiedad inactiva lanza 404 (no se puede guardar como favorito)."""
        prop = make_inactive_property()

        with patch("src.services.favorite_service.property_repository") as mock_prop_repo:
            mock_prop_repo.get_by_id = AsyncMock(return_value=prop)

            service = FavoriteService()
            with pytest.raises(HTTPException) as exc:
                await service.add(mock_db, mock_user.id, prop.id)

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_add_duplicate_raises_409(self, mock_db, mock_user):
        """Favorito ya existente lanza 409 Conflict."""
        prop = make_active_property()

        with patch("src.services.favorite_service.property_repository") as mock_prop_repo, \
             patch("src.services.favorite_service.favorite_repository") as mock_fav_repo:

            mock_prop_repo.get_by_id = AsyncMock(return_value=prop)
            mock_fav_repo.exists = AsyncMock(return_value=True)

            service = FavoriteService()
            with pytest.raises(HTTPException) as exc:
                await service.add(mock_db, mock_user.id, prop.id)

            assert exc.value.status_code == 409


# ── Tests: remove ─────────────────────────────────────────────────

class TestRemove:

    @pytest.mark.asyncio
    async def test_remove_not_in_favorites_raises_404(self, mock_db, mock_user):
        """Quitar favorito que no existe lanza 404."""
        with patch("src.services.favorite_service.favorite_repository") as mock_fav_repo:
            mock_fav_repo.remove = AsyncMock(return_value=False)

            service = FavoriteService()
            with pytest.raises(HTTPException) as exc:
                await service.remove(mock_db, mock_user.id, uuid.uuid4())

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_happy_path(self, mock_db, mock_user):
        """Favorito existente se elimina sin error."""
        with patch("src.services.favorite_service.favorite_repository") as mock_fav_repo:
            mock_fav_repo.remove = AsyncMock(return_value=True)

            service = FavoriteService()
            await service.remove(mock_db, mock_user.id, uuid.uuid4())

            mock_fav_repo.remove.assert_awaited_once()


# ── Tests: get_my_favorites ───────────────────────────────────────

class TestGetMyFavorites:

    @pytest.mark.asyncio
    async def test_get_my_favorites_returns_list(self, mock_db, mock_user):
        """Retorna lista de PropertyListItem mapeada desde los favoritos del usuario."""
        prop_id = uuid.uuid4()
        fav = make_favorite(mock_user.id, prop_id)
        mock_item = MagicMock()

        with patch("src.services.favorite_service.favorite_repository") as mock_fav_repo, \
             patch("src.services.favorite_service.PropertyListItem") as mock_schema:

            mock_fav_repo.get_by_user = AsyncMock(return_value=[fav])
            mock_schema.from_property = MagicMock(return_value=mock_item)

            service = FavoriteService()
            result = await service.get_my_favorites(mock_db, mock_user.id)

            assert result == [mock_item]
            mock_schema.from_property.assert_called_once_with(fav.property)

    @pytest.mark.asyncio
    async def test_get_my_favorites_empty(self, mock_db, mock_user):
        """Usuario sin favoritos retorna lista vacía."""
        with patch("src.services.favorite_service.favorite_repository") as mock_fav_repo:
            mock_fav_repo.get_by_user = AsyncMock(return_value=[])

            service = FavoriteService()
            result = await service.get_my_favorites(mock_db, mock_user.id)

            assert result == []
