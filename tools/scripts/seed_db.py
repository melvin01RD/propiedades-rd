"""
Pobla la DB con datos de prueba.
Uso: cd backend && python ../tools/scripts/seed_db.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../backend/.env"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.core.config import get_settings
from src.core.security import hash_password
from src.persistence.models.user import User
from src.persistence.models.agent import Agent
from src.persistence.models.owner import Owner
from src.persistence.models.property import Property, PropertyType, OperationType, Currency, PropertyStatus

settings = get_settings()

engine = create_async_engine(settings.database_url)
AsyncSessionFactory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def clear_data(session: AsyncSession):
    """Limpia datos existentes en orden correcto (FK)"""
    tables = ["favorites", "alerts", "property_images", "properties", "agents", "owners", "users"]
    for table in tables:
        await session.execute(text(f"DELETE FROM {table}"))
    print("✓ Datos anteriores eliminados")


async def seed_users(session: AsyncSession) -> dict:
    """Crea usuarios de prueba"""
    users = {}

    admin = User(
        email="admin@propiedades-rd.dev",
        password_hash=hash_password("Admin123!"),
        role="admin",
        is_active=True,
    )
    session.add(admin)

    agent_user = User(
        email="agente@propiedades-rd.dev",
        password_hash=hash_password("Agent123!"),
        role="agent",
        is_active=True,
    )
    session.add(agent_user)

    owner_user = User(
        email="propietario@propiedades-rd.dev",
        password_hash=hash_password("Owner123!"),
        role="owner",
        is_active=True,
    )
    session.add(owner_user)

    await session.flush()
    users["admin"] = admin
    users["agent_user"] = agent_user
    users["owner_user"] = owner_user
    print(f"✓ {len(users)} usuarios creados")
    return users


async def seed_agents(session: AsyncSession, users: dict) -> dict:
    """Crea perfiles de agentes"""
    agents = {}

    agent = Agent(
        user_id=users["agent_user"].id,
        first_name="Carlos",
        last_name="Méndez",
        phone="+1-809-555-0101",
        license_number="LIC-2024-001",
        agency_name="Propiedades Premium RD",
    )
    session.add(agent)
    await session.flush()
    agents["carlos"] = agent
    print(f"✓ {len(agents)} agentes creados")
    return agents


async def seed_owners(session: AsyncSession, users: dict) -> dict:
    """Crea perfiles de propietarios"""
    owners = {}

    owner = Owner(
        user_id=users["owner_user"].id,
        first_name="María",
        last_name="González",
        phone="+1-809-555-0202",
    )
    session.add(owner)
    await session.flush()
    owners["maria"] = owner
    print(f"✓ {len(owners)} propietarios creados")
    return owners


async def seed_properties(session: AsyncSession, agents: dict, owners: dict):
    """Crea propiedades de prueba"""
    properties_data = [
        {
            "title": "Apartamento moderno en Piantini",
            "description": "Hermoso apartamento de 3 habitaciones en el corazón de Piantini con vista al mar.",
            "property_type": PropertyType.apartment,
            "operation_type": OperationType.sale,
            "price": 185000.00,
            "currency": Currency.USD,
            "bedrooms": 3,
            "bathrooms": 2,
            "area_m2": 145.0,
            "address": "Calle El Recodo 45, Piantini",
            "province": "Distrito Nacional",
            "city": "Santo Domingo",
            "sector": "Piantini",
            "status": PropertyStatus.active,
            "agent_id": agents["carlos"].id,
        },
        {
            "title": "Villa en Casa de Campo",
            "description": "Espectacular villa con piscina privada y campo de golf en Casa de Campo.",
            "property_type": PropertyType.villa,
            "operation_type": OperationType.rent,
            "price": 5500.00,
            "currency": Currency.USD,
            "bedrooms": 5,
            "bathrooms": 4,
            "area_m2": 420.0,
            "address": "Casa de Campo, Bloque 12",
            "province": "La Romana",
            "city": "La Romana",
            "sector": "Casa de Campo",
            "status": PropertyStatus.active,
            "owner_id": owners["maria"].id,
        },
        {
            "title": "Local comercial en Naco",
            "description": "Local comercial de 80m² en zona de alta afluencia en Naco.",
            "property_type": PropertyType.commercial,
            "operation_type": OperationType.rent,
            "price": 45000.00,
            "currency": Currency.DOP,
            "bedrooms": 0,
            "bathrooms": 1,
            "area_m2": 80.0,
            "address": "Av. Tiradentes 32, Naco",
            "province": "Distrito Nacional",
            "city": "Santo Domingo",
            "sector": "Naco",
            "status": PropertyStatus.active,
            "agent_id": agents["carlos"].id,
        },
        {
            "title": "Casa familiar en Los Prados",
            "description": "Casa de 4 habitaciones con jardín y garaje en residencial Los Prados.",
            "property_type": PropertyType.house,
            "operation_type": OperationType.sale,
            "price": 9500000.00,
            "currency": Currency.DOP,
            "bedrooms": 4,
            "bathrooms": 3,
            "area_m2": 280.0,
            "address": "Calle Los Prados 18",
            "province": "Distrito Nacional",
            "city": "Santo Domingo",
            "sector": "Los Prados",
            "status": PropertyStatus.active,
            "owner_id": owners["maria"].id,
        },
    ]

    for data in properties_data:
        prop = Property(**data)
        session.add(prop)

    await session.flush()
    print(f"✓ {len(properties_data)} propiedades creadas")


async def main():
    print("\n🌱 Iniciando seed de la base de datos...\n")
    async with AsyncSessionFactory() as session:
        async with session.begin():
            await clear_data(session)
            users = await seed_users(session)
            agents = await seed_agents(session, users)
            owners = await seed_owners(session, users)
            await seed_properties(session, agents, owners)

    print("\n✅ Seed completado exitosamente!")
    print("\nCredenciales de prueba:")
    print("  Admin:       admin@propiedades-rd.dev / Admin123!")
    print("  Agente:      agente@propiedades-rd.dev / Agent123!")
    print("  Propietario: propietario@propiedades-rd.dev / Owner123!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
