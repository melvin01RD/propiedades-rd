# Hooks — propiedades-rd

## Post-edit: modelos modificados → migraciones

Cuando edites o crees cualquier archivo dentro de:
- `src/persistence/models/`

Al terminar, recuérdale al usuario:

---
⚠️ **Modificaste un modelo SQLAlchemy.**

Si agregaste, eliminaste o cambiaste columnas, relaciones o constraints, necesitas generar una migración:

```powershell
cd backend
alembic revision --autogenerate -m "descripcion_del_cambio"
alembic upgrade head
```

Revisa el archivo generado en `src/persistence/migrations/versions/` antes de aplicarlo — el autogenerate no detecta todo (renombrados, cambios de tipo en algunos casos).

---

## Post-edit: modelo nuevo → __init__.py

Cuando crees un archivo nuevo dentro de:
- `src/persistence/models/`

Al terminar, recuérdale al usuario:

---
⚠️ **Creaste un modelo nuevo.**

Agrégalo al `src/persistence/models/__init__.py` para que Alembic y el resto del proyecto lo detecten:

```python
from src.persistence.models.nuevo_modelo import NuevoModelo

__all__ = [
    ...,
    "NuevoModelo",
]
```

Sin este paso, Alembic no generará la migración correctamente.

---
