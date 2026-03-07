# Skill: Refactor — propiedades-rd

Cuando se te pida refactorizar código, sigue este proceso. Nunca cambies comportamiento, solo estructura.

## Regla principal

> Un refactor no cambia lo que hace el código, solo cómo está escrito.

Antes de tocar cualquier archivo, confirma:
1. Entiendes qué hace el código actualmente
2. Tienes claro qué problema de estructura estás resolviendo
3. El comportamiento será idéntico antes y después

## 1. Estandarizar nombres y convenciones

**Archivos y módulos:**
- Archivos en `snake_case`: `property_router.py`, `user_repository.py`
- Clases en `PascalCase`: `PropertyRepository`, `UserRole`
- Variables y funciones en `snake_case`: `get_current_user`, `property_id`
- Constantes en `UPPER_SNAKE_CASE`: `MAX_UPLOAD_SIZE`

**Nombres descriptivos:**
- Evitar nombres de una letra excepto en loops simples (`i`, `k`)
- Evitar abreviaciones ambiguas: `prop` es aceptable para `Property`, `usr` no lo es para `User`
- Funciones deben describir lo que hacen: `get_by_id`, `create_property`, `soft_delete`

**Consistencia en endpoints:**
- Parámetros de ruta: `property_id`, `province_id`, `user_id` (nunca `id` solo)
- Respuestas de error con `detail` en español: `"Propiedad no encontrada"`
- Status codes consistentes: `201` para create, `204` para delete, `200` para el resto

## 2. Eliminar duplicación de código

Identifica y extrae:

**Helpers repetidos en routers:**
```python
# Si esto aparece más de una vez, extráelo como helper
prop = await repository.get_by_id(db, id)
if not prop:
    raise HTTPException(status_code=404, detail="...")
```

**Validaciones repetidas en schemas:**
- Si el mismo `@field_validator` aparece en `XCreate` y `XUpdate`, moverlo a una clase base

**Queries similares en repositorios:**
- Si dos métodos construyen la misma base de query, extraer `_base_query()`

## 3. Mejorar legibilidad y estructura

**Funciones largas:**
- Si una función tiene más de 40 líneas, evalúa si puede dividirse
- Cada función debe hacer una sola cosa (Single Responsibility)
- Los helpers privados van al final de la clase, prefijados con `_`

**Comentarios:**
- Los comentarios explican el "por qué", no el "qué"
- Elimina comentarios que solo repiten el código:
  ```python
  # MAL: incrementa el contador
  counter += 1
  
  # BIEN: compensamos el offset base 0 del paginador
  counter += 1
  ```
- Los docstrings de módulo y clase son bienvenidos

**Estructura de routers:**
El orden estándar dentro de un router es:
1. Imports
2. `router = APIRouter(...)`
3. Helpers privados (`_get_x_or_404`, `_assert_owner`)
4. Endpoints en orden: GET list → GET single → POST → PUT → DELETE

**Estructura de repositorios:**
1. Imports
2. Dataclasses de filtros
3. Dataclasses de resultado (Page)
4. Clase repositorio:
   - Constantes de clase (`_EAGER`)
   - Métodos de lectura
   - Métodos de escritura
   - Helpers privados
5. Instancia singleton

## Proceso de entrega

1. Lista los cambios que vas a hacer antes de hacerlos
2. Agrupa los cambios por archivo
3. Después de cada archivo modificado, verifica que el servidor arranca: `python -c "from src.main import app; print('OK')"`
4. Reporta qué cambiaste y por qué en cada caso
