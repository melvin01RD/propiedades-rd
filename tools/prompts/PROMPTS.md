# Prompts reutilizables — propiedades-rd

Copia y pega el prompt que necesites en Claude Code.

---

## 🔍 Code Review

```
Haz un code review del archivo [ARCHIVO] usando el skill en .claude/skills/code-review/SKILL.md.
Reporta todos los issues encontrados organizados por severidad.
```

---

## 🏗️ Crear endpoint nuevo

```
Crea un endpoint [MÉTODO] [RUTA] para [DESCRIPCIÓN].

Sigue la arquitectura del proyecto:
1. Schema en src/api/schemas/[nombre]_schemas.py
2. Repositorio en src/persistence/repositories/[nombre]_repository.py (si no existe)
3. Service en src/services/[nombre]_service.py
4. Router en src/api/routes/[nombre]_router.py
5. Registrar el router en main.py

Al terminar verifica que el servidor arranca.
```

---

## 🗄️ Crear modelo nuevo

```
Crea un modelo SQLAlchemy para [ENTIDAD] con estos campos:
[LISTA DE CAMPOS]

Sigue los patrones del proyecto:
1. Archivo en src/persistence/models/[nombre].py
2. Timestamps con lambda: datetime.now(timezone.utc)
3. UUID como primary key
4. Agregar al src/persistence/models/__init__.py
5. Generar migración: alembic revision --autogenerate -m "[descripcion]"
6. Aplicar: alembic upgrade head
```

---

## 🧪 Crear tests

```
Crea tests para [MÓDULO/ENDPOINT] en backend/tests/.

Incluye:
- Tests unitarios en backend/tests/unit/
- Tests de integración en backend/tests/integration/

Cubre los casos:
1. Happy path
2. Validaciones de entrada inválida
3. Autorización (sin token, token inválido, acceso denegado)
4. Casos borde (not found, duplicados, etc.)

Usa pytest + pytest-asyncio + httpx.
```

---

## ♻️ Refactor

```
Refactoriza [ARCHIVO o MÓDULO] usando el skill en .claude/skills/refactor/SKILL.md.

Enfócate en:
- [estandarizar nombres / eliminar duplicación / mejorar legibilidad]

No cambies el comportamiento, solo la estructura.
Al terminar verifica que el servidor arranca.
```

---

## 🚀 Release

```
Haz un release siguiendo el skill en .claude/skills/release/SKILL.md.
El tipo de cambio es [patch / minor / major].
```

---

## 🐛 Debug

```
El endpoint [MÉTODO] [RUTA] está fallando con este error:
[PEGAR ERROR]

Revisa el router, service y repositorio correspondiente.
Identifica la causa raíz y corrígela.
Al terminar verifica que el servidor arranca y el endpoint responde correctamente.
```

---

## 📊 Estado del proyecto

```
Revisa el proyecto completo y dame:
1. Lista de endpoints activos con sus rutas
2. Modelos existentes en la DB
3. Migraciones aplicadas (alembic history)
4. Archivos sin usar o huérfanos
5. Porcentaje estimado de completitud por módulo
```
