# backend — CLAUDE.md

## Contexto local
API REST construida con FastAPI. Maneja autenticación, CRUD de propiedades, búsqueda geoespacial y lógica de negocio de la plataforma.

---

## Estructura

```
backend/
├── src/
│   ├── main.py                     ← punto de entrada FastAPI
│   ├── api/
│   │   ├── routes/                 ← definición de endpoints (routers)
│   │   ├── controllers/            ← lógica de cada endpoint
│   │   ├── schemas/                ← Pydantic models (request/response)
│   │   └── middleware/             ← auth, logging, error handling
│   ├── services/
│   │   ├── property_service.py     ← lógica de negocio de propiedades
│   │   ├── search_service.py       ← búsqueda con filtros + PostGIS
│   │   └── valuation_service.py    ← estadísticas de mercado
│   ├── persistence/
│   │   ├── models/                 ← SQLAlchemy ORM models
│   │   ├── repositories/           ← acceso a datos (patrón Repository)
│   │   └── migrations/             ← Alembic migrations
│   └── core/
│       ├── config.py               ← settings via pydantic-settings
│       └── security.py             ← JWT, hashing, dependencias de auth
└── tests/
    ├── unit/
    ├── integration/
    └── conftest.py
```

---

## Patrones y convenciones

- **Patrón Repository**: los controllers nunca acceden a la DB directamente
- **Schemas separados**: `CreateSchema`, `UpdateSchema`, `ResponseSchema` por recurso
- **Dependency Injection**: auth y DB session se inyectan vía `Depends()`
- **Services stateless**: los services reciben el repo como parámetro
- **Migraciones con Alembic**: nunca modificar la DB directamente en prod

## Convenciones de nombres

| Tipo | Convención | Ejemplo |
|------|-----------|---------|
| Router | `noun_router.py` | `properties_router.py` |
| Controller | `noun_controller.py` | `properties_controller.py` |
| Schema | `NounCreateSchema` | `PropertyCreateSchema` |
| Model | `NounModel` | `PropertyModel` |
| Repository | `NounRepository` | `PropertyRepository` |
| Service | `NounService` | `PropertyService` |

## Variables de entorno requeridas

```
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
SECRET_KEY=...
CLOUDINARY_URL=cloudinary://...
RESEND_API_KEY=...
```

## Comandos frecuentes

```bash
# Levantar dev
uvicorn src.main:app --reload

# Crear migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Tests
pytest tests/ -v

# Cobertura
pytest tests/ --cov=src --cov-report=html
```
