# Skill: Release — propiedades-rd

Cuando se te pida hacer un release, sigue este proceso completo en orden. No saltes pasos.

## 1. Verificación previa

Antes de crear el tag, verifica que el proyecto está en condiciones de release:

```powershell
# 1. Sin cambios sin commitear
git status

# 2. El servidor arranca sin errores
python -c "from src.main import app; print('OK')"

# 3. Alembic sincronizado
alembic check
```

Si cualquiera de estos falla, detente y reporta el problema antes de continuar.

## 2. Determinar la versión

Usa versionado semántico: `vMAJOR.MINOR.PATCH`

- **PATCH** (v0.2.0 → v0.2.1): bug fixes, ajustes menores, limpieza
- **MINOR** (v0.2.0 → v0.3.0): nueva funcionalidad, nuevos endpoints, nuevos modelos
- **MAJOR** (v0.2.0 → v1.0.0): cambios que rompen compatibilidad, rediseño de API

Pregunta al usuario qué tipo de cambio es si no está claro.

## 3. Actualizar versión en el código

Actualiza la versión en `main.py`:
```python
app = FastAPI(
    version="X.Y.Z",  # ← nueva versión
    ...
)
```

## 4. Generar el changelog

Lee los commits desde el último tag hasta HEAD:
```powershell
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

Organiza los commits en estas categorías y redáctalos en español:

```markdown
## vX.Y.Z — DD/MM/YYYY

### ✨ Nuevas funcionalidades
- ...

### 🐛 Correcciones
- ...

### ♻️ Refactors
- ...

### 🧹 Limpieza
- ...
```

Agrega la entrada al inicio de `CHANGELOG.md`. Si el archivo no existe, créalo.

## 5. Commit del release

```powershell
git add .
git commit -m "chore: release vX.Y.Z"
```

## 6. Crear el tag

```powershell
git tag -a vX.Y.Z -m "release vX.Y.Z — resumen de los cambios principales"
git push
git push origin vX.Y.Z
```

## 7. Confirmación final

Reporta:
- Versión creada
- Número de commits incluidos
- Link al tag en GitHub: `https://github.com/melvin01RD/propiedades-rd/releases/tag/vX.Y.Z`
