# ADR-002: JWT para autenticación

**Estado:** Aceptado  
**Fecha:** 2025-03  
**Autor:** Melvin De La Cruz

---

## Contexto

La plataforma necesita autenticar usuarios (agentes, propietarios, admins) con sesiones que persistan entre requests. El frontend en Vercel y el backend en Railway son dominios distintos.

## Decisión

Usar **JWT (JSON Web Tokens)** con access token de corta duración + refresh token almacenado en cookie HttpOnly.

| Token | TTL | Almacenamiento |
|-------|-----|----------------|
| Access token | 15 minutos | Memory / Authorization header |
| Refresh token | 7 días | Cookie HttpOnly + Secure |

## Alternativas consideradas

- **Sessions en Redis**: más control de revocación, pero agrega estado al backend y complejidad
- **Auth0 / Clerk**: soluciones managed, reducen trabajo pero agregan costo y dependencia externa
- **JWT stateless puro (sin refresh)**: más simple, pero tokens de larga duración son un riesgo de seguridad

## Justificación

- Sin estado en el servidor para access tokens → escala horizontalmente
- Refresh token en HttpOnly cookie → no accesible desde JS, mitiga XSS
- Librería `python-jose` + `passlib` son maduras y bien documentadas para FastAPI
- Compatible con el patrón de `Depends()` de FastAPI para inyectar el usuario autenticado

## Consecuencias

- **Positivas:** stateless, cross-domain friendly (CORS), patrón estándar conocido
- **Negativas:** revocación inmediata de tokens no es trivial
- **Acción futura:** si se necesita logout inmediato global, agregar blacklist de JTI en Redis
