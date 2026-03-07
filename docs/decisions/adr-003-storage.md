# ADR-003: Cloudinary para almacenamiento y optimización de imágenes

**Estado:** Aceptado  
**Fecha:** 2025-03  
**Autor:** Melvin De La Cruz

---

## Contexto

Las propiedades tienen múltiples imágenes (hasta 20 por listing). Necesitamos subida, transformación (resize, webp, thumbnails) y entrega optimizada por CDN.

## Decisión

Usar **Cloudinary** como plataforma de gestión de imágenes.

## Alternativas consideradas

| Opción | Pros | Contras |
|--------|------|---------|
| Cloudinary | Transformaciones on-the-fly, CDN, free tier generoso | Vendor lock-in |
| AWS S3 + CloudFront | Control total, escalable | Costo y complejidad de setup |
| Supabase Storage | Simple, integrado | Sin transformaciones automáticas |
| Self-hosted (MinIO) | Control total | Operación compleja para un dev solo |

## Justificación

- Free tier suficiente para MVP (25GB storage, 25GB bandwidth/mes)
- Transformaciones via URL sin procesamiento en el servidor
- SDK oficial para Python bien mantenido
- CDN global incluido — importante para velocidad desde RD

## Flujo de subida

```
Cliente → Backend (valida + genera upload signature) → Cloudinary (upload directo)
                                                      ↓
                                              Backend guarda URL en DB
```

## Consecuencias

- **Positivas:** cero operación de storage, thumbnails automáticos, CDN global
- **Negativas:** si Cloudinary tiene downtime, las imágenes no cargan
- **Acción requerida:** configurar carpetas por entorno (propiedades-rd/dev/, propiedades-rd/prod/)
