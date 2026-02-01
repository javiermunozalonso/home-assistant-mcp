# Arquitectura del Servidor MCP de Home Assistant

Este documento describe la arquitectura y organización del código del servidor MCP de Home Assistant.

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Estructura de Directorios](#estructura-de-directorios)
3. [Componentes Principales](#componentes-principales)
4. [Organización de Herramientas](#organización-de-herramientas)
5. [Principios de Diseño](#principios-de-diseño)
6. [Guía para Contribuir](#guía-para-contribuir)

---

## Visión General

El servidor MCP de Home Assistant está construido sobre **FastMCP**, un framework de alto nivel para Python que proporciona:

- Validación automática de parámetros mediante Pydantic
- Decoradores simples para registrar herramientas
- Gestión del ciclo de vida del servidor
- Soporte para múltiples formatos de respuesta (JSON y Markdown)
- Anotaciones semánticas para las herramientas (readOnly, destructive, idempotent)

### Stack Tecnológico

- **FastMCP**: Framework principal para el servidor MCP
- **Pydantic v2**: Validación de datos y modelos
- **httpx**: Cliente HTTP asíncrono para comunicación con Home Assistant
- **pytest**: Framework de testing

---

## Estructura de Directorios

```
src/home_assistant_mcp/
├── core.py              # Infraestructura central (FastMCP, cliente, lifecycle)
├── server.py            # Punto de entrada y registro de herramientas
├── client.py            # Cliente HTTP para Home Assistant REST API
├── config.py            # Configuración y carga desde variables de entorno
├── models.py            # Modelos Pydantic para respuestas de la API
├── tool_models.py       # Modelos Pydantic para entradas de herramientas
└── tools/               # Implementación de herramientas MCP por funcionalidad
    ├── __init__.py      # Exporta todas las herramientas
    ├── health.py        # Verificación de salud y configuración
    ├── entities.py      # Listado y consulta de entidades
    ├── services.py      # Listado y llamada de servicios
    ├── control.py       # Operaciones de control (encender/apagar/alternar)
    ├── history.py       # Datos históricos de estados
    ├── events.py        # Disparo de eventos personalizados
    ├── areas.py         # Gestión de áreas/habitaciones
    ├── templates.py     # Renderizado de plantillas Jinja2
    └── dashboards.py    # Gestión de dashboards de Lovelace
```

---

## Componentes Principales

### 1. `core.py` - Infraestructura Central

**Responsabilidad**: Proporciona la infraestructura base compartida por todo el servidor.

**Contenido**:
- Instancia de FastMCP con configuración de lifecycle
- Cliente global de Home Assistant
- Función `get_client()` para acceder al cliente
- Gestión del ciclo de vida (`app_lifespan`)
- Configuración de logging

**Por qué existe**: Separar la infraestructura central en un módulo independiente previene importaciones circulares entre `server.py` y el paquete `tools/`.

**Ejemplo de uso**:
```python
from .core import mcp, get_client

@mcp.tool(annotations={...})
async def my_tool(params: MyInput) -> str:
    client = get_client()
    # ... usar el cliente
```

### 2. `server.py` - Punto de Entrada

**Responsabilidad**: Punto de entrada principal del servidor MCP.

**Contenido**:
- Importa todas las herramientas desde `tools/` (los decoradores `@mcp.tool()` las registran automáticamente)
- Función `main()` que ejecuta el servidor

**Simplicidad**: Este archivo es intencionalmente simple (~50 líneas) y solo se encarga de:
1. Importar herramientas para registrarlas
2. Proporcionar el punto de entrada `main()`

### 3. `client.py` - Cliente de Home Assistant

**Responsabilidad**: Comunicación con la API REST de Home Assistant.

**Características**:
- Cliente HTTP asíncrono basado en `httpx.AsyncClient`
- Métodos para todas las operaciones de la API
- Gestión de errores y timeouts
- Soporte para plantillas Jinja2 (consultas de áreas)

### 4. `tool_models.py` - Modelos de Entrada

**Responsabilidad**: Definir y validar parámetros de entrada para todas las herramientas.

**Características**:
- Modelos Pydantic v2 para cada herramienta
- Validadores personalizados (formato entity_id, rangos RGB, etc.)
- Enum `ResponseFormat` para salidas JSON/Markdown
- Base común `ToolInputBase` con configuración compartida

**Ejemplo**:
```python
class TurnOnInput(ToolInputBase):
    entity_id: str = Field(..., description="Entity ID to turn on")
    brightness: Optional[int] = Field(None, ge=0, le=255, description="Brightness 0-255")

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        if "." not in v:
            raise ValueError("entity_id must be in format 'domain.entity'")
        return v
```

### 5. `tools/` - Implementación de Herramientas

**Responsabilidad**: Implementar todas las herramientas MCP, organizadas por funcionalidad.

**Organización por Dominio**:

| Archivo | Herramientas | Descripción |
|---------|-------------|-------------|
| `health.py` | `ha_health_check`, `ha_get_config` | Verificación de salud y configuración |
| `entities.py` | `ha_list_entities`, `ha_get_entity_state` | Consulta de entidades |
| `services.py` | `ha_list_services`, `ha_call_service` | Descubrimiento y llamada de servicios |
| `control.py` | `ha_turn_on`, `ha_turn_off`, `ha_toggle` | Control de dispositivos |
| `history.py` | `ha_get_history` | Datos históricos |
| `events.py` | `ha_fire_event` | Disparo de eventos |
| `areas.py` | `ha_list_areas`, `ha_get_area_*` | Gestión de áreas (4 herramientas) |
| `templates.py` | `ha_render_template` | Renderizado de plantillas |
| `dashboards.py` | `ha_list_dashboards`, `ha_create_dashboard`, etc. | Gestión de dashboards (5 herramientas) |

**Patrón de Implementación**:
```python
"""Module docstring explaining the domain."""

import logging
from ..core import mcp, get_client
from ..tool_models import MyInput, ResponseFormat

logger = logging.getLogger(__name__)

@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_my_tool(params: MyInput) -> str:
    """Tool description with examples.

    Examples:
        - Simple: ha_my_tool()
        - With params: ha_my_tool(param="value")

    Args:
        params: Input parameters

    Returns:
        str: Human-readable result
    """
    try:
        client = get_client()
        result = await client.some_operation(params.value)

        # Formato de respuesta dual (JSON/Markdown)
        if params.response_format == ResponseFormat.JSON:
            return json.dumps(result, indent=2)
        else:
            return f"# Result\n{result}"

    except Exception as e:
        logger.exception("Error in operation")
        return f"✗ Error: {e}"
```

---

## Organización de Herramientas

### Criterios de Agrupación

Las 22 herramientas están organizadas en 9 archivos siguiendo estos criterios:

1. **Cohesión funcional**: Herramientas relacionadas con el mismo dominio (entidades, servicios, áreas, etc.)
2. **Tamaño manejable**: Archivos de 50-150 líneas, fáciles de mantener
3. **Independencia**: Cada archivo puede entenderse y modificarse de forma independiente
4. **Escalabilidad**: Fácil agregar nuevas herramientas al dominio correspondiente

### Ejemplo: `tools/control.py`

Este archivo agrupa 3 herramientas relacionadas con **control de dispositivos**:

- `ha_turn_on` - Encender entidad (con parámetros opcionales: brillo, color)
- `ha_turn_off` - Apagar entidad
- `ha_toggle` - Alternar estado de entidad

**Justificación**: Las tres operaciones son conceptualmente relacionadas (control de estado on/off) y comparten:
- Mismos tipos de entidades objetivo
- Patrones de respuesta similares
- Anotaciones similares (destructive, idempotent/non-idempotent)

---

## Principios de Diseño

### 1. **DRY (Don't Repeat Yourself)**

- Modelos reutilizables en `tool_models.py`
- Validadores compartidos (entity_id, RGB)
- Base común `ToolInputBase` con configuración

### 2. **Single Responsibility Principle (SRP)**

- `core.py` → Infraestructura
- `server.py` → Punto de entrada
- `client.py` → Comunicación API
- `tools/*.py` → Implementación de herramientas por dominio

### 3. **Open/Closed Principle**

- Agregar nuevas herramientas no requiere modificar infraestructura
- Nuevos dominios se agregan como archivos en `tools/`
- Extensión sin modificación de código existente

### 4. **Dependency Inversion**

- Herramientas dependen de abstracciones (`get_client()`, modelos Pydantic)
- No dependen de implementaciones concretas
- Fácil testing con mocks

### 5. **Clean Code**

- Nombres descriptivos y claros
- Funciones pequeñas y enfocadas
- Documentación con ejemplos
- Manejo consistente de errores

---

## Guía para Contribuir

### Agregar una Nueva Herramienta

#### 1. **Definir el Modelo de Entrada** (`tool_models.py`)

```python
class MyNewToolInput(ToolInputBase):
    """Input for my_new_tool."""

    param1: str = Field(..., description="Description of param1")
    param2: Optional[int] = Field(None, ge=0, description="Optional param2")

    @field_validator("param1")
    @classmethod
    def validate_param1(cls, v: str) -> str:
        # Validación personalizada
        if not v:
            raise ValueError("param1 cannot be empty")
        return v
```

#### 2. **Implementar la Herramienta** (archivo apropiado en `tools/`)

Identifica el archivo más apropiado basándote en la funcionalidad:
- ¿Consulta entidades? → `entities.py`
- ¿Controla dispositivos? → `control.py`
- ¿Gestiona áreas? → `areas.py`
- ¿Nueva categoría? → Crear nuevo archivo en `tools/`

```python
@mcp.tool(
    annotations={
        "readOnlyHint": True,  # ¿Solo lectura?
        "destructiveHint": False,  # ¿Modifica estado?
        "idempotentHint": True,  # ¿Misma entrada = mismo resultado?
        "openWorldHint": True,  # ¿Interactúa con mundo externo?
    }
)
async def ha_my_new_tool(params: MyNewToolInput) -> str:
    """Brief description.

    Longer description with context.

    Examples:
        - Basic: ha_my_new_tool(param1="value")
        - Advanced: ha_my_new_tool(param1="value", param2=10)

    Args:
        params: Input parameters

    Returns:
        str: Result description
    """
    try:
        client = get_client()
        result = await client.new_operation(params.param1, params.param2)
        return f"✓ Success: {result}"
    except Exception as e:
        logger.exception("Error in my_new_tool")
        return f"✗ Error: {e}"
```

#### 3. **Exportar la Herramienta** (`tools/__init__.py`)

```python
from .appropriate_file import ha_my_new_tool

__all__ = [
    # ... existing tools
    "ha_my_new_tool",
]
```

#### 4. **Importar en `server.py`**

```python
from .tools import (
    # ... existing imports
    ha_my_new_tool,
)
```

#### 5. **Crear Tests** (`tests/unit/tools/test_appropriate_file.py`)

```python
import pytest
from unittest.mock import AsyncMock
from home_assistant_mcp import core
from home_assistant_mcp.tools.appropriate_file import ha_my_new_tool
from home_assistant_mcp.tool_models import MyNewToolInput

@pytest.mark.asyncio
async def test_my_new_tool_success():
    """Test ha_my_new_tool with successful operation."""
    mock_client = AsyncMock()
    mock_client.new_operation.return_value = "expected_result"
    core.client = mock_client

    result = await ha_my_new_tool(MyNewToolInput(param1="test"))

    assert "✓" in result
    assert "expected_result" in result
    mock_client.new_operation.assert_called_once_with("test", None)

@pytest.mark.asyncio
async def test_my_new_tool_error():
    """Test ha_my_new_tool handles errors."""
    mock_client = AsyncMock()
    mock_client.new_operation.side_effect = Exception("API Error")
    core.client = mock_client

    result = await ha_my_new_tool(MyNewToolInput(param1="test"))

    assert "✗" in result
    assert "API Error" in result
```

### Crear una Nueva Categoría de Herramientas

Si necesitas agregar herramientas que no encajan en ninguna categoría existente:

#### 1. **Crear nuevo archivo** (`tools/my_category.py`)

```python
"""Tools for my new category."""

import logging
from ..core import mcp, get_client
from ..tool_models import MyInput

logger = logging.getLogger(__name__)

# Implementar herramientas...
```

#### 2. **Actualizar `tools/__init__.py`**

```python
from .my_category import ha_category_tool1, ha_category_tool2

__all__ = [
    # ... existing
    "ha_category_tool1",
    "ha_category_tool2",
]
```

#### 3. **Actualizar `server.py`**

```python
from .tools import (
    # ... existing
    ha_category_tool1,
    ha_category_tool2,
)
```

### Modificar una Herramienta Existente

#### 1. **Localiza el archivo** en `tools/` correspondiente

Busca en `tools/__init__.py` para ver qué archivo contiene la herramienta.

#### 2. **Modifica la implementación**

Mantén la firma de la función y el formato de respuesta para compatibilidad.

#### 3. **Actualiza los tests**

Asegúrate de que los tests existentes pasen y agrega nuevos si es necesario.

#### 4. **Actualiza la documentación**

Si cambia la funcionalidad, actualiza el docstring y ejemplos.

---

## Mejores Prácticas

### 1. Validación de Entrada

- Usa validadores Pydantic para lógica compleja
- Proporciona mensajes de error claros y accionables
- Incluye ejemplos en las descripciones de los campos

### 2. Manejo de Errores

- Captura excepciones específicas cuando sea posible
- Usa `logger.exception()` para errores inesperados
- Retorna mensajes útiles con el símbolo `✗` para errores

### 3. Respuestas Duales (JSON/Markdown)

Para herramientas que retornan datos estructurados:

```python
if params.response_format == ResponseFormat.JSON:
    return json.dumps({
        "data": result,
        "metadata": {...}
    }, indent=2)
else:
    # Formato Markdown legible
    return f"""# Result

**Data**: {result}
**Metadata**: ...
"""
```

### 4. Paginación

Para herramientas que retornan listas:

```python
# Calcular paginación
total = len(all_items)
start = params.offset
end = min(start + params.limit, total)
paginated = all_items[start:end]
has_more = end < total

# Incluir metadata en JSON
return json.dumps({
    "total": total,
    "count": len(paginated),
    "offset": params.offset,
    "limit": params.limit,
    "has_more": has_more,
    "next_offset": end if has_more else None,
    "items": paginated
})
```

### 5. Anotaciones Semánticas

Usa anotaciones correctas para ayudar a los clientes a entender el comportamiento:

- `readOnlyHint: True` - Solo lectura, no modifica estado
- `destructiveHint: True` - Modifica o elimina datos
- `idempotentHint: True` - Misma entrada produce mismo resultado
- `idempotentHint: False` - Cada llamada puede producir diferente resultado (ej: toggle)
- `openWorldHint: True` - Interactúa con sistemas externos

### 6. Testing

- Tests unitarios para cada herramienta en `tests/unit/tools/`
- Mock del cliente (`core.client = AsyncMock()`)
- Tests de validación de entrada (Pydantic)
- Tests de manejo de errores
- Coverage objetivo: >90%

---

## Versionado y Compatibilidad

### Cambios Compatible (Minor/Patch)

- Agregar nuevas herramientas
- Agregar parámetros opcionales a herramientas existentes
- Mejorar mensajes de error
- Optimizaciones de rendimiento
- Correcciones de bugs

### Cambios Incompatibles (Major)

- Eliminar herramientas
- Cambiar parámetros requeridos
- Cambiar formato de respuesta de forma incompatible
- Renombrar herramientas

**Regla**: Siempre mantener compatibilidad hacia atrás cuando sea posible.

---

## Recursos Adicionales

- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Home Assistant REST API](https://developers.home-assistant.io/docs/api/rest/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)

---

## Historial de Cambios de Arquitectura

### 2026-02-01: Migración a FastMCP y Reorganización

**Cambios principales**:
- Migración de bajo nivel MCP API a FastMCP
- Creación de `tool_models.py` con modelos Pydantic
- Separación de herramientas en paquete `tools/` por funcionalidad
- Creación de `core.py` para infraestructura central
- Reducción de `server.py` a punto de entrada simple

**Motivación**:
- Reducir código repetitivo (75% menos código)
- Mejorar validación automática de entrada
- Facilitar mantenimiento y escalabilidad
- Mejor organización y localización de código

**Impacto**: Breaking change, requiere actualización de configuración en clientes MCP.
