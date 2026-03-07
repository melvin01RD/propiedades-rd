# ADR-001: PostgreSQL + PostGIS como base de datos principal

**Estado:** Aceptado  
**Fecha:** 2025-03  
**Autor:** Melvin De La Cruz

---

## Contexto

La plataforma necesita almacenar propiedades inmobiliarias con coordenadas geográficas y soportar búsquedas por proximidad (ej. "propiedades en un radio de 5km de Santo Domingo centro"). También requiere queries complejas con múltiples filtros combinados.

## Decisión

Usar **PostgreSQL 16 con la extensión PostGIS** como base de datos principal.

## Alternativas consideradas

| Opción | Pros | Contras |
|--------|------|---------|
| PostgreSQL + PostGIS | Queries geo nativas, ACID, madurez | Más complejo de operar |
| MongoDB | Geo índices, flexibilidad de schema | Sin relaciones fuertes, menos garantías |
| MySQL | Simple, conocido | Soporte geo inferior |
| Supabase | Managed + PostGIS incluido | Vendor lock-in, costo a escala |

## Justificación

- PostGIS es el estándar de facto para datos geoespaciales en SQL
- Las propiedades tienen relaciones con agentes, usuarios, favoritos — se benefician de FK y transacciones
- Railway soporta PostgreSQL + PostGIS sin configuración adicional
- El equipo (Melvin) ya conoce SQL; no hay curva adicional

## Consecuencias

- **Positivas:** queries geo potentes (`ST_DWithin`, `ST_Distance`), integridad referencial, migraciones con Alembic
- **Negativas:** PostGIS requiere habilitar la extensión en el servidor (`CREATE EXTENSION postgis`), ligera complejidad operacional
- **Acción requerida:** el script de setup debe incluir `CREATE EXTENSION IF NOT EXISTS postgis;`
