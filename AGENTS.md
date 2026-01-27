# AGENTS.md

Este archivo consolida las reglas de comportamiento y workflows para agentes que trabajan en este repositorio.

---

## 🎯 Reglas de Código (Aplicación Continua)

Las siguientes reglas **DEBEN** aplicarse en todo momento al trabajar con código:

### Principios de Arquitectura y Diseño

1. **Principios SOLID**: Aplicar Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation y Dependency Inversion.

2. **Arquitectura DDD y TDD**: Seguir Domain-Driven Design y Test-Driven Development.

3. **Clean Code**: Código limpio, legible y mantenible.

4. **Don't Repeat Yourself (DRY)**: Evitar duplicación de código.

5. **Keep It Simple (KISS)**: Mantener soluciones simples y directas.

6. **You Ain't Gonna Need It (YAGNI)**: No agregar funcionalidad hasta que sea necesaria.

7. **Modularización**: Buscar la modularización del código en componentes reutilizables.

### Gestión de Dependencias y Entorno

1. **Ejecutar comandos**: Usar siempre `uv` para lanzar ejecuciones.

2. **Agregar dependencias**: Usar `uv add <package>` para dependencias de producción.

3. **Dependencias de desarrollo**: Usar `uv add --dev <package>` para dependencias de desarrollo (testing, linting, etc.).

### Testing

1. **Tests obligatorios**: Siempre generar tests asociados a las funcionalidades desarrolladas.

2. **Framework de testing**: Usar siempre `pytest` para la ejecución de tests.

3. **Estructura de tests**: Los tests deben respetar la estructura original de la funcionalidad, distribuidos por archivos siguiendo la organización del proyecto (ver sección Tests más abajo).

### Documentación

1. **Documentación de código**: Al crear una función, generar documentación asociada. Si es una clase, documentar la clase y cada método siguiendo el **estándar de Google Style**.

### Organización de Clases

1. **Un fichero por clase**: Las clases deben tener sus ficheros individuales. No se pueden tener varias clases en el mismo fichero. Los nombres deben estar en formato `snake_case`.

---

## 📋 Reglas de Repositorio

### Documentación y Seguimiento

1. **README**: Actualizar siempre el README.md al añadir funcionalidades nuevas.

2. **Commits**: Generar un commit git al completar una tarea significativa.

### Sincronización de Artefactos

1. **Artefactos internos**: Al crear artefacts internos (tasks, implementation plans), usar el workflow de sincronización (ver `sync-artifacts` más abajo) para mantener un histórico en la carpeta `planning/`.

---

## 🧪 Reglas de Testing

### Estructura de Directorios (Obligatoria)

El proyecto sigue una **estructura híbrida** que separa por tipo de test y espeja la estructura de `src/`:

```
src/
  <nombre_proyecto>/
    ...

tests/
  unit/           # Espeja estructura de src/
  integration/    # Puede espejar o agrupar por funcionalidad
  e2e/            # Flujos completos de negocio
  data/           # Datos estáticos de test
```

### Ejemplo de Estructura

```
src/
  home_assistant_mcp/
    client.py
    server.py
    config.py

tests/
  unit/
    test_client.py
    test_server.py
    test_config.py
  integration/
    test_server.py
  conftest.py
```

### Convenciones de Nombres

1. **Ficheros de test**: Usar el patrón `test_*.py`.
2. **Funciones de test**: Nombrar con prefijo `test_*`.
3. **Relación directa**: `src/myproj/auth/login.py` → `tests/unit/auth/test_login.py`.

### Clasificación de Tests

#### Tests Unitarios (`tests/unit/`)

- Prueban **una unidad lógica pequeña** (función, método, clase).
- **Sin acceso a servicios externos**: No llamadas HTTP, BBDD, colas reales.
- Todas las dependencias externas se **simulan/mokean**.
- Ejemplos: validación, cálculos puros, servicios con repositorios mockeados.

#### Tests de Integración (`tests/integration/`)

- Prueban la **interacción entre múltiples componentes**.
- Usan recursos reales o semi-reales:
  - BBDD de pruebas (local o contenedor)
  - Cola de mensajería de pruebas
  - Servicios HTTP simulados (docker, testcontainers)
- Más lentos que unitarios pero **razonablemente rápidos**.

#### Tests End-to-End (`tests/e2e/`)

- Cubren **flujos completos de negocio**.
- Recorren casi toda la pila: API / UI / BBDD / colas.
- Requieren entorno más pesado (docker-compose, datos cargados).

### Aislamiento y Dependencias

**Tests unitarios**:

- No pueden depender del orden de ejecución.
- No pueden depender de estado compartido.
- No deben realizar I/O real.

**Tests de integración y e2e**:

- Deben dejar el entorno limpio (limpiar BBDD, resetear colas, borrar temporales).
- Se permite I/O controlado.

### Uso de Pytest y Markers

1. **Framework**: Usar `pytest`.

2. **Markers obligatorios**: Marcar tests de integración y e2e:

```python
import pytest

@pytest.mark.integration
def test_auth_flow_with_db():
    ...

@pytest.mark.e2e
def test_full_checkout_flow():
    ...
```

1. **Configuración**: Declarar markers en `pytest.ini` o `pyproject.toml`:

```ini
[pytest]
markers =
    integration: tests de integración (requieren recursos externos)
    e2e: tests end-to-end (flujos completos y entornos pesados)
```

1. **Comandos de ejecución**:

```bash
# Todos los unitarios
pytest tests/unit

# Tests de integración
pytest tests/integration -m integration

# Tests e2e
pytest tests/e2e -m e2e

# Suite completa
pytest tests
```

### Fixtures y Utilidades

