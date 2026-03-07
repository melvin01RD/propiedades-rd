import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

# Cargar .env desde backend/
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

# Alembic Config
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importar Base y todos los modelos para autogenerate
from src.core.database import Base
import src.persistence.models  # noqa: F401 — registra todos los modelos en Base.metadata

target_metadata = Base.metadata

# Tablas gestionadas fuera de Alembic (PostGIS, esquemas externos)
_EXCLUDED_TABLES = {"spatial_ref_sys"}

# Índices creados por 001_initial_schema.sql (aplicado manualmente antes de Alembic).
# Existen en la DB pero no están declarados en los modelos, así que Alembic los
# detectaría como "sobrantes" y querría eliminarlos. Los excluimos del autogenerate.
_EXCLUDED_INDEXES = {
    "idx_alerts_user_active",
    "idx_properties_agent",
    "idx_properties_operation",
    "idx_properties_operation_type",
    "idx_properties_owner",
    "idx_properties_price",
    "idx_properties_property_type",
    "idx_properties_province_id",
    "idx_properties_sector_id",
    "idx_properties_status",
    "idx_properties_type",
    "idx_property_images_property",
    "idx_sectors_province_id",
}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in _EXCLUDED_TABLES:
        return False
    if type_ == "index" and name in _EXCLUDED_INDEXES:
        return False
    return True


def get_url() -> str:
    url = os.getenv("DATABASE_URL", "")
    # asyncpg es el driver correcto para async
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(get_url(), poolclass=pool.NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
