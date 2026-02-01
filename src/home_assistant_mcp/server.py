"""MCP Server for Home Assistant integration using FastMCP.

This module provides the server entry point and registers all tools.

The actual tool implementations are organized in the tools/ package by functionality:
- tools.health: Health checks and configuration
- tools.entities: Entity listing and state queries
- tools.services: Service discovery and calls
- tools.control: Device control operations
- tools.history: Historical state data
- tools.events: Event firing
- tools.areas: Area/room management
- tools.templates: Jinja2 template rendering
- tools.dashboards: Dashboard management

Core infrastructure (FastMCP instance, client, lifecycle) is in core.py.
"""

from .core import get_client, mcp  # noqa: F401

# Import all tools to register them with FastMCP
# The @mcp.tool() decorators in each module will automatically register the tools
from .tools import (  # noqa: F401
    ha_call_service,
    ha_create_dashboard,
    ha_delete_dashboard,
    ha_fire_event,
    ha_get_area_devices,
    ha_get_area_entities,
    ha_get_config,
    ha_get_dashboard,
    ha_get_entity_area,
    ha_get_entity_state,
    ha_get_history,
    ha_health_check,
    ha_list_areas,
    ha_list_dashboards,
    ha_list_entities,
    ha_list_services,
    ha_render_template,
    ha_toggle,
    ha_turn_off,
    ha_turn_on,
    ha_update_dashboard,
)


def main() -> None:
    """Main entry point for the MCP server."""
    import asyncio

    # Run FastMCP server with stdio transport
    asyncio.run(mcp.run(transport="stdio"))


if __name__ == "__main__":
    main()
