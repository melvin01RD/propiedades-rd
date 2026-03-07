import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from src.persistence.models.user import User, UserRole


# ── Fixtures de usuario ───────────────────────────────────────────

@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def mock_user(user_id):
    user = MagicMock(spec=User)
    user.id = user_id
    user.email = "test@example.com"
    user.password_hash = "$2b$12$CUL3CVmlAMuoO59nSHSWwebvT4Djt1NjylfDdKjeC9N3uUh.Trl62"
    user.role = UserRole.owner
    user.is_active = True
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = datetime.now(timezone.utc)
    return user


@pytest.fixture
def mock_admin_user(user_id):
    user = MagicMock(spec=User)
    user.id = user_id
    user.email = "admin@example.com"
    user.password_hash = "$2b$12$CUL3CVmlAMuoO59nSHSWwebvT4Djt1NjylfDdKjeC9N3uUh.Trl62"
    user.role = UserRole.admin
    user.is_active = True
    return user


# ── Fixture de DB mock ────────────────────────────────────────────

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db
