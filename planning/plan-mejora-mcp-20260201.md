# Plan de Mejora del Servidor MCP de Home Assistant

**Fecha:** 2026-02-01
**Objetivo:** Alinear el servidor MCP con las mejores prácticas oficiales de Anthropic
**Skill Utilizado:** mcp-builder

---

## Resumen Ejecutivo

Después de revisar el código actual contra las mejores prácticas de MCP (Model Context Protocol), se han identificado múltiples áreas de mejora que afectan la usabilidad, seguridad, rendimiento y compatibilidad del servidor. Este plan prioriza las acciones necesarias para transformar el servidor de una implementación funcional básica a un servidor MCP de alta calidad que sigue todas las mejores prácticas recomendadas.

---

## Problemas Identificados

### 🔴 **CRÍTICOS** (Bloquean adopción de best practices)

#### 1. Arquitectura no compatible con FastMCP
- **Ubicación:** `src/home_assistant_mcp/server.py`
- **Problema:** Usa API de bajo nivel `mcp.server.Server` en lugar de FastMCP
- **Impacto:**
  - Pérdida de validación automática de entrada
  - Sin generación automática de schemas desde docstrings
  - Código más verboso y propenso a errores
  - Peor experiencia de desarrollo
- **Evidencia:** Líneas 15-16, 40-43 en server.py

#### 2. Falta de validación de entrada con Pydantic
- **Ubicación:** `src/home_assistant_mcp/tools/*.py`
- **Problema:** Las herramientas usan `dict[str, Any]` en lugar de modelos Pydantic
- **Impacto:**
  - Sin validación de tipos en tiempo de ejecución
  - Sin documentación automática de parámetros
  - Errores difíciles de debugear
  - No cumple con las mejores prácticas de Python MCP SDK
- **Evidencia:** Todos los archivos `execute()` reciben `arguments: dict[str, Any]`

#### 3. Sin anotaciones de herramientas
- **Ubicación:** `src/home_assistant_mcp/tools/*.py`
- **Problema:** Ninguna herramienta define anotaciones MCP estándar
- **Impacto:**
  - Los clientes no saben qué operaciones son de solo lectura
  - No se puede distinguir operaciones destructivas
  - Sin información sobre idempotencia
  - Dificulta la toma de decisiones del agente
- **Anotaciones faltantes:**
  - `readOnlyHint`: Para operaciones de consulta
  - `destructiveHint`: Para operaciones que modifican estado
  - `idempotentHint`: Para operaciones repetibles
  - `openWorldHint`: Para operaciones con entidades externas

#### 4. Falta de soporte para múltiples formatos de respuesta
- **Ubicación:** `src/home_assistant_mcp/tools/*.py`
- **Problema:** Solo texto plano, sin opción JSON/Markdown estructurado
- **Impacto:**
  - Dificulta procesamiento programático por agentes
  - No se puede elegir entre formato humano vs máquina
  - No sigue el patrón recomendado de ResponseFormat
- **Referencia:** MCP Best Practices - Response Formats

---

### 🟡 **IMPORTANTES** (Afectan usabilidad y rendimiento)

#### 5. Sin paginación en listados
- **Ubicación:** `src/home_assistant_mcp/tools/ha_list_entities.py`, `ha_list_services.py`
- **Problema:** Devuelven todos los resultados sin límite
- **Impacto:**
  - Puede devolver miles de entidades
  - Saturación de memoria y ancho de banda
  - Timeouts en instalaciones grandes
  - No sigue MCP Best Practices para paginación
- **Solución requerida:**
  - Parámetros `limit` (default: 20-50) y `offset`
  - Metadata: `total`, `count`, `has_more`, `next_offset`

#### 6. Gestión de recursos no óptima
- **Ubicación:** `src/home_assistant_mcp/server.py:30-37`
- **Problema:** Cliente global que nunca se cierra correctamente
- **Impacto:**
  - Conexiones HTTP/WebSocket abiertas indefinidamente
  - Posibles memory leaks
  - No aprovecha lifecycle hooks de FastMCP
