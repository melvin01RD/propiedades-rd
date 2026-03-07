# Arquitectura — propiedades-rd

## Visión general

```
┌─────────────────────────────────────────────────────────┐
│                        Cliente                          │
│              Next.js 14 (Vercel)                        │
│        App Router · TypeScript · Tailwind               │
│              Mapbox GL JS · shadcn/ui                   │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTPS / REST API
┌─────────────────▼───────────────────────────────────────┐
│                      Backend                            │
│             FastAPI (Railway)                           │
│     ┌─────────────┐    ┌─────────────────────┐         │
│     │  API Layer  │    │   Service Layer      │         │
│     │  routes     │───▶│   business logic     │         │
│     │  controllers│    │   property_service   │         │
│     │  schemas    │    │   search_service     │         │
│     │  middleware │    │   valuation_service  │         │
│     └─────────────┘    └──────────┬──────────┘         │
│                                   │                     │
│     ┌─────────────────────────────▼──────────┐         │
│     │          Persistence Layer              │         │
│     │  repositories · models · migrations     │         │
│     └─────────────────────────────────────────┘        │
└──────────┬──────────────────┬──────────────────────────┘
           │                  │
┌──────────▼──────┐  ┌────────▼─────────┐
│  PostgreSQL 16  │  │   Redis           │
│  + PostGIS      │  │   (caché queries) │
│  (Railway)      │  │   (Railway)       │
└─────────────────┘  └──────────────────┘
           │
    ┌──────▼──────────────────────┐
    │  Servicios externos          │
    │  Cloudinary (imágenes)       │
    │  Resend (emails transacc.)   │
    └──────────────────────────────┘
```

---

## Capas del backend

### API Layer (`src/api/`)
Responsabilidad única: traducir HTTP ↔ Python. No contiene lógica de negocio.
- **routes/**: registra los endpoints en el router de FastAPI
- **controllers/**: recibe la request, llama al service, retorna la response
- **schemas/**: Pydantic models para validación de entrada y serialización de salida
- **middleware/**: auth guard, logging, manejo global de errores

### Service Layer (`src/services/`)
Toda la lógica de negocio vive aquí. Los services son stateless y no conocen HTTP.
- Reciben datos ya validados desde los controllers
- Orquestan llamadas a repositories y servicios externos
- Lanzan excepciones de dominio (no HTTPException)

### Persistence Layer (`src/persistence/`)
Acceso a datos únicamente. Nada de lógica de negocio.
- **models/**: SQLAlchemy ORM models (mapeo tabla ↔ clase)
- **repositories/**: queries SQL, nunca expuestos fuera de esta capa
- **migrations/**: Alembic, versionadas y revisadas en PR

---

## Modelo de datos principal

```
users
  id, email, password_hash, role (agent|owner|admin), created_at

properties
  id, title, description, price, currency
  property_type (house|apartment|land|commercial)
  operation_type (sale|rent)
  bedrooms, bathrooms, area_m2
  location GEOMETRY(Point, 4326)   ← PostGIS
  address, city, sector, province
  owner_id → users.id
  status (active|inactive|sold|rented)
  created_at, updated_at

property_images
  id, property_id → properties.id
  cloudinary_url, cloudinary_public_id
  is_cover, sort_order

favorites
  user_id → users.id
  property_id → properties.id
  created_at

alerts
  id, user_id → users.id
  filters JSONB    ← criterios de búsqueda guardados
  is_active, last_triggered_at
```

---

## Decisiones de arquitectura

Ver carpeta `docs/decisions/` para los ADRs completos:
- [ADR-001](decisions/adr-001-database.md) — PostgreSQL + PostGIS
- [ADR-002](decisions/adr-002-auth.md) — JWT Auth
- [ADR-003](decisions/adr-003-storage.md) — Cloudinary
