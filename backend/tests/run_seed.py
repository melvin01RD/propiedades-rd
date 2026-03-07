"""
Script de seed: provincias, sectores y amenidades.

Uso:
    python -m src.persistence.seeds.run_seed
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from src.core.database import async_session_factory
from src.persistence.models import Province, Sector, Amenity
from src.persistence.seeds.seed_provinces import PROVINCES_SEED, SECTORS_SEED
from src.persistence.seeds.seed_amenities import AMENITIES_SEED


async def seed_provinces(session: AsyncSession) -> None:
    stmt = insert(Province).values(PROVINCES_SEED)
    stmt = stmt.on_conflict_do_nothing(index_elements=["code"])
    await session.execute(stmt)
    print(f"  ✅ {len(PROVINCES_SEED)} provincias insertadas (o ya existían)")


async def seed_sectors(session: AsyncSession) -> None:
    stmt = insert(Sector).values(SECTORS_SEED)
    stmt = stmt.on_conflict_do_nothing(constraint="uq_sector_name_province")
    await session.execute(stmt)
    print(f"  ✅ {len(SECTORS_SEED)} sectores insertados (o ya existían)")


async def seed_amenities(session: AsyncSession) -> None:
    stmt = insert(Amenity).values(AMENITIES_SEED)
    stmt = stmt.on_conflict_do_nothing(index_elements=["slug"])
    await session.execute(stmt)
    print(f"  ✅ {len(AMENITIES_SEED)} amenidades insertadas (o ya existían)")


async def run_all() -> None:
    print("🌱 Iniciando seed de catálogos...")
    async with async_session_factory() as session:
        async with session.begin():
            await seed_provinces(session)
            await seed_sectors(session)
            await seed_amenities(session)
    print("🎉 Seed completado.")


if __name__ == "__main__":
    asyncio.run(run_all())