- **Código problemático:**
```python
_client: HomeAssistantClient | None = None
_config: HomeAssistantConfig | None = None

def get_client() -> HomeAssistantClient:
    global _client, _config
    if _client is None:
        # ...
    return _client  # Nunca se cierra
```

#### 7. Mensajes de error poco accionables
- **Ubicación:** `src/home_assistant_mcp/server.py:61-75`
- **Problema:** Errores genéricos sin contexto ni sugerencias
- **Ejemplos problemáticos:**
  - `"Missing required argument: {e}"` - ¿Cuál argumento? ¿Qué valores son válidos?
  - `"Invalid argument type: {e}"` - ¿Qué tipo se esperaba?
  - `"Internal error: {e}"` - ¿Cómo resolver?
- **Mejor práctica:** Incluir argumento específico, valores válidos, siguiente paso sugerido

#### 8. Falta de documentación en herramientas
- **Ubicación:** Todos los `TOOL_DEF` en `src/home_assistant_mcp/tools/`
- **Problema:** Descripciones muy básicas, sin ejemplos concretos
- **Ejemplos:**
  - `ha_health_check`: "Check if Home Assistant API is accessible and running"
  - Mejor: "Check if Home Assistant API is accessible and running. Returns API version and status. Example: Use this before other operations to verify connectivity."
- **Impacto:** Agentes no entienden cuándo usar cada herramienta

---

### 🟢 **MEJORAS RECOMENDADAS** (Refinamiento y calidad)

#### 9. Actualizar README con ejemplos de uso
- **Ubicación:** `README.md:99-112`
- **Problema:** Lista de herramientas desactualizada
- **Faltantes:**
  - `ha_list_areas`
  - `ha_get_area_entities`
  - `ha_get_area_devices`
  - `ha_get_entity_area`
  - `ha_render_template`
  - `ha_list_dashboards`
  - `ha_get_dashboard`
  - `ha_create_dashboard`
  - `ha_update_dashboard`
  - `ha_delete_dashboard`

#### 10. Crear archivo de evaluaciones
- **Ubicación:** Falta `evaluations.xml`
- **Problema:** No hay evaluaciones MCP para testing automatizado
- **Impacto:** No se puede medir efectividad del servidor con agentes LLM
- **Requisito:** 10 preguntas complejas, read-only, independientes, verificables
- **Referencia:** `.claude/skills/mcp-builder/reference/evaluation.md`

#### 11. Optimizar imports en tools
- **Ubicación:** `src/home_assistant_mcp/tools/*.py`
- **Problema:** Imports repetitivos en cada archivo
- **Ejemplo actual:**
```python
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
```
- **Mejora:** Módulo común con imports y tipos compartidos

---

## Plan de Implementación

### **FASE 1: Migración a FastMCP** 🔴 (Alta Prioridad)

**Objetivo:** Migrar de `mcp.server.Server` a FastMCP con validación Pydantic

**Tareas:**

1. **Migrar server.py a FastMCP**
   - Reemplazar `from mcp.server import Server` por `from mcp.server.fastmcp import FastMCP`
   - Cambiar `server = Server("home-assistant-mcp")` por `mcp = FastMCP("home_assistant_mcp")`
   - Eliminar decoradores `@server.list_tools()` y `@server.call_tool()`
   - Implementar herramientas directamente con `@mcp.tool()`

2. **Crear modelos Pydantic para cada herramienta**
   - Crear archivo `src/home_assistant_mcp/tool_models.py`
   - Definir modelos para las 22 herramientas existentes
   - Usar `Field()` con descripciones detalladas
   - Añadir `model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra='forbid')`
   - Implementar validadores personalizados donde sea necesario

