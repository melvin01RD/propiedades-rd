# Runbook: Deploy

## Backend (Railway)

### Primera vez
1. Crear proyecto en Railway
2. Agregar servicio PostgreSQL → habilitar PostGIS: `CREATE EXTENSION IF NOT EXISTS postgis;`
3. Agregar servicio Redis
4. Conectar el repo de GitHub al servicio de backend
5. Configurar variables de entorno (ver `.env.example`)

### Variables requeridas en Railway
```
DATABASE_URL          # Railway lo provee automáticamente
REDIS_URL             # Railway lo provee automáticamente
SECRET_KEY            # generar con: openssl rand -hex 32
CLOUDINARY_URL        # desde dashboard de Cloudinary
RESEND_API_KEY        # desde dashboard de Resend
ENVIRONMENT           # production
ALLOWED_ORIGINS       # https://propiedades-rd.vercel.app
```

### Deploy continuo
Push a `main` → Railway hace deploy automático.

```bash
# Ver logs
railway logs

# Correr migraciones en prod
railway run alembic upgrade head
```

## Rollback

```bash
railway deployments
railway rollback
```

## Verificación post-deploy

```bash
curl https://api.propiedades-rd.railway.app/health
```
