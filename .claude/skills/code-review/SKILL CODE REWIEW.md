# Skill: Code Review — propiedades-rd

Cuando se te pida hacer un code review, sigue este proceso completo antes de reportar.

## 1. Imports sin uso y código muerto

Busca en cada archivo revisado:
- Imports que no se referencian en el código
- Variables, funciones o clases definidas pero nunca llamadas
- Bloques comentados que no aportan contexto
- `create_refresh_token` u otras funciones de infraestructura a medias

Reporta: archivo, línea, qué está sin uso y si se puede eliminar de forma segura.

## 2. Seguridad

Revisa los siguientes puntos en orden:

**Auth y JWT:**
- Todo endpoint protegido usa `Depends(get_current_user)`
- El payload del JWT valida `type == "access"` antes de extraer `sub`
- Ningún refresh token puede acceder a recursos protegidos

**Validaciones:**
- Los schemas de entrada (`Create`, `Update`) tienen validaciones mínimas: `min_length`, `gt=0`, `ge=0`
- Passwords tienen mínimo 8 caracteres con `@field_validator`
- Ningún campo acepta strings vacíos donde no tiene sentido

**Autorización:**
- Los endpoints de escritura (`POST`, `PUT`, `DELETE`) verifican que el usuario sea dueño del recurso o admin
- Se usa `_assert_owner` o patrón equivalente antes de modificar
- Ningún usuario puede modificar recursos de otro usuario sin ser admin

**SQL:**
- No hay queries construidas con f-strings o concatenación de strings
- Todos los filtros usan parámetros de SQLAlchemy (`.where(Model.field == value)`)

## 3. Consistencia con patrones del proyecto

**Patrón Repository:**
- Toda consulta a la DB pasa por un repositorio, nunca directo en el router
- Los repositorios son stateless: `db` se recibe como parámetro en cada método
- Existe una instancia singleton al final del archivo (`x_repository = XRepository()`)
- Los repositorios usan `selectinload` para relaciones, nunca lazy loading

**Schemas:**
- Existe `XCreate`, `XUpdate`, `XResponse` para cada entidad
- `XUpdate` tiene todos los campos opcionales (`| None`)
- `XUpdate` usa `model_dump(exclude_unset=True)` en el router para no sobreescribir campos no enviados
- Las respuestas de listado son más ligeras que las de detalle

**Modelos:**
- Timestamps usan `lambda: datetime.now(timezone.utc)`, nunca `datetime.utcnow`
- Nuevos modelos están importados en `src/persistence/models/__init__.py`
- Las relaciones usan `back_populates`, no `backref` (excepto los existentes)

**Estructura de archivos:**
```
src/api/routes/      → routers
src/api/schemas/     → schemas pydantic
src/persistence/models/      → modelos SQLAlchemy
src/persistence/repositories/  → repositorios
src/services/        → lógica de negocio compleja
```

## Formato del reporte

Organiza el reporte en tres secciones con severidad:

🔴 CRÍTICO — rompe en runtime o es vulnerabilidad de seguridad
🟠 MEDIO — falla cuando se usa o viola un patrón core
🟡 BAJO — inconsistencia menor, lint, código muerto

Para cada issue incluye:
- Archivo y línea
- Qué está mal
- Cómo corregirlo (con ejemplo de código si aplica)

Al final incluye un resumen con conteo por severidad y si el código está listo para merge o no.
