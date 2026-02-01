# Listado de Tareas - Mejora del Servidor MCP

**Fecha:** 2026-02-01
**Plan asociado:** `plan-mejora-mcp-20260201.md`

---

## Índice Rápido

- [Fase 1: Migración a FastMCP](#fase-1-migración-a-fastmcp) - 4 tareas
- [Fase 2: Validación y Formatos](#fase-2-validación-y-formatos) - 4 tareas
- [Fase 3: Paginación y Rendimiento](#fase-3-paginación-y-rendimiento) - 4 tareas
- [Fase 4: Gestión de Recursos](#fase-4-gestión-de-recursos) - 3 tareas
- [Fase 5: Documentación y Testing](#fase-5-documentación-y-testing) - 4 tareas
- [Fase 6: Refinamiento](#fase-6-refinamiento) - 3 tareas

**Total:** 22 tareas

---

## FASE 1: Migración a FastMCP 🔴

### Tarea 1.1: Migrar server.py a FastMCP
- [ ] **Actualizar imports en server.py**
  - Cambiar `from mcp.server import Server` → `from mcp.server.fastmcp import FastMCP`
  - Eliminar import `from mcp.server.stdio import stdio_server`
  - Eliminar imports `from mcp.types import TextContent, Tool`

- [ ] **Reemplazar instancia de servidor**
  - Cambiar `server = Server("home-assistant-mcp")` → `mcp = FastMCP("home_assistant_mcp")`
  - Nota: Nombre debe seguir convención Python: `snake_case` sin guiones

- [ ] **Eliminar decoradores obsoletos**
  - Eliminar función `list_tools()` con decorador `@server.list_tools()`
  - Eliminar función `call_tool()` con decorador `@server.call_tool()`
  - Eliminar diccionarios `TOOLS_LIST` y `TOOLS_MAP` de `tools/__init__.py`

- [ ] **Actualizar función main()**
  - FastMCP tiene su propio método `run()` integrado
  - Simplificar a: `mcp.run(transport="stdio")`
  - Eliminar función `run_server()` completa

- [ ] **Ejecutar tests para verificar compatibilidad**
  - `uv run pytest tests/unit/test_server.py`
  - Ajustar tests que verificaban estructura anterior

**Archivos a modificar:**
- `src/home_assistant_mcp/server.py`
- `src/home_assistant_mcp/tools/__init__.py`
- `tests/unit/test_server.py`

**Estimación:** 2 horas
**Prioridad:** 🔴 Crítica
**Dependencias:** Ninguna

---

### Tarea 1.2: Crear modelos Pydantic para todas las herramientas
- [ ] **Crear archivo tool_models.py**
  - Ubicación: `src/home_assistant_mcp/tool_models.py`
  - Imports necesarios:
    ```python
    from pydantic import BaseModel, Field, field_validator, ConfigDict
    from typing import Optional, List, Dict, Any
    from enum import Enum
    from datetime import datetime
    ```

- [ ] **Definir ResponseFormat enum**
  ```python
  class ResponseFormat(str, Enum):
      """Output format for tool responses."""
      MARKDOWN = "markdown"
      JSON = "json"
  ```

- [ ] **Crear modelos para herramientas de consulta (read-only)**
  - [ ] `HealthCheckInput` (sin parámetros, solo para consistencia)
  - [ ] `GetConfigInput` (sin parámetros)
  - [ ] `ListEntitiesInput`:
    - `domain: Optional[str]` - Dominio para filtrar
    - `limit: int = Field(default=50, ge=1, le=500)`
    - `offset: int = Field(default=0, ge=0)`
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`
  - [ ] `GetEntityStateInput`:
    - `entity_id: str = Field(..., description="Entity ID (e.g., 'light.living_room')")`
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`
  - [ ] `ListServicesInput`:
    - `limit: int = Field(default=20, ge=1, le=100)`
    - `offset: int = Field(default=0, ge=0)`
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`

- [ ] **Crear modelos para herramientas de control (destructive)**
  - [ ] `CallServiceInput`:
    - `domain: str = Field(..., description="Service domain (e.g., 'light', 'switch')")`
    - `service: str = Field(..., description="Service name (e.g., 'turn_on', 'turn_off')")`
    - `entity_id: Optional[str]` - Puede ser lista separada por comas
    - `data: Optional[Dict[str, Any]] = Field(default_factory=dict)`
  - [ ] `TurnOnInput`:
    - `entity_id: str`
    - `brightness: Optional[int] = Field(None, ge=0, le=255)`
    - `brightness_pct: Optional[int] = Field(None, ge=0, le=100)`
    - `color_temp: Optional[int] = Field(None, gt=0)`
    - `rgb_color: Optional[List[int]] = Field(None, min_items=3, max_items=3)`
  - [ ] `TurnOffInput`:
    - `entity_id: str`
  - [ ] `ToggleInput`:
    - `entity_id: str`

- [ ] **Crear modelos para herramientas de historial**
  - [ ] `GetHistoryInput`:
    - `entity_id: Optional[str]`
    - `start_time: Optional[datetime]`
    - `end_time: Optional[datetime]`
    - `limit: int = Field(default=100, ge=1, le=1000)`
    - `offset: int = Field(default=0, ge=0)`
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`

- [ ] **Crear modelos para herramientas de eventos**
  - [ ] `FireEventInput`:
    - `event_type: str = Field(..., min_length=1)`
    - `event_data: Optional[Dict[str, Any]] = Field(default_factory=dict)`

- [ ] **Crear modelos para herramientas de áreas**
  - [ ] `ListAreasInput`:
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`
  - [ ] `GetAreaEntitiesInput`:
    - `area: str = Field(..., description="Area ID or name")`
    - `domain: Optional[str] = Field(None, description="Optional domain filter (e.g., 'light')")`
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`
  - [ ] `GetAreaDevicesInput`:
    - `area: str`
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`
  - [ ] `GetEntityAreaInput`:
    - `entity_id: str`

- [ ] **Crear modelos para herramientas de templates**
  - [ ] `RenderTemplateInput`:
    - `template: str = Field(..., min_length=1, description="Jinja2 template to render")`

- [ ] **Crear modelos para herramientas de dashboards**
  - [ ] `ListDashboardsInput`:
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`
  - [ ] `GetDashboardInput`:
    - `url_path: Optional[str] = Field(None, description="Dashboard URL path (None for default)")`
    - `response_format: ResponseFormat = ResponseFormat.MARKDOWN`
  - [ ] `CreateDashboardInput`:
    - `url_path: str = Field(..., pattern=r'^[a-z0-9-]+$')`
    - `title: str = Field(..., min_length=1, max_length=100)`
    - `icon: Optional[str] = Field(None, pattern=r'^mdi:[a-z0-9-]+$')`
    - `show_in_sidebar: bool = Field(default=True)`
    - `require_admin: bool = Field(default=False)`
  - [ ] `UpdateDashboardInput`:
    - `dashboard_id: str = Field(..., min_length=1)`
    - `title: Optional[str] = Field(None, min_length=1)`
    - `icon: Optional[str] = Field(None, pattern=r'^mdi:[a-z0-9-]+$')`
    - `show_in_sidebar: Optional[bool] = None`
    - `require_admin: Optional[bool] = None`
  - [ ] `DeleteDashboardInput`:
    - `dashboard_id: str = Field(..., min_length=1)`

- [ ] **Añadir model_config a todos los modelos**
  ```python
  model_config = ConfigDict(
      str_strip_whitespace=True,
      validate_assignment=True,
      extra='forbid'
  )
  ```

- [ ] **Implementar validadores personalizados**
  - [ ] Validador de entity_id (formato domain.entity):
    ```python
    @field_validator('entity_id')
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        if '.' not in v:
            raise ValueError(
                "entity_id debe tener formato 'domain.entity' "
                "(ejemplo: 'light.living_room'). "
                "Use ha_list_entities para ver entidades disponibles."
            )
        return v
    ```
  - [ ] Validador de rgb_color (valores 0-255):
    ```python
    @field_validator('rgb_color')
    @classmethod
    def validate_rgb(cls, v: List[int] | None) -> List[int] | None:
        if v is not None:
            if not all(0 <= c <= 255 for c in v):
                raise ValueError(
                    "rgb_color debe contener valores entre 0 y 255. "
                    "Ejemplo: [255, 0, 0] para rojo"
                )
        return v
    ```

**Archivos a crear:**
- `src/home_assistant_mcp/tool_models.py` (nuevo, ~400-500 líneas)

**Estimación:** 4 horas
**Prioridad:** 🔴 Crítica
**Dependencias:** Tarea 1.1 (para entender estructura FastMCP)

---

### Tarea 1.3: Convertir herramientas a decoradores @mcp.tool()
- [ ] **Refactorizar estructura de archivos de herramientas**
  - Cada archivo debe exportar una función decorada, no un TOOL_DEF + execute
  - Nueva estructura ejemplo:
    ```python
    # ha_health_check.py
    from home_assistant_mcp.tool_models import HealthCheckInput

    async def ha_health_check(params: HealthCheckInput) -> str:
        """Check if Home Assistant API is accessible and running.

        Returns API status message and version information.
        Use this before other operations to verify connectivity.

        Returns:
            str: JSON or Markdown formatted status
        """
        # Implementación...
    ```

- [ ] **Convertir herramientas de consulta (8 herramientas)**
  - [ ] `ha_health_check.py`
  - [ ] `ha_get_config.py`
  - [ ] `ha_list_entities.py`
  - [ ] `ha_get_entity_state.py`
  - [ ] `ha_list_services.py`
  - [ ] `ha_list_areas.py`
  - [ ] `ha_get_area_entities.py`
  - [ ] `ha_get_area_devices.py`

- [ ] **Convertir herramientas de control (4 herramientas)**
  - [ ] `ha_call_service.py`
  - [ ] `ha_turn_on.py`
  - [ ] `ha_turn_off.py`
  - [ ] `ha_toggle.py`

- [ ] **Convertir herramientas de historial y eventos (2 herramientas)**
  - [ ] `ha_get_history.py`
  - [ ] `ha_fire_event.py`

- [ ] **Convertir herramientas de templates (1 herramienta)**
  - [ ] `ha_render_template.py`

- [ ] **Convertir herramientas de áreas (1 herramienta adicional)**
  - [ ] `ha_get_entity_area.py`

- [ ] **Convertir herramientas de dashboards (5 herramientas)**
  - [ ] `ha_list_dashboards.py`
  - [ ] `ha_get_dashboard.py`
  - [ ] `ha_create_dashboard.py`
  - [ ] `ha_update_dashboard.py`
  - [ ] `ha_delete_dashboard.py`

- [ ] **Actualizar tools/__init__.py**
  - Importar funciones en lugar de módulos
  - Registrar con FastMCP en server.py en lugar de exportar listas

- [ ] **Modificar server.py para registrar herramientas**
  - Importar todas las funciones de herramientas
  - Aplicar decorador @mcp.tool() a cada una con anotaciones

**Archivos a modificar:**
- `src/home_assistant_mcp/tools/*.py` (22 archivos)
- `src/home_assistant_mcp/tools/__init__.py`
- `src/home_assistant_mcp/server.py`

**Estimación:** 6 horas (30 min por herramienta + integración)
**Prioridad:** 🔴 Crítica
**Dependencias:** Tareas 1.1, 1.2

---

### Tarea 1.4: Añadir anotaciones a todas las herramientas
- [ ] **Definir anotaciones para herramientas read-only**
  - Template de anotaciones:
    ```python
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
    ```
  - Aplicar a: health_check, get_config, list_entities, get_entity_state,
    list_services, get_history, list_areas, get_area_entities,
    get_area_devices, get_entity_area, render_template,
    list_dashboards, get_dashboard

- [ ] **Definir anotaciones para herramientas destructivas no-idempotentes**
  - Template:
    ```python
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True
    }
    ```
  - Aplicar a: fire_event

- [ ] **Definir anotaciones para herramientas destructivas idempotentes**
  - Template:
    ```python
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,  # Múltiples llamadas = mismo resultado
        "openWorldHint": True
    }
    ```
  - Aplicar a: turn_on, turn_off, call_service (con mismo entity_id/data)

- [ ] **Definir anotaciones para toggle (destructiva no-idempotente)**
  - Template:
    ```python
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,  # Cada llamada cambia el estado
        "openWorldHint": True
    }
    ```
  - Aplicar a: toggle

- [ ] **Definir anotaciones para dashboards**
  - create_dashboard: destructive, non-idempotent
  - update_dashboard: destructive, idempotent
  - delete_dashboard: destructive, idempotent

- [ ] **Documentar decisiones de anotaciones**
  - Crear tabla en el plan explicando por qué cada herramienta tiene sus anotaciones
  - Casos especiales: por qué call_service puede ser idempotente

- [ ] **Verificar anotaciones en tests**
  - Crear test que verifique que todas las herramientas tienen las 4 anotaciones
  - Test que verifica coherencia (readOnly=True implica destructive=False)

**Archivos a modificar:**
- `src/home_assistant_mcp/server.py` (al registrar herramientas)
- `tests/unit/test_tool_annotations.py` (nuevo)
- `planning/plan-mejora-mcp-20260201.md` (tabla de anotaciones)

**Estimación:** 2 horas
**Prioridad:** 🔴 Crítica
**Dependencias:** Tarea 1.3

---

## FASE 2: Validación y Formatos 🔴

### Tarea 2.1: Implementar enum ResponseFormat
- [ ] **Verificar definición en tool_models.py**
  - Ya debería estar creado en Tarea 1.2
  - Verificar que esté exportado en `__all__`

- [ ] **Añadir ResponseFormat a modelos relevantes**
  - Añadir campo `response_format` a todos los modelos de herramientas de consulta
  - Default: `ResponseFormat.MARKDOWN`
  - Herramientas afectadas: list_entities, get_entity_state, list_services,
    get_config, list_areas, get_area_entities, get_area_devices, get_history,
    list_dashboards, get_dashboard

- [ ] **Documentar cuándo usar cada formato**
  - JSON: Para procesamiento programático, cuando el agente necesita parsear datos
  - Markdown: Para presentación al usuario, respuestas más legibles

**Archivos a modificar:**
- `src/home_assistant_mcp/tool_models.py`

**Estimación:** 1 hora
**Prioridad:** 🔴 Crítica
**Dependencias:** Tarea 1.2

---

### Tarea 2.2: Actualizar herramientas para soportar JSON y Markdown
- [ ] **Crear funciones de formato en utils.py**
  - [ ] `format_entity_list(entities, format)`:
    - Markdown: tabla con columnas entity_id, state, friendly_name
    - JSON: array de objetos con todos los campos
  - [ ] `format_entity_state(state, format)`:
    - Markdown: formato clave-valor legible con timestamps formateados
    - JSON: objeto EntityState completo
  - [ ] `format_services(services, format)`:
    - Markdown: lista por dominio con servicios indentados
    - JSON: array de ServiceDomain completo
  - [ ] `format_config(config, format)`:
    - Markdown: estilo YAML legible
    - JSON: objeto ConfigEntry completo
  - [ ] `format_history(history, format)`:
    - Markdown: timeline con timestamps legibles
    - JSON: array de HistoryEntry completo
  - [ ] `format_areas(areas, format)`:
    - Markdown: lista numerada
    - JSON: array de strings
  - [ ] `format_dashboards(dashboards, format)`:
    - Markdown: tabla con columnas id, title, url_path
    - JSON: array de Dashboard completo

- [ ] **Actualizar herramientas para usar funciones de formato**
  - [ ] ha_list_entities.py
  - [ ] ha_get_entity_state.py
  - [ ] ha_list_services.py
  - [ ] ha_get_config.py
  - [ ] ha_get_history.py
  - [ ] ha_list_areas.py
  - [ ] ha_get_area_entities.py
  - [ ] ha_get_area_devices.py
  - [ ] ha_list_dashboards.py
  - [ ] ha_get_dashboard.py

- [ ] **Crear tests para formatos**
  - Test que verifica formato JSON es JSON válido
  - Test que verifica formato Markdown contiene headers/tablas
  - Test de consistencia: mismo contenido en ambos formatos

**Archivos a modificar:**
- `src/home_assistant_mcp/tools/utils.py`
- `src/home_assistant_mcp/tools/ha_*.py` (herramientas de consulta)
- `tests/unit/test_formatting.py` (nuevo)

**Estimación:** 5 horas
**Prioridad:** 🔴 Crítica
**Dependencias:** Tarea 2.1

---

### Tarea 2.3: Mejorar mensajes de error
- [ ] **Crear módulo error_handling.py**
  - Ubicación: `src/home_assistant_mcp/error_handling.py`
  - Función principal:
    ```python
    def create_actionable_error(
        error: Exception,
        context: str,
        suggestions: List[str]
    ) -> str:
        """Create error message with context and next steps."""
    ```

- [ ] **Definir mensajes de error por tipo**
  - [ ] ValidationError (Pydantic):
    - Contexto: qué campo falló, valor recibido, constraint violado
    - Sugerencia: valores válidos, ejemplos correctos
  - [ ] HomeAssistantError:
    - 404: "Entidad '{entity_id}' no encontrada. Use ha_list_entities para ver entidades disponibles."
    - 401/403: "Error de autenticación. Verifique HA_TOKEN en .env"
    - 500: "Error del servidor de Home Assistant. Verifique que HA esté funcionando."
  - [ ] httpx.TimeoutException:
    - "Timeout al conectar con Home Assistant. Verifique HA_URL y que el servidor esté accesible."
  - [ ] KeyError:
    - "Parámetro requerido '{key}' no proporcionado. Parámetros requeridos: {required_params}"

- [ ] **Mapear errores comunes a soluciones**
  - Crear diccionario `ERROR_SOLUTIONS`:
    ```python
    ERROR_SOLUTIONS = {
        "entity not found": "Use ha_list_entities para listar entidades disponibles",
        "invalid domain": "Dominios válidos: light, switch, climate, sensor, etc.",
        "invalid brightness": "Brightness debe ser 0-255 o use brightness_pct para porcentaje",
        # ...
    }
    ```

- [ ] **Actualizar manejo de errores en server.py**
  - Reemplazar bloques try/except genéricos
  - Usar `create_actionable_error()` para todos los errores
  - Incluir código de error y tipo de excepción

- [ ] **Actualizar manejo de errores en client.py**
  - Mejorar excepciones HomeAssistantError con más contexto
  - Incluir status_code y response body cuando sea relevante

- [ ] **Crear tests de mensajes de error**
  - Test que verifica que errores incluyen sugerencias
  - Test que verifica que entity_id inválido sugiere ha_list_entities
  - Test que verifica formato consistente de errores

**Archivos a crear/modificar:**
- `src/home_assistant_mcp/error_handling.py` (nuevo)
- `src/home_assistant_mcp/server.py`
- `src/home_assistant_mcp/client.py`
- `tests/unit/test_error_handling.py` (nuevo)

**Estimación:** 4 horas
**Prioridad:** 🔴 Crítica
**Dependencias:** Tarea 1.3

---

### Tarea 2.4: Añadir validación robusta en modelos
- [ ] **Implementar validadores de entity_id**
  - Formato: `domain.entity_name`
  - Dominios válidos (lista exhaustiva o regex)
  - Caracteres permitidos en entity_name

- [ ] **Implementar validadores de rangos numéricos**
  - brightness: 0-255
  - brightness_pct: 0-100
  - color_temp: > 0 (en mireds)
  - rgb_color: [0-255, 0-255, 0-255]

- [ ] **Implementar validadores de formatos específicos**
  - dashboard url_path: lowercase, alphanumeric + guiones
  - dashboard icon: formato "mdi:icon-name"
  - template: no vacío, sintaxis Jinja2 básica

- [ ] **Implementar validadores de lógica de negocio**
  - TurnOnInput: brightness y brightness_pct mutuamente exclusivos
  - GetHistoryInput: end_time debe ser posterior a start_time
  - CreateDashboardInput: title no puede contener solo espacios

- [ ] **Añadir mensajes de error descriptivos**
  - Cada validator debe tener mensaje con:
    - Qué está mal
    - Qué se esperaba
    - Ejemplo de valor correcto

- [ ] **Crear tests de validación**
  - Test por cada validador
  - Tests de casos edge (valores límite)
  - Tests de mensajes de error

**Archivos a modificar:**
- `src/home_assistant_mcp/tool_models.py`
- `tests/unit/test_validation.py` (nuevo)

**Estimación:** 4 horas
**Prioridad:** 🔴 Crítica
**Dependencias:** Tarea 1.2

---

## FASE 3: Paginación y Rendimiento 🟡

### Tarea 3.1: Implementar paginación en ha_list_entities
- [ ] **Actualizar ListEntitiesInput (ya en Tarea 1.2)**
  - Verificar que tiene `limit` y `offset`

- [ ] **Implementar paginación en la función**
  - Obtener todas las entidades
  - Aplicar filtro de dominio si se proporciona
  - Calcular `total = len(filtered_entities)`
  - Aplicar slicing: `entities[offset:offset+limit]`
  - Preparar metadata de paginación

- [ ] **Crear función de metadata en utils.py**
  ```python
  def create_pagination_metadata(
      total: int,
      limit: int,
      offset: int
  ) -> Dict[str, Any]:
      count = min(limit, total - offset)
      has_more = offset + limit < total
      next_offset = offset + limit if has_more else None

      return {
          "total": total,
          "count": count,
          "offset": offset,
          "limit": limit,
          "has_more": has_more,
          "next_offset": next_offset
      }
  ```

- [ ] **Actualizar formato de respuesta**
  - JSON: incluir metadata + array de entities
  - Markdown: mostrar "Showing X-Y of Z entities" + tabla + hint de paginación

- [ ] **Actualizar docstring**
  - Explicar uso de limit y offset
  - Ejemplo de paginación: "Para obtener siguientes 50: limit=50, offset=50"

- [ ] **Crear tests de paginación**
  - Test límite menor que total
  - Test offset mayor que 0
  - Test última página (has_more=false)
  - Test página vacía (offset > total)

**Archivos a modificar:**
- `src/home_assistant_mcp/tools/ha_list_entities.py`
- `src/home_assistant_mcp/tools/utils.py`
- `tests/unit/test_pagination.py` (nuevo)

**Estimación:** 3 horas
**Prioridad:** 🟡 Media
**Dependencias:** Tareas 2.1, 2.2

---

### Tarea 3.2: Implementar paginación en ha_list_services
- [ ] **Actualizar ListServicesInput**
  - Similar a ListEntitiesInput

- [ ] **Implementar paginación**
  - Obtener todos los servicios
  - Convertir a lista plana (domain + service)
  - Aplicar paginación
  - Usar `create_pagination_metadata()`

- [ ] **Actualizar formatos**
  - JSON: metadata + services array
  - Markdown: contador + lista + hint

- [ ] **Tests de paginación**
  - Similar a ha_list_entities

**Archivos a modificar:**
- `src/home_assistant_mcp/tools/ha_list_services.py`
- `src/home_assistant_mcp/tool_models.py`
- `tests/unit/test_pagination.py`

**Estimación:** 2 horas
**Prioridad:** 🟡 Media
**Dependencias:** Tarea 3.1

---

### Tarea 3.3: Implementar paginación en ha_get_history
- [ ] **Actualizar GetHistoryInput**
  - Ya debe tener limit y offset de Tarea 1.2

- [ ] **Implementar paginación**
  - Obtener historial completo del rango de tiempo
  - Aplanar lista de listas si es necesario
  - Aplicar paginación
  - Metadata

- [ ] **Considerar paginación temporal**
  - Además de limit/offset numérico
  - Permitir paginación por ventanas de tiempo
  - Parámetro `window_hours: Optional[int]` para dividir en chunks temporales

- [ ] **Actualizar formatos**
  - JSON: metadata + history entries
  - Markdown: timeline con indicadores de página

- [ ] **Tests**
  - Paginación numérica
  - Paginación temporal (si se implementa)
  - Historial vacío

**Archivos a modificar:**
- `src/home_assistant_mcp/tools/ha_get_history.py`
- `src/home_assistant_mcp/tool_models.py`
- `tests/unit/test_pagination.py`

**Estimación:** 3 horas
**Prioridad:** 🟡 Media
**Dependencias:** Tarea 3.1

---

### Tarea 3.4: Añadir metadata de paginación a todas las herramientas de listado
- [ ] **Verificar que todas las herramientas de listado tienen paginación**
  - ha_list_entities ✓ (Tarea 3.1)
  - ha_list_services ✓ (Tarea 3.2)
  - ha_get_history ✓ (Tarea 3.3)
  - ha_list_areas - evaluar si necesita paginación (probablemente no, pocos items)
  - ha_get_area_entities - podría beneficiarse
  - ha_list_dashboards - evaluar (probablemente no, pocos items)

- [ ] **Implementar paginación en ha_get_area_entities si es necesario**
  - Si un área tiene >100 entidades, puede ser útil

- [ ] **Documentar defaults de paginación**
  - Crear tabla en README:
    | Herramienta | Default Limit | Max Limit | Razonamiento |
    |-------------|---------------|-----------|--------------|
    | list_entities | 50 | 500 | Balance entre utilidad y rendimiento |
    | list_services | 20 | 100 | Menos servicios que entidades |
    | get_history | 100 | 1000 | Historial puede ser extenso |

- [ ] **Crear guía de uso de paginación para usuarios**
  - Sección en README: "Working with Large Datasets"
  - Ejemplos de cómo paginar resultados
  - Cuándo usar limit alto vs múltiples requests

**Archivos a modificar:**
- `src/home_assistant_mcp/tools/ha_get_area_entities.py` (posiblemente)
- `README.md`
- `planning/plan-mejora-mcp-20260201.md`

**Estimación:** 2 horas
**Prioridad:** 🟡 Media
**Dependencias:** Tareas 3.1, 3.2, 3.3

---

## FASE 4: Gestión de Recursos 🟡

### Tarea 4.1: Refactorizar gestión del cliente con lifecycle hooks
- [ ] **Eliminar variables globales de server.py**
  - Eliminar `_client` y `_config`
  - Eliminar función `get_client()`

- [ ] **Implementar hooks de FastMCP**
  ```python
  @mcp.on_startup()
  async def startup():
      """Initialize Home Assistant client on server startup."""
      global client
      logger.info("Initializing Home Assistant client...")
      config = load_config()
      client = HomeAssistantClient(config)
      logger.info(f"Connected to Home Assistant at {config.url}")

  @mcp.on_shutdown()
  async def shutdown():
      """Cleanup resources on server shutdown."""
      global client
      if client:
          logger.info("Closing Home Assistant client...")
          await client.close()
          client = None
          logger.info("Client closed successfully")
  ```

- [ ] **Actualizar herramientas para usar cliente global**
  - En cada herramienta, acceder a `client` global
  - O pasar client como parámetro (investigar mejor patrón en FastMCP)

- [ ] **Añadir logging de lifecycle**
  - Log cuando se inicializa el cliente
  - Log cuando se cierra
  - Log de errores en startup (configuración inválida)

- [ ] **Tests de lifecycle**
  - Test que verifica que startup inicializa el cliente
  - Test que verifica que shutdown cierra el cliente
  - Test que verifica que múltiples startups no crean múltiples clientes

**Archivos a modificar:**
- `src/home_assistant_mcp/server.py`
- `tests/integration/test_lifecycle.py` (nuevo)

**Estimación:** 3 horas
**Prioridad:** 🟡 Media
**Dependencias:** Tarea 1.1

---

### Tarea 4.2: Implementar cierre correcto de conexiones
- [ ] **Mejorar método close() en client.py**
  - Ya existe, verificar que cierra:
    - HTTP client (`self._client`)
    - WebSocket client (`self._ws_client`)
  - Añadir manejo de excepciones robusto
  - No fallar si alguna conexión ya está cerrada

- [ ] **Añadir verificación de estado**
  - Propiedad `is_closed` para verificar si el cliente está cerrado
  - Evitar uso de cliente cerrado

- [ ] **Implementar __del__ como fallback**
  ```python
  def __del__(self):
      """Destructor to ensure cleanup."""
      if hasattr(self, '_client') and self._client and not self._client.is_closed:
          import warnings
          warnings.warn("HomeAssistantClient was not closed properly")
  ```

- [ ] **Logging de cierre**
  - Log cuando se cierra HTTP client
  - Log cuando se cierra WebSocket client
  - Log de warnings si hay problemas al cerrar

- [ ] **Tests de cierre**
  - Test que verifica que close() cierra HTTP client
  - Test que verifica que close() cierra WebSocket client
  - Test que verifica que close() es idempotente (llamarlo 2 veces no falla)
  - Test que verifica que uso después de close() lanza error descriptivo

**Archivos a modificar:**
- `src/home_assistant_mcp/client.py`
- `tests/unit/test_client.py`
- `tests/integration/test_client_cleanup.py` (nuevo)

**Estimación:** 2 horas
**Prioridad:** 🟡 Media
**Dependencias:** Ninguna (puede hacerse en paralelo)

---

### Tarea 4.3: Añadir logging estructurado
- [ ] **Configurar logger en server.py**
  - Eliminar `logging.basicConfig()`
  - Usar configuración más robusta:
    ```python
    import logging
    import sys

    logger = logging.getLogger("home_assistant_mcp")
    logger.setLevel(logging.INFO)

    # Solo a stderr para no interferir con stdio transport
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    ```

- [ ] **Añadir logging en niveles apropiados**
  - DEBUG: Argumentos de herramientas, responses de API
  - INFO: Ejecución de herramientas, lifecycle events
  - WARNING: Operaciones sospechosas, parámetros inusuales
  - ERROR: Errores recuperables
  - CRITICAL: Errores que impiden funcionamiento del servidor

- [ ] **Logging en client.py**
  - DEBUG: Cada request HTTP/WebSocket
  - INFO: Conexión establecida, autenticación exitosa
  - WARNING: Reintentos, timeouts
  - ERROR: Fallos de autenticación, errores de API

- [ ] **Logging en herramientas**
  - INFO al inicio: "Executing ha_turn_on with entity_id=light.living_room"
  - DEBUG: Parámetros completos
  - ERROR: Errores específicos de la herramienta

- [ ] **Configurar logging por entorno**
  - Variable de entorno `HA_LOG_LEVEL` (default: INFO)
  - En desarrollo: DEBUG
  - En producción: INFO o WARNING

- [ ] **Tests de logging**
  - Test que verifica que logs van a stderr, no stdout
  - Test que verifica niveles de log correctos
  - Test que verifica que información sensible no se loguea

**Archivos a modificar:**
- `src/home_assistant_mcp/server.py`
- `src/home_assistant_mcp/client.py`
- `src/home_assistant_mcp/config.py` (añadir HA_LOG_LEVEL)
- `tests/unit/test_logging.py` (nuevo)

**Estimación:** 2 horas
**Prioridad:** 🟡 Media
**Dependencias:** Ninguna

---

## FASE 5: Documentación y Testing 🟢

### Tarea 5.1: Mejorar docstrings con ejemplos concretos
- [ ] **Definir template de docstring**
  ```python
  async def ha_turn_on(params: TurnOnInput) -> str:
      """[One-line summary]

      [Detailed description of what the tool does]

      Examples:
          - [Example 1 with real values]
          - [Example 2 with different parameters]
          - [Example 3 showing advanced usage]

      Common use cases:
          - [Use case 1]
          - [Use case 2]

      Common errors:
          - [Error 1]: [How to fix]
          - [Error 2]: [How to fix]

      Args:
          params: [Description] containing:
              - field1: [Description]
              - field2: [Description]

      Returns:
          str: [Description of return format]
      """
  ```

- [ ] **Actualizar docstrings de herramientas de consulta (13 herramientas)**
  - [ ] ha_health_check
  - [ ] ha_get_config
  - [ ] ha_list_entities
  - [ ] ha_get_entity_state
  - [ ] ha_list_services
  - [ ] ha_list_areas
  - [ ] ha_get_area_entities
  - [ ] ha_get_area_devices
  - [ ] ha_get_entity_area
  - [ ] ha_render_template
  - [ ] ha_list_dashboards
  - [ ] ha_get_dashboard
  - [ ] ha_get_history

- [ ] **Actualizar docstrings de herramientas de control (9 herramientas)**
  - [ ] ha_call_service
  - [ ] ha_turn_on
  - [ ] ha_turn_off
  - [ ] ha_toggle
  - [ ] ha_fire_event
  - [ ] ha_create_dashboard
  - [ ] ha_update_dashboard
  - [ ] ha_delete_dashboard

- [ ] **Verificar que ejemplos son realistas**
  - Usar entity_ids típicos (light.living_room, switch.kitchen)
  - Usar valores de parámetros comunes (brightness=128, rgb_color=[255,0,0])
  - Incluir ejemplos de áreas comunes (bedroom, kitchen, living_room)

**Archivos a modificar:**
- `src/home_assistant_mcp/tools/*.py` (22 archivos)

**Estimación:** 4 horas (10-15 min por herramienta)
**Prioridad:** 🟢 Media-Baja
**Dependencias:** Tareas 1.3, 2.2

---

### Tarea 5.2: Actualizar README con todas las herramientas
- [ ] **Actualizar tabla de herramientas**
  - Añadir las 10 herramientas faltantes
  - Organizar por categoría:
    - **Health & Config** (2): health_check, get_config
    - **Entities** (4): list_entities, get_entity_state, get_history, get_entity_area
    - **Control** (5): call_service, turn_on, turn_off, toggle, fire_event
    - **Services** (1): list_services
    - **Areas** (3): list_areas, get_area_entities, get_area_devices
    - **Templates** (1): render_template
    - **Dashboards** (5): list_dashboards, get_dashboard, create_dashboard, update_dashboard, delete_dashboard

- [ ] **Actualizar sección de ejemplos**
  - Añadir ejemplos de uso de áreas:
    - "List all lights in the bedroom"
    - "Get all devices in the kitchen area"
  - Añadir ejemplos de dashboards:
    - "Create a new dashboard for energy monitoring"
    - "List all available dashboards"
  - Añadir ejemplos de templates:
    - "Render a template to check area state"

- [ ] **Añadir sección "Advanced Features"**
  - Uso de templates Jinja2
  - Gestión de dashboards
  - Queries complejas con áreas

- [ ] **Añadir sección "Response Formats"**
  - Explicar JSON vs Markdown
  - Cuándo usar cada uno
  - Ejemplos de cada formato

- [ ] **Añadir sección "Pagination"**
  - Cómo funciona limit y offset
  - Ejemplos de paginación
  - Best practices para datasets grandes

- [ ] **Actualizar sección de configuración**
  - Añadir variable HA_LOG_LEVEL
  - Explicar niveles de log

- [ ] **Añadir troubleshooting**
  - Problema: "Connection refused"
    - Solución: Verificar HA_URL, que Home Assistant esté corriendo
  - Problema: "Authentication failed"
    - Solución: Verificar HA_TOKEN, regenerar si es necesario
  - Problema: "Timeout"
    - Solución: Aumentar HA_TIMEOUT, verificar red
  - Problema: "Entity not found"
    - Solución: Usar ha_list_entities para verificar entity_id

- [ ] **Añadir sección de mejores prácticas**
  - Usar response_format=JSON cuando se procesen datos
  - Usar paginación para listados grandes
  - Verificar conectividad con ha_health_check antes de operaciones
  - Usar ha_list_entities para descubrir entity_ids

**Archivos a modificar:**
- `README.md`

**Estimación:** 3 horas
**Prioridad:** 🟢 Media
**Dependencias:** Todas las fases anteriores (para documentar features implementadas)

---

### Tarea 5.3: Crear archivo evaluations.xml
- [ ] **Estudiar guía de evaluación**
  - Leer `.claude/skills/mcp-builder/reference/evaluation.md` completo
  - Entender requisitos de preguntas:
    - Independientes
    - Read-only
    - Complejas (3+ tool calls)
    - Realistas
    - Verificables
    - Estables

- [ ] **Inspeccionar herramientas disponibles**
  - Listar todas las herramientas read-only
  - Identificar combinaciones interesantes de herramientas

- [ ] **Explorar contenido disponible (usando Home Assistant real si es posible)**
  - Usar ha_list_entities para ver qué datos hay
  - Usar ha_list_areas para ver áreas
  - Usar ha_list_services para ver servicios
  - Usar ha_get_config para ver configuración

- [ ] **Generar 10 preguntas complejas**
  - Pregunta 1: Conteo con filtro
    - Ejemplo: "¿Cuántas luces hay en áreas que contienen 'bedroom' en su nombre?"
  - Pregunta 2: Comparación de estados
    - Ejemplo: "¿Qué sensor de temperatura tiene el valor más alto actualmente?"
  - Pregunta 3: Query multi-área
    - Ejemplo: "¿Cuántos dispositivos hay en total en las áreas 'kitchen' y 'living_room'?"
  - Pregunta 4: Análisis de servicios
    - Ejemplo: "¿Cuántos servicios distintos ofrece el dominio 'automation'?"
  - Pregunta 5: Estado de área
    - Ejemplo: "¿Cuántos switches están en estado 'on' en el área 'bedroom'?"
  - Pregunta 6: Descubrimiento de relaciones
    - Ejemplo: "¿En qué área está ubicada la entidad 'light.kitchen_main'?"
  - Pregunta 7: Análisis de configuración
    - Ejemplo: "¿Qué versión de Home Assistant está corriendo?"
  - Pregunta 8: Query con templates
    - Ejemplo: "¿Cuántas entidades de dominio 'light' están actualmente en estado 'on'?"
  - Pregunta 9: Análisis de dashboards
    - Ejemplo: "¿Cuántos dashboards hay configurados que se muestran en el sidebar?"
  - Pregunta 10: Query histórico
    - Ejemplo: "¿Cuántos cambios de estado tuvo la entidad 'binary_sensor.front_door' en las últimas 24 horas?"

- [ ] **Resolver cada pregunta manualmente**
  - Ejecutar las tool calls necesarias
  - Verificar que la respuesta es única y verificable
  - Documentar el proceso de resolución

- [ ] **Crear archivo evaluations.xml**
  ```xml
  <evaluation>
    <qa_pair>
      <question>[Pregunta 1]</question>
      <answer>[Respuesta 1]</answer>
    </qa_pair>
    <!-- ... 9 more qa_pairs -->
  </evaluation>
  ```

- [ ] **Validar formato XML**
  - Verificar que es XML bien formado
  - Verificar que tiene exactamente 10 qa_pairs

- [ ] **Documentar proceso de evaluación**
  - Crear `evaluations-guide.md` explicando cómo se crearon las preguntas
  - Incluir razonamiento de por qué cada pregunta cumple los criterios

**Archivos a crear:**
- `evaluations.xml`
- `planning/evaluations-guide.md`

**Estimación:** 4 horas (exploración + creación + verificación)
**Prioridad:** 🟢 Media
**Dependencias:** Todas las fases anteriores (necesita servidor funcional)

---

### Tarea 5.4: Añadir más tests de integración
- [ ] **Tests de paginación completos**
  - Test de múltiples páginas consecutivas
  - Test de última página
  - Test de offset mayor que total
  - Test de limit=1 (edge case)
  - Test de limit=500 (max)

- [ ] **Tests de formatos JSON/Markdown**
  - Test que JSON es parseable
  - Test que Markdown contiene markdown válido
  - Test de consistencia de datos entre formatos
  - Test de campos requeridos en JSON
  - Test de formato legible en Markdown

- [ ] **Tests de validación Pydantic**
  - Test de cada validador personalizado
  - Test de mensajes de error de validación
  - Test de valores límite (boundary testing)
  - Test de tipos incorrectos

- [ ] **Tests de lifecycle**
  - Test de startup hook
  - Test de shutdown hook
  - Test de reinicialización (shutdown + startup)
  - Test de errores en startup (config inválida)

- [ ] **Tests de manejo de errores**
  - Test de error 404 (entidad no encontrada)
  - Test de error 401 (auth fallo)
  - Test de timeout
  - Test de error de red

- [ ] **Tests de herramientas de dashboards (WebSocket)**
  - Mock de WebSocket para tests
  - Test de creación de dashboard
  - Test de actualización
  - Test de eliminación
  - Test de listado

- [ ] **Tests de herramientas de áreas**
  - Test de obtención de entidades por área
  - Test de filtrado por dominio
  - Test de área inexistente

- [ ] **Aumentar coverage**
  - Objetivo: >90%
  - Identificar líneas sin coverage
  - Añadir tests para cubrir casos faltantes

- [ ] **Tests de regresión**
  - Guardar casos que han fallado en el pasado
  - Asegurar que no vuelvan a fallar

**Archivos a crear/modificar:**
- `tests/integration/test_pagination.py`
- `tests/integration/test_formats.py`
- `tests/integration/test_validation.py`
- `tests/integration/test_lifecycle.py`
- `tests/integration/test_error_handling.py`
- `tests/integration/test_dashboards.py`
- `tests/integration/test_areas.py`

**Estimación:** 6 horas
**Prioridad:** 🟢 Media
**Dependencias:** Todas las fases anteriores

---

## FASE 6: Refinamiento 🟢

### Tarea 6.1: Optimizar imports y estructura de código
- [ ] **Crear módulo common.py**
  - Ubicación: `src/home_assistant_mcp/tools/common.py`
  - Imports compartidos:
    ```python
    from typing import Any, Optional, List, Dict
    from home_assistant_mcp.client import HomeAssistantClient
    from home_assistant_mcp.tool_models import ResponseFormat
    from home_assistant_mcp.tools.utils import (
        format_response,
        create_pagination_metadata
    )

    __all__ = [
        "HomeAssistantClient",
        "ResponseFormat",
        "format_response",
        "create_pagination_metadata",
        "Any", "Optional", "List", "Dict"
    ]
    ```

- [ ] **Actualizar imports en herramientas**
  - Reemplazar imports individuales por:
    ```python
    from .common import *
    from home_assistant_mcp.tool_models import TurnOnInput  # Modelo específico
    ```

- [ ] **Reorganizar utils.py**
  - Separar en módulos por responsabilidad:
    - `utils/formatting.py` - Funciones de formato
    - `utils/pagination.py` - Funciones de paginación
    - `utils/validation.py` - Validadores comunes
  - Mantener `utils.py` como re-export para compatibilidad

- [ ] **Eliminar código duplicado**
  - Buscar patrones repetidos en herramientas
  - Extraer a funciones comunes
  - Ejemplo: parsing de entity_id comma-separated

- [ ] **Aplicar principio DRY**
  - Una sola fuente de verdad para cada concepto
  - Reusar funciones en lugar de copiar código

**Archivos a crear/modificar:**
- `src/home_assistant_mcp/tools/common.py` (nuevo)
- `src/home_assistant_mcp/tools/utils/formatting.py` (nuevo)
- `src/home_assistant_mcp/tools/utils/pagination.py` (nuevo)
- `src/home_assistant_mcp/tools/utils/validation.py` (nuevo)
- `src/home_assistant_mcp/tools/utils/__init__.py` (nuevo)
- `src/home_assistant_mcp/tools/*.py` (actualizar imports)

**Estimación:** 3 horas
**Prioridad:** 🟢 Baja
**Dependencias:** Todas las fases anteriores

---

### Tarea 6.2: Añadir más ejemplos al README
- [ ] **Crear sección "Common Use Cases"**
  - Caso 1: "Morning routine automation"
    - Listar luces del dormitorio
    - Encender luces a 30% de brillo
    - Obtener temperatura actual
  - Caso 2: "Energy monitoring"
    - Listar sensores de energía
    - Obtener estados actuales
    - Calcular consumo total
  - Caso 3: "Security check"
    - Listar binary_sensors (puertas/ventanas)
    - Verificar estados
    - Crear reporte
  - Caso 4: "Room status dashboard"
    - Obtener todas las entidades de un área
    - Formatear como dashboard
    - Guardar configuración

- [ ] **Añadir FAQ**
  - Q: ¿Cómo encuentro el entity_id de mis dispositivos?
  - Q: ¿Puedo controlar múltiples entidades a la vez?
  - Q: ¿Cómo sé qué servicios están disponibles?
  - Q: ¿Qué hago si una entidad no responde?
  - Q: ¿Cómo creo un template personalizado?
  - Q: ¿Puedo crear dashboards dinámicos?

- [ ] **Añadir sección "Integration Examples"**
  - Integración con Claude Desktop
  - Integración con scripts Python
  - Integración con Node.js
  - Integración con otros MCP servers

- [ ] **Añadir ejemplos de código**
  - Ejemplo de cliente Python que usa el MCP server
  - Ejemplo de automatización completa
  - Ejemplo de monitoreo continuo

**Archivos a modificar:**
- `README.md`

**Estimación:** 2 horas
**Prioridad:** 🟢 Baja
**Dependencias:** Tarea 5.2

---

### Tarea 6.3: Evaluar y decidir sobre herramientas de workflow
- [ ] **Analizar resultados de evaluations.xml**
  - ¿Qué patrones de uso se repiten?
  - ¿Qué combinaciones de herramientas son comunes?
  - ¿Hay operaciones que requieren muchas llamadas?

- [ ] **Identificar candidatos para workflows**
  - Posibles workflows de alto nivel:
    - `ha_get_area_status(area_name)`: Estado completo de un área
    - `ha_control_area(area_name, action, domain)`: Control masivo por área
    - `ha_create_scene_from_state(name, area)`: Crear escena desde estado actual
    - `ha_compare_areas(area1, area2)`: Comparar estados de dos áreas

- [ ] **Evaluar trade-offs**
  - **Pros de workflows:**
    - Menos llamadas MCP
    - Operaciones más semánticas
    - Más fácil para usuarios
  - **Cons de workflows:**
    - Menos flexibilidad
    - Más código a mantener
    - Pueden no cubrir todos los casos
    - Duplicación de lógica

- [ ] **Decisión: API coverage vs workflows**
  - Según MCP best practices: priorizar API coverage
  - Workflows solo si hay evidencia clara de necesidad
  - Algunos clientes tienen code execution (pueden combinar tools)

- [ ] **Documentar decisión**
  - Crear documento `planning/workflow-decision.md`
  - Explicar razonamiento
  - Listar workflows considerados
  - Conclusión: implementar o no implementar
  - Si no: explicar que se puede lograr con combinación de tools
  - Si sí: crear plan de implementación

- [ ] **Si se decide implementar workflows**
  - Priorizar 2-3 workflows más comunes
  - Implementar como herramientas adicionales
  - Documentar claramente que son shortcuts
  - Mantener herramientas básicas sin cambios

**Archivos a crear:**
- `planning/workflow-decision.md`
- (Opcional) `src/home_assistant_mcp/tools/ha_get_area_status.py`
- (Opcional) `src/home_assistant_mcp/tools/ha_control_area.py`

**Estimación:** 2 horas (análisis + decisión) + 3 horas (si se implementan workflows)
**Prioridad:** 🟢 Baja
**Dependencias:** Tarea 5.3 (evaluations para análisis de patrones)

---

## Resumen de Estimaciones

| Fase | Tareas | Horas Estimadas | Prioridad |
|------|--------|-----------------|-----------|
| Fase 1: Migración a FastMCP | 4 | 14h | 🔴 Crítica |
| Fase 2: Validación y Formatos | 4 | 14h | 🔴 Crítica |
| Fase 3: Paginación | 4 | 10h | 🟡 Media |
| Fase 4: Gestión de Recursos | 3 | 7h | 🟡 Media |
| Fase 5: Documentación y Testing | 4 | 17h | 🟢 Media |
| Fase 6: Refinamiento | 3 | 7h (+ 3h opcional) | 🟢 Baja |
| **TOTAL** | **22** | **69h** (~9 días) | |

---

## Checkpoints de Validación

### Checkpoint 1: Post-Fase 1
- [ ] Tests pasan sin errores
- [ ] FastMCP funcionando correctamente
- [ ] Todas las herramientas tienen modelos Pydantic
- [ ] Todas las herramientas tienen anotaciones

**Criterio de éxito:** `uv run pytest tests/unit` pasa al 100%

---

### Checkpoint 2: Post-Fase 2
- [ ] Todas las herramientas de consulta soportan JSON y Markdown
- [ ] Errores son accionables y descriptivos
- [ ] Validación robusta en todos los modelos

**Criterio de éxito:** Manual testing con inputs inválidos muestra errores útiles

---

### Checkpoint 3: Post-Fase 3
- [ ] Herramientas de listado tienen paginación funcional
- [ ] Metadata de paginación es correcta
- [ ] Performance mejorada con datasets grandes

**Criterio de éxito:** Listar 1000+ entidades no causa problemas

---

### Checkpoint 4: Post-Fase 4
- [ ] No hay memory leaks
- [ ] Cliente se cierra correctamente
- [ ] Logging funciona en todos los niveles

**Criterio de éxito:** Servidor puede correr horas sin degradación

---

### Checkpoint 5: Post-Fase 5
- [ ] README completo y actualizado
- [ ] evaluations.xml con 10 casos
- [ ] Coverage >90%
- [ ] Docstrings completos

**Criterio de éxito:** Nueva persona puede usar el servidor solo leyendo README

---

### Checkpoint 6: Post-Fase 6
- [ ] Código limpio y DRY
- [ ] No hay duplicación
- [ ] Decisión sobre workflows documentada

**Criterio de éxito:** Code review sin observaciones mayores

---

## Cómo Usar Este Documento

1. **Marcar tareas completadas** con `[x]` en lugar de `[ ]`
2. **Actualizar estimaciones** si difieren de la realidad
3. **Documentar decisiones** en el plan cuando se tomen
4. **Crear issues/PRs** referenciando números de tarea (ej: "Tarea 1.1: Migrar server.py")
5. **Revisar checkpoints** al finalizar cada fase
6. **Actualizar este documento** conforme se avanza

---

**Última actualización:** 2026-02-01
**Estado:** Pendiente de inicio
**Próxima tarea:** Tarea 1.1 - Migrar server.py a FastMCP
