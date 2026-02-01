"""MCP tools for Home Assistant organized by functionality.

This package contains all MCP tool implementations, grouped by domain:
- health: Health checks and configuration
- entities: Entity listing and state queries
- services: Service discovery and calls
- control: Device control operations (turn on/off/toggle)
- history: Historical state data
- events: Event firing
- areas: Area/room management
- templates: Jinja2 template rendering
- dashboards: Dashboard management
"""

# Import all tools so they can be registered with FastMCP
from .health import ha_health_check, ha_get_config
from .entities import ha_list_entities, ha_get_entity_state
from .services import ha_list_services, ha_call_service
from .control import ha_turn_on, ha_turn_off, ha_toggle
from .history import ha_get_history
from .events import ha_fire_event
from .areas import (
    ha_list_areas,
    ha_get_area_entities,
    ha_get_area_devices,
    ha_get_entity_area,
)
from .templates import ha_render_template
from .dashboards import (
    ha_list_dashboards,
    ha_get_dashboard,
    ha_create_dashboard,
    ha_update_dashboard,
    ha_delete_dashboard,
)



__health_and_config__ = [
    "ha_health_check",
    "ha_get_config",
]

__entities__ = [
    "ha_list_entities",
    "ha_get_entity_state",
]

__services__ = [
    "ha_list_services",
    "ha_call_service",
]

__control__ = [
    "ha_turn_on",
    "ha_turn_off",
    "ha_toggle",
]

__history__ = [
    "ha_get_history",
]

__events__ = [
    "ha_fire_event",
]

__areas__ = [
    "ha_list_areas",
    "ha_get_area_entities",
    "ha_get_area_devices",
    "ha_get_entity_area",
]

__templates__ = [
    "ha_render_template",
]

__dashboards__ = [
    "ha_list_dashboards",
    "ha_get_dashboard",
    "ha_create_dashboard",
    "ha_update_dashboard",
    "ha_delete_dashboard",
]

__all__ = [
    *__health_and_config__,
    *__entities__,
    *__services__,
    *__control__,
    *__history__,
    *__events__,
    *__areas__,
    *__templates__,
    *__dashboards__,
]
