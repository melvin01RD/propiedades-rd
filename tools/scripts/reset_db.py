"""
Borra y recrea todas las tablas de la DB.
⚠️  DESTRUCTIVO — no usar en producción.
Uso: cd backend && python ../tools/scripts/reset_db.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../backend/.env"))

from src.core.config import get_settings

settings = get_settings()

# Bloquear ejecución en producción
if settings.environment == "production":
    print("❌ Este script no puede ejecutarse en producción.")
    sys.exit(1)


async def reset():
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    engine = create_async_engine(settings.database_url)

    print(f"\n⚠️  Reset de DB en entorno: {settings.environment}")
    confirm = input("¿Estás seguro? Escribe 'si' para continuar: ")
    if confirm.lower() != "si":
        print("Cancelado.")
        await engine.dispose()
        return

    async with engine.begin() as conn:
        print("\n🗑️  Eliminando tablas...")

        # Drop tables en orden correcto (FK)
        await conn.execute(text("DROP TABLE IF EXISTS favorites CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS alerts CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS property_images CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS properties CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS agents CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS owners CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))

        # Drop ENUMs
        await conn.execute(text("DROP TYPE IF EXISTS user_role CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS property_type CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS operation_type CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS currency CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS property_status CASCADE"))

        print("✓ Tablas y ENUMs eliminados")

    print("\n📋 Ahora ejecuta el schema SQL para recrear las tablas:")
    print("   python -c \"...\" (usa el script de apply_schema o psql)")
    print("\n✅ Reset completado.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset())
