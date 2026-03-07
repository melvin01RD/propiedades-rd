# propiedades-rd — CLAUDE.md

## Qué es este proyecto
Plataforma inmobiliaria para el mercado dominicano (estilo Zillow).
Sirve dos propósitos: producto real orientado a RD + proyecto de portafolio serio como backend developer.

**Desarrollador:** Melvin De La Cruz  
**Disponibilidad:** ~12 horas semanales  
**Idioma del código:** inglés | **Comunicación:** español

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI (Python) |
| Base de datos | PostgreSQL + PostGIS |
| Caché | Redis |
| Auth | JWT |
| Imágenes | Cloudinary |
| Emails | Resend |
| Frontend | Next.js 14 + TypeScript + Tailwind |
| Mapas | Mapbox GL JS |
| UI | shadcn/ui |
| Deploy backend | Railway |
| Deploy frontend | Vercel |

---

## Estructura del proyecto

```
propiedades-rd/
├── CLAUDE.md               ← este archivo (contexto global)
├── README.md
├── docs/
│   ├── architecture.md
│   ├── decisions/          ← ADRs (Architecture Decision Records)
│   └── runbooks/           ← procedimientos operacionales
├── .claude/
│   ├── settings.json
│   └── skills/             ← skills locales del proyecto
├── tools/
│   ├── scripts/
│   └── prompts/
├── backend/
│   ├── CLAUDE.md           ← contexto local del backend
│   └── src/
│       ├── api/            ← routes, controllers, schemas, middleware
│       ├── services/       ← lógica de negocio
│       ├── persistence/    ← models, repositories, migrations
│       └── core/           ← config, security
└── frontend/
    └── CLAUDE.md           ← contexto local del frontend
```

---

## Convenciones de trabajo

- **Documentar antes de implementar**: cada entregable importante tiene su doc técnico primero
- **ADRs**: las decisiones de arquitectura van en `docs/decisions/adr-NNN-titulo.md`
- **CLAUDE.md por módulo**: cada subcarpeta principal tiene su propio contexto local
- **Entregas incrementales**: funcional > completo. No dejar features a medias
- **Tests**: el backend tiene cobertura de tests desde el inicio, no al final

---

## Roadmap resumido

| Semana | Foco |
|--------|------|
| 1 | Base: schema DB, auth JWT, CRUD propiedades |
| 2 | Core: búsqueda + filtros, imágenes, geolocalización |
| 3 | Frontend: listado, mapa, detalle, panel agente |
| 4 | Features: estadísticas, favoritos, alertas, admin |
| 5 | Deploy + SEO + docs técnica completa |

---

## Módulos con CLAUDE.md propio
- `backend/CLAUDE.md` — contexto de FastAPI, patrones usados, convenciones
- `frontend/CLAUDE.md` — contexto de Next.js, componentes, convenciones
