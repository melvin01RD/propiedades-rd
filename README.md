# propiedades-rd

Plataforma inmobiliaria para la República Dominicana. Busca, publica y compara propiedades en venta y alquiler con mapa interactivo y estadísticas de mercado por sector.

---

## Stack

- **Backend:** FastAPI · PostgreSQL + PostGIS · Redis · JWT
- **Frontend:** Next.js 14 · TypeScript · Tailwind · Mapbox GL JS
- **Infraestructura:** Railway · Vercel · Cloudinary · Resend

## Estructura del repositorio

```
propiedades-rd/
├── backend/    # API FastAPI
├── frontend/   # Next.js 14
├── docs/       # Documentación técnica y ADRs
└── tools/      # Scripts y utilidades
```

## Desarrollo local

### Requisitos
- Python 3.12+
- Node.js 20+
- PostgreSQL 16 + PostGIS
- Redis

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

## Documentación

- [Arquitectura](docs/architecture.md)
- [Decisiones técnicas (ADRs)](docs/decisions/)
- [Deploy](docs/runbooks/deploy.md)

## Autor

**Melvin De La Cruz** — QA Engineer / Backend Developer