3. **Convertir herramientas a decoradores @mcp.tool()**
   - Modificar estructura de `src/home_assistant_mcp/tools/*.py`
   - Cambiar firma de `execute(client, arguments)` a función decorada con modelo Pydantic
   - Ejemplo:
     ```python
     @mcp.tool(annotations={...})
     async def ha_health_check() -> str:
         """Check if Home Assistant API is accessible..."""
     ```

4. **Añadir anotaciones a todas las herramientas**
   - Herramientas de solo lectura: `readOnlyHint=True, destructiveHint=False`
   - Herramientas destructivas: `readOnlyHint=False, destructiveHint=True`
   - Analizar idempotencia de cada operación
   - Todas tienen `openWorldHint=True` (interactúan con Home Assistant)

**Criterios de aceptación:**
- ✅ `server.py` usa FastMCP
- ✅ Todas las herramientas tienen modelos Pydantic
- ✅ Todas las herramientas tienen anotaciones correctas
- ✅ Tests pasan sin modificaciones (compatibilidad retroactiva)

**Archivos afectados:**
- `src/home_assistant_mcp/server.py`
- `src/home_assistant_mcp/tool_models.py` (nuevo)
- `src/home_assistant_mcp/tools/*.py` (22 archivos)

---

### **FASE 2: Validación y Formatos** 🔴 (Alta Prioridad)

**Objetivo:** Implementar formatos de respuesta y validación robusta

**Tareas:**

5. **Implementar enum ResponseFormat**
   - Crear en `src/home_assistant_mcp/tool_models.py`:
     ```python
     class ResponseFormat(str, Enum):
         MARKDOWN = "markdown"
         JSON = "json"
     ```
   - Añadir a modelos de herramientas de consulta como parámetro opcional

6. **Actualizar herramientas para soportar JSON y Markdown**
   - Herramientas afectadas:
     - `ha_list_entities` - formato tabla vs JSON estructurado
     - `ha_get_entity_state` - formato legible vs objeto JSON
     - `ha_list_services` - lista formateada vs JSON
     - `ha_get_config` - YAML-like vs JSON
     - `ha_list_areas` - lista simple vs JSON
     - `ha_get_history` - timeline vs JSON estructurado
   - Implementar función `format_response(data, format)` en utils

7. **Mejorar mensajes de error**
   - Crear módulo `src/home_assistant_mcp/error_handling.py`
   - Implementar función `create_error_message(error, context, suggestions)`
   - Actualizar manejo de errores en cada herramienta
   - Ejemplos de mejoras:
     - KeyError → "Argumento requerido 'entity_id' no proporcionado. Ejemplo: 'light.living_room'"
     - TypeError → "Argumento 'brightness' debe ser entero 0-255, recibido: {value}"
     - HomeAssistantError → "Entidad 'light.xyz' no encontrada. Use ha_list_entities para ver entidades disponibles."

8. **Añadir validación robusta en modelos**
   - Validadores de entity_id (formato domain.entity)
   - Validadores de rangos (brightness 0-255, etc.)
   - Validadores de enums (dominio válido, estado válido)
   - Ejemplo:
     ```python
     @field_validator('entity_id')
     @classmethod
     def validate_entity_id(cls, v: str) -> str:
         if '.' not in v:
             raise ValueError("entity_id debe tener formato 'domain.entity' (ej: 'light.living_room')")
         return v
     ```

**Criterios de aceptación:**
- ✅ Todas las herramientas de consulta soportan JSON y Markdown
- ✅ Errores incluyen contexto y próximos pasos
- ✅ Validadores Pydantic cubren casos edge
- ✅ Tests de validación añadidos

**Archivos afectados:**
- `src/home_assistant_mcp/tool_models.py`
- `src/home_assistant_mcp/tools/utils.py`
- `src/home_assistant_mcp/error_handling.py` (nuevo)
- `src/home_assistant_mcp/tools/*.py` (herramientas de consulta)

---

### **FASE 3: Paginación y Rendimiento** 🟡 (Media Prioridad)

**Objetivo:** Implementar paginación en herramientas de listado

