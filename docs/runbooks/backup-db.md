# Runbook: Backup de Base de Datos

## Backup manual

```bash
# Dump completo
pg_dump $DATABASE_URL \
  --no-owner \
  --no-acl \
  --format=custom \
  --file=backup_$(date +%Y%m%d_%H%M%S).dump

# Dump solo schema
pg_dump $DATABASE_URL \
  --no-owner \
  --schema-only \
  --file=schema_$(date +%Y%m%d).sql
```

## Restore

```bash
pg_restore \
  --no-owner \
  --no-acl \
  --dbname=$DATABASE_URL \
  backup_20250301_120000.dump
```

## Frecuencia recomendada

| Ambiente | Frecuencia | Retención |
|----------|-----------|-----------|
| Producción | Diario (automático Railway) | 7 días |
| Antes de migración | Siempre | Hasta verificar |

## Notas

- Railway hace backups automáticos diarios en planes pagos
- Antes de cualquier migración en prod, hacer backup manual