1. **Fixtures globales**: Definir en `tests/conftest.py`.
2. **Fixtures específicos**: En `tests/<tipo>/conftest.py`.
3. **Datos estáticos**: En `tests/data/` o `tests/<tipo>/data/`.

### Requisitos para CI/CD

1. **Obligatorio en cada push/PR**: Ejecutar `tests/unit/`.
2. **Tests de integración**: En PRs a ramas principales o pipelines nocturnos.
3. **Tests e2e**: En merges a `main` o pipelines nocturnos.

```bash
# Fast suite (CI en cada push)
pytest tests/unit

# Full backend suite (PR a main)
pytest tests/unit tests/integration -m "not e2e"

# Suite completa (nightly)
pytest tests -m "integration or e2e"
```

### Requisitos para Nuevas Contribuciones

1. **Todo código nuevo** en `src/` debe venir con tests en la carpeta adecuada:
   - Lógica pura → `tests/unit/`
   - Integración con BBDD/servicios → `tests/integration/`
   - Flujos de negocio completos → `tests/e2e/`

2. **Movimientos de módulos**: Si se mueve un módulo en `src/`, mover sus tests manteniendo correspondencia.

3. **PRs rechazados**:
   - Tests unitarios fuera de `tests/unit/`
   - Lógica de integración en tests bajo `tests/unit/`

---

## 🔄 Workflows

Los workflows son procedimientos guiados para tareas específicas.

### 1. Run Tests

**Descripción**: Ejecutar tests del proyecto usando pytest y uv.

**Comando estándar**:

```bash
uv run pytest
```

**Casos de uso**:

- Verificar que el código funciona correctamente.
- Antes de hacer commits o PRs.
- Durante el desarrollo para validar cambios.

---

### 2. Manage Dependencies

**Descripción**: Gestionar dependencias del proyecto correctamente usando uv.

**Pasos**:

1. **Añadir dependencia de producción**:

```bash
uv add <package_name>
```

Ejemplo:

```bash
uv add requests
```

1. **Añadir dependencia de desarrollo**:

```bash
uv add --dev <package_name>
```

Ejemplo:

```bash
uv add --dev pytest
```

1. **Sincronizar entorno** tras cambios manuales en `pyproject.toml`:

```bash
uv sync
```

1. **Actualizar README.md** si es necesario con información de la nueva dependencia.

2. **Actualizar documentación** en `docs/` (si usa mkdocs) con información del nuevo componente.

---

### 3. Create Component

**Descripción**: Crear un nuevo componente siguiendo principios DDD y SOLID.

**Pasos**:

1. **Identificar la capa** a la que pertenece el componente:
   - Domain (entidades, value objects)
   - Application (casos de uso, servicios de aplicación)
   - Infrastructure (repositorios, adaptadores externos)
   - UI (controladores, presentación)

2. **Crear el fichero** de la clase en `snake_case`:

```bash
touch src/<capa>/<nombre_componente>.py
```

Ejemplo:

```bash
touch src/domain/new_entity.py
```

1. **Definir la clase** asegurando:
   - Principio de Responsabilidad Única (SRP)
   - Documentación (docstrings estilo Google) para clase y métodos
   - Type hints estrictos

2. **Crear el fichero de test** correspondiente:

```bash
touch tests/unit/<capa>/test_<nombre_componente>.py
```

Ejemplo:

```bash
touch tests/unit/domain/test_new_entity.py
```

1. **Implementar tests** cubriendo casos de éxito y error.

2. **Lanzar tests** para verificar:

```bash
uv run pytest
```

1. **Actualizar README.md** si es necesario.

2. **Actualizar documentación** en `docs/` (si usa mkdocs).

---

### 4. Sync Artifacts

**Descripción**: Sincronizar artefactos generados (tasks, planes) a la carpeta `planning/` para mantener histórico.

**Pasos**:

1. **Asegurar que existe** la carpeta `planning`:

```bash
mkdir -p planning
```

1. **Copiar artefactos** a una carpeta con timestamp:

```bash
UUID="<session-uuid>"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="$HOME/.gemini/antigravity/brain/$UUID"
DEST_DIR="planning/$UUID/$TIMESTAMP"

mkdir -p "$DEST_DIR"
cp "$SOURCE_DIR"/*.md "$DEST_DIR/"
echo "Artifacts copied to $DEST_DIR"
```

**Nota**: Reemplazar `<session-uuid>` con el UUID de la sesión actual.

---

## 📌 Resumen de Comandos Esenciales

```bash
# Sincronizar dependencias
uv sync

# Añadir dependencia de producción
uv add <package>

# Añadir dependencia de desarrollo
uv add --dev <package>

# Ejecutar todos los tests
uv run pytest

# Ejecutar solo tests unitarios
uv run pytest tests/unit

# Ejecutar tests de integración
uv run pytest tests/integration -m integration

# Ejecutar con cobertura
uv run pytest --cov=src/<proyecto> --cov-report=html

# Ejecutar el servidor MCP
uv run home-assistant-mcp
```

---

## ✅ Checklist de Contribución

Antes de hacer un commit o PR, asegurarse de:

- [ ] El código sigue los principios SOLID, DDD, Clean Code
- [ ] Cada clase está en su propio fichero en `snake_case`
- [ ] Todas las funciones/clases tienen documentación estilo Google
- [ ] Se han creado tests unitarios en `tests/unit/`
- [ ] Se han creado tests de integración si aplica
- [ ] Los tests pasan: `uv run pytest`
- [ ] Se ha actualizado el README.md si es necesario
- [ ] Se ha actualizado la documentación en `docs/` si aplica
- [ ] Las dependencias nuevas se agregaron con `uv add` (o `uv add --dev`)

---

**Última actualización**: 2026-01-27