**Tareas:**

9. **Implementar paginación en ha_list_entities**
   - Añadir parámetros al modelo:
     - `limit: int = Field(default=50, ge=1, le=500)`
     - `offset: int = Field(default=0, ge=0)`
   - Implementar slicing: `entities[offset:offset+limit]`
   - Devolver metadata:
     ```json
     {
       "total": 150,
       "count": 50,
       "offset": 0,
       "has_more": true,
       "next_offset": 50,
       "entities": [...]
     }
     ```

10. **Implementar paginación en ha_list_services**
    - Similar a ha_list_entities
    - Default limit=20 (menos servicios que entidades)

11. **Implementar paginación en ha_get_history**
    - Parámetros adicionales: `limit`, `offset`
    - Considerar paginación temporal (por rangos de tiempo)

12. **Añadir metadata de paginación**
    - Crear función común `add_pagination_metadata(data, limit, offset, total)`
    - Usar en todas las herramientas de listado
    - Incluir en formato Markdown y JSON

**Criterios de aceptación:**
- ✅ ha_list_entities, ha_list_services, ha_get_history tienen paginación
- ✅ Metadata incluye total, count, offset, has_more, next_offset
- ✅ Default limits razonables (20-50)
- ✅ Tests verifican paginación correcta

**Archivos afectados:**
- `src/home_assistant_mcp/tools/ha_list_entities.py`
- `src/home_assistant_mcp/tools/ha_list_services.py`
- `src/home_assistant_mcp/tools/ha_get_history.py`
- `src/home_assistant_mcp/tools/utils.py`

---

### **FASE 4: Gestión de Recursos** 🟡 (Media Prioridad)

**Objetivo:** Implementar gestión correcta del ciclo de vida del cliente

**Tareas:**

13. **Refactorizar gestión del cliente con lifecycle hooks**
    - Eliminar variables globales `_client` y `_config`
    - Usar FastMCP lifecycle hooks:
      ```python
      @mcp.on_startup()
      async def startup():
          global client
          config = load_config()
          client = HomeAssistantClient(config)

      @mcp.on_shutdown()
      async def shutdown():
          global client
          if client:
              await client.close()
      ```

14. **Implementar cierre correcto de conexiones**
    - Asegurar que `HomeAssistantClient.close()` cierra:
      - HTTP client (`self._client`)
      - WebSocket client (`self._ws_client`)
    - Añadir logging de cierre
    - Tests que verifican cierre correcto

15. **Añadir logging estructurado**
    - Migrar de `logging.basicConfig()` a logger configurado
    - Niveles apropiados:
      - DEBUG: Argumentos de herramientas
      - INFO: Ejecución de herramientas
      - WARNING: Operaciones sospechosas
      - ERROR: Errores recuperables
    - No logear a stdout (solo stderr para stdio transport)

**Criterios de aceptación:**
- ✅ Cliente se inicializa en startup y cierra en shutdown
- ✅ Sin variables globales para el cliente
- ✅ Tests verifican que no hay leaks de conexiones
- ✅ Logging estructurado en todos los niveles

**Archivos afectados:**
- `src/home_assistant_mcp/server.py`
- `src/home_assistant_mcp/client.py`
- Tests de integración

---

### **FASE 5: Documentación y Testing** 🟢 (Media Prioridad)

**Objetivo:** Mejorar documentación y crear evaluaciones MCP

**Tareas:**

16. **Mejorar docstrings con ejemplos concretos**
    - Cada herramienta debe tener:
      - Descripción clara de funcionalidad
      - Ejemplos de uso con valores reales
      - Casos de uso típicos
      - Errores comunes y cómo evitarlos
    - Ejemplo:
      ```python
      async def ha_turn_on(params: TurnOnInput) -> str:
          """Turn on an entity with optional parameters.

          This tool turns on lights, switches, or other controllable entities.
          You can specify additional parameters like brightness or color for lights.

          Examples:
              - Turn on a light: entity_id="light.living_room"
              - Set brightness: entity_id="light.kitchen", brightness=128
              - Set color: entity_id="light.bedroom", rgb_color=[255, 0, 0]

          Common errors:
              - Entity not found: Use ha_list_entities to find valid entity IDs
              - Domain not supported: Only works with controllable entities
          """
      ```

17. **Actualizar README con todas las herramientas**
    - Tabla completa con las 22 herramientas
    - Descripción de cada una
    - Ejemplos de uso en lenguaje natural
    - Sección de herramientas por categoría:
      - Consulta (read-only)
      - Control (destructive)
      - Áreas y ubicaciones
      - Dashboards
      - Avanzado (templates, eventos)

18. **Crear archivo evaluations.xml**
    - 10 preguntas complejas siguiendo guía de evaluation.md
    - Requisitos por pregunta:
      - Independiente (no depende de otras)
      - Solo read-only (no destructiva)
      - Compleja (requiere múltiples llamadas)
      - Realista (caso de uso real)
      - Verificable (respuesta única y clara)
      - Estable (respuesta no cambia en el tiempo)
    - Ejemplos de preguntas:
      1. "¿Cuántas luces hay en áreas que contienen la palabra 'bedroom'?"
      2. "¿Qué entidad de sensor de temperatura tiene el valor más alto actualmente?"
      3. "¿Cuántos switches están en estado 'on' en el área 'kitchen'?"
    - Verificar respuestas manualmente antes de incluir

19. **Añadir más tests de integración**
    - Tests para paginación
    - Tests para formatos JSON/Markdown
    - Tests para validación Pydantic
    - Tests para lifecycle (startup/shutdown)
    - Coverage objetivo: >90%

**Criterios de aceptación:**
- ✅ Todas las herramientas tienen docstrings completos con ejemplos
- ✅ README actualizado y completo
- ✅ evaluations.xml con 10 casos verificados
- ✅ Coverage >90% en tests

**Archivos afectados:**
- `src/home_assistant_mcp/tools/*.py`
- `README.md`
- `evaluations.xml` (nuevo)
- `tests/integration/*` (ampliado)

---

### **FASE 6: Refinamiento** 🟢 (Baja Prioridad)

**Objetivo:** Optimización final y pulido

**Tareas:**

20. **Optimizar imports y estructura de código**
    - Crear `src/home_assistant_mcp/tools/common.py`:
      ```python
      from typing import Any
      from mcp.types import TextContent
      from home_assistant_mcp.client import HomeAssistantClient
      from home_assistant_mcp.tool_models import ResponseFormat

      __all__ = ["TextContent", "HomeAssistantClient", "ResponseFormat"]
      ```
    - Usar `from .common import *` en herramientas
    - Reorganizar utils en módulos por responsabilidad

21. **Añadir más ejemplos al README**
    - Sección "Common Use Cases" con ejemplos completos
    - Guía de troubleshooting
    - FAQ

22. **Considerar herramientas de workflow de alto nivel**
    - Evaluar necesidad de herramientas compuestas:
      - `ha_turn_on_area(area_name, domain)` - Enciende todas las luces de un área
      - `ha_get_room_status(area_name)` - Estado completo de una habitación
      - `ha_create_scene(name, entities)` - Crea escena desde estado actual
    - Solo añadir si las evaluaciones muestran necesidad
    - Priorizar API coverage sobre workflows

**Criterios de aceptación:**
- ✅ Código más limpio y DRY
- ✅ README con ejemplos avanzados
- ✅ Decisión documentada sobre workflows

**Archivos afectados:**
- `src/home_assistant_mcp/tools/common.py` (nuevo)
- `src/home_assistant_mcp/tools/*.py`
- `README.md`

---

## Matriz de Priorización

| Fase | Prioridad | Impacto | Esfuerzo | Debe completarse antes de |
|------|-----------|---------|----------|---------------------------|
| Fase 1 | 🔴 Crítica | Alto | Alto | Fase 2, 3, 4 |
| Fase 2 | 🔴 Crítica | Alto | Medio | Fase 5 |
| Fase 3 | 🟡 Media | Medio | Medio | Fase 5 |
| Fase 4 | 🟡 Media | Medio | Bajo | - |
| Fase 5 | 🟢 Baja | Alto | Medio | - |
| Fase 6 | 🟢 Baja | Bajo | Bajo | - |

---

## Criterios de Éxito Global

### Técnicos
- ✅ Todas las herramientas usan FastMCP con modelos Pydantic
- ✅ Todas las herramientas tienen anotaciones apropiadas (readOnlyHint, etc.)
- ✅ Soporte para JSON y Markdown en todas las herramientas de consulta
- ✅ Paginación implementada en herramientas de listado
- ✅ Tests de evaluación MCP pasando al 100%
- ✅ Coverage de tests >90%
- ✅ Gestión de recursos sin leaks

### Documentación
- ✅ README actualizado y completo con 22 herramientas
- ✅ Docstrings completos con ejemplos en todas las herramientas
- ✅ evaluations.xml con 10 casos de prueba verificados

### Calidad
- ✅ Sin warnings de validación Pydantic
- ✅ Sin errores de mypy/type checking
- ✅ Código pasa ruff/linting sin errores
- ✅ Cumple 100% de MCP Best Practices

---

## Estimación de Impacto

| Área | Estado Actual | Estado Final | Mejora |
|------|---------------|--------------|---------|
| **Usabilidad por Agentes** | 🟡 Funcional pero limitado | 🟢 Excelente con anotaciones claras | +80% |
| **Seguridad** | 🟡 Básica | 🟢 Validación robusta | +60% |
| **Rendimiento** | 🟡 Problemas con listados grandes | 🟢 Paginación eficiente | +70% |
| **Mantenibilidad** | 🟡 Código verboso | 🟢 Código limpio y DRY | +75% |
| **Compatibilidad MCP** | 🔴 No sigue best practices | 🟢 100% compatible | +100% |
| **Experiencia de Desarrollo** | 🟡 API de bajo nivel | 🟢 FastMCP + Pydantic | +90% |

---

## Riesgos y Mitigaciones

### Riesgo 1: Breaking changes en migración a FastMCP
- **Probabilidad:** Media
- **Impacto:** Alto
- **Mitigación:**
  - Tests completos antes de migrar
  - Migración incremental herramienta por herramienta
  - Mantener compatibilidad retroactiva donde sea posible

### Riesgo 2: Rendimiento degradado con validación Pydantic
- **Probabilidad:** Baja
- **Impacto:** Medio
- **Mitigación:**
  - Benchmarks antes y después
  - Validación lazy donde sea apropiado
  - Caché de modelos compilados

### Riesgo 3: Evaluations.xml difíciles de crear
- **Probabilidad:** Media
- **Impacto:** Bajo
- **Mitigación:**
  - Seguir guía de evaluation.md al pie de la letra
  - Verificar respuestas manualmente
  - Empezar con preguntas simples y aumentar complejidad

---

## Próximos Pasos Inmediatos

1. **Revisar y aprobar este plan** con stakeholders
2. **Crear branch de desarrollo** `feature/mcp-improvements`
3. **Iniciar Fase 1**: Migración a FastMCP
4. **Configurar CI/CD** para validar best practices
5. **Documentar decisiones** en este plan conforme se implementan

---

## Referencias

- [MCP Best Practices](/.claude/skills/mcp-builder/reference/mcp_best_practices.md)
- [Python MCP Server Guide](/.claude/skills/mcp-builder/reference/python_mcp_server.md)
- [Evaluation Guide](/.claude/skills/mcp-builder/reference/evaluation.md)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk#fastmcp)

---

**Autor:** Claude Code + mcp-builder skill
**Última actualización:** 2026-02-01
