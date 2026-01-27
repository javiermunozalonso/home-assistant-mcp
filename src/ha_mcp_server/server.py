"""MCP Server for Home Assistant integration."""

import json
from datetime import datetime
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import HomeAssistantClient, HomeAssistantError
from .config import HomeAssistantConfig, load_config

# Create the MCP server instance
server = Server("home-assistant-mcp")

# Global client instance (initialized when server starts)
_client: HomeAssistantClient | None = None
_config: HomeAssistantConfig | None = None


def get_client() -> HomeAssistantClient:
    """Get the Home Assistant client instance."""
    global _client, _config
    if _client is None:
        if _config is None:
            _config = load_config()
        _client = HomeAssistantClient(_config)
    return _client


def format_response(data: Any) -> str:
    """Format response data as JSON string."""
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump(), indent=2, default=str)
    if isinstance(data, list):
        return json.dumps(
            [item.model_dump() if hasattr(item, "model_dump") else item for item in data],
            indent=2,
            default=str,
        )
    return json.dumps(data, indent=2, default=str)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for Home Assistant control."""
    return [
        Tool(
            name="ha_health_check",
            description="Check if Home Assistant API is accessible and running",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ha_get_config",
            description="Get Home Assistant configuration including version, location, and loaded components",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ha_list_entities",
            description="List all entities or filter by domain (e.g., light, switch, sensor)",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Optional domain to filter entities (e.g., 'light', 'switch', 'sensor', 'climate')",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="ha_get_entity_state",
            description="Get the current state and attributes of a specific entity",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID (e.g., 'light.living_room', 'switch.kitchen')",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="ha_list_services",
            description="List all available services, optionally filtered by domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Optional domain to filter services (e.g., 'light', 'switch')",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="ha_call_service",
            description="Call a Home Assistant service to control devices",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Service domain (e.g., 'light', 'switch', 'climate')",
                    },
                    "service": {
                        "type": "string",
                        "description": "Service name (e.g., 'turn_on', 'turn_off', 'toggle')",
                    },
                    "entity_id": {
                        "type": "string",
                        "description": "Target entity ID or comma-separated list of IDs",
                    },
                    "data": {
                        "type": "object",
                        "description": "Additional service data (e.g., brightness, color_temp)",
                    },
                },
                "required": ["domain", "service"],
            },
        ),
        Tool(
            name="ha_turn_on",
            description="Turn on an entity (light, switch, etc.) with optional parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to turn on",
                    },
                    "brightness": {
                        "type": "integer",
                        "description": "Brightness level 0-255 (for lights)",
                        "minimum": 0,
                        "maximum": 255,
                    },
                    "brightness_pct": {
                        "type": "integer",
                        "description": "Brightness percentage 0-100 (for lights)",
                        "minimum": 0,
                        "maximum": 100,
                    },
                    "color_temp": {
                        "type": "integer",
                        "description": "Color temperature in mireds (for lights)",
                    },
                    "rgb_color": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "RGB color as [r, g, b] array (for lights)",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="ha_turn_off",
            description="Turn off an entity (light, switch, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to turn off",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="ha_toggle",
            description="Toggle an entity's state (on->off or off->on)",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to toggle",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="ha_get_history",
            description="Get historical state changes for an entity",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID to get history for",
                    },
                    "hours_ago": {
                        "type": "integer",
                        "description": "Number of hours of history to retrieve (default: 24)",
                        "default": 24,
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="ha_fire_event",
            description="Fire a custom event in Home Assistant",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                        "description": "Type of event to fire",
                    },
                    "event_data": {
                        "type": "object",
                        "description": "Optional data to include with the event",
                    },
                },
                "required": ["event_type"],
            },
        ),
        Tool(
            name="ha_list_areas",
            description="List all configured areas in Home Assistant",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ha_get_area_entities",
            description="Get all entities assigned to a specific area",
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area ID or name (e.g., 'salon', 'kitchen')",
                    },
                    "domain": {
                        "type": "string",
                        "description": "Optional domain to filter entities (e.g., 'light', 'switch', 'sensor')",
                    },
                },
                "required": ["area"],
            },
        ),
        Tool(
            name="ha_get_area_devices",
            description="Get all devices assigned to a specific area",
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area ID or name (e.g., 'salon', 'kitchen')",
                    },
                },
                "required": ["area"],
            },
        ),
        Tool(
            name="ha_get_entity_area",
            description="Get the area name for a specific entity",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "Entity ID (e.g., 'light.living_room')",
                    },
                },
                "required": ["entity_id"],
            },
        ),
        Tool(
            name="ha_render_template",
            description="Render a Home Assistant Jinja2 template. Useful for advanced queries using HA template functions like areas(), area_entities(), states(), etc.",
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {
                        "type": "string",
                        "description": "Jinja2 template string (e.g., '{{ states(\"sensor.temperature\") }}' or '{{ areas() | list }}')",
                    },
                },
                "required": ["template"],
            },
        ),
        Tool(
            name="ha_list_dashboards",
            description="List all Lovelace dashboards",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ha_get_dashboard",
            description="Get configuration of a specific dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "url_path": {
                        "type": "string",
                        "description": "Dashboard URL path (optional, null for default)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="ha_create_dashboard",
            description="Create a new Lovelace dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "url_path": {
                        "type": "string",
                        "description": "URL path for the dashboard (e.g., 'my-dashboard')",
                    },
                    "title": {
                        "type": "string",
                        "description": "Dashboard title",
                    },
                    "icon": {
                        "type": "string",
                        "description": "Optional dashboard icon (e.g., 'mdi:home')",
                    },
                    "show_in_sidebar": {
                        "type": "boolean",
                        "description": "Show in sidebar (default: true)",
                    },
                    "require_admin": {
                        "type": "boolean",
                        "description": "Require admin access (default: false)",
                    },
                },
                "required": ["url_path", "title"],
            },
        ),
        Tool(
            name="ha_update_dashboard",
            description="Update an existing dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_id": {
                        "type": "string",
                        "description": "Dashboard ID to update",
                    },
                    "title": {
                        "type": "string",
                        "description": "New title",
                    },
                    "icon": {
                        "type": "string",
                        "description": "New icon",
                    },
                    "show_in_sidebar": {
                        "type": "boolean",
                        "description": "Show in sidebar",
                    },
                },
                "required": ["dashboard_id"],
            },
        ),
        Tool(
            name="ha_delete_dashboard",
            description="Delete a dashboard",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_id": {
                        "type": "string",
                        "description": "Dashboard ID to delete",
                    },
                },
                "required": ["dashboard_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls for Home Assistant operations."""
    client = get_client()

    try:
        if name == "ha_health_check":
            result = await client.check_api()
            return [TextContent(type="text", text=f"Home Assistant API is running: {result.message}")]

        elif name == "ha_get_config":
            result = await client.get_config()
            return [TextContent(type="text", text=format_response(result))]

        elif name == "ha_list_entities":
            domain = arguments.get("domain")
            if domain:
                entities = await client.get_entities_by_domain(domain)
            else:
                entities = await client.get_states()

            # Return simplified list
            entity_list = [
                {
                    "entity_id": e.entity_id,
                    "state": e.state,
                    "friendly_name": e.attributes.get("friendly_name", e.entity_id),
                }
                for e in entities
            ]
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(entity_list)} entities:\n{json.dumps(entity_list, indent=2)}",
                )
            ]

        elif name == "ha_get_entity_state":
            entity_id = arguments["entity_id"]
            result = await client.get_state(entity_id)
            return [TextContent(type="text", text=format_response(result))]

        elif name == "ha_list_services":
            services = await client.get_services()
            domain = arguments.get("domain")
            if domain:
                services = [s for s in services if s.domain == domain]

            # Simplified service list
            service_list = []
            for domain_obj in services:
                for service_name, service_def in domain_obj.services.items():
                    service_list.append(
                        {
                            "service": f"{domain_obj.domain}.{service_name}",
                            "description": service_def.description or "No description",
                        }
                    )
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(service_list)} services:\n{json.dumps(service_list, indent=2)}",
                )
            ]

        elif name == "ha_call_service":
            domain = arguments["domain"]
            service = arguments["service"]
            entity_id = arguments.get("entity_id")
            data = arguments.get("data", {})

            # Handle comma-separated entity IDs
            if entity_id and "," in entity_id:
                entity_id = [e.strip() for e in entity_id.split(",")]

            result = await client.call_service(domain, service, entity_id=entity_id, data=data)
            return [
                TextContent(
                    type="text",
                    text=f"Service {domain}.{service} called successfully.\nChanged states: {format_response(result.changed_states)}",
                )
            ]

        elif name == "ha_turn_on":
            entity_id = arguments["entity_id"]
            kwargs = {}
            for key in ["brightness", "brightness_pct", "color_temp", "rgb_color"]:
                if key in arguments:
                    kwargs[key] = arguments[key]

            result = await client.turn_on(entity_id, **kwargs)
            return [
                TextContent(
                    type="text",
                    text=f"Turned on {entity_id}.\nNew state: {format_response(result.changed_states)}",
                )
            ]

        elif name == "ha_turn_off":
            entity_id = arguments["entity_id"]
            result = await client.turn_off(entity_id)
            return [
                TextContent(
                    type="text",
                    text=f"Turned off {entity_id}.\nNew state: {format_response(result.changed_states)}",
                )
            ]

        elif name == "ha_toggle":
            entity_id = arguments["entity_id"]
            result = await client.toggle(entity_id)
            return [
                TextContent(
                    type="text",
                    text=f"Toggled {entity_id}.\nNew state: {format_response(result.changed_states)}",
                )
            ]

        elif name == "ha_get_history":
            entity_id = arguments["entity_id"]
            hours_ago = arguments.get("hours_ago", 24)
            from datetime import timedelta

            start_time = datetime.now() - timedelta(hours=hours_ago)
            history = await client.get_history(entity_id=entity_id, start_time=start_time)

            # Flatten and format history
            entries = []
            for entity_history in history:
                for entry in entity_history:
                    entries.append(
                        {
                            "entity_id": entry.entity_id,
                            "state": entry.state,
                            "last_changed": str(entry.last_changed) if entry.last_changed else None,
                        }
                    )
            return [
                TextContent(
                    type="text",
                    text=f"History for {entity_id} (last {hours_ago} hours):\n{json.dumps(entries, indent=2)}",
                )
            ]

        elif name == "ha_fire_event":
            event_type = arguments["event_type"]
            event_data = arguments.get("event_data", {})
            await client.fire_event(event_type, event_data)
            return [TextContent(type="text", text=f"Event '{event_type}' fired successfully.")]

        elif name == "ha_list_areas":
            areas = await client.get_areas()
            # Get friendly names for each area
            area_info = []
            for area_id in areas:
                area_name = await client.get_area_name(area_id)
                area_info.append({
                    "area_id": area_id,
                    "name": area_name or area_id,
                })
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(areas)} areas:\n{json.dumps(area_info, indent=2)}",
                )
            ]

        elif name == "ha_get_area_entities":
            area = arguments["area"]
            domain = arguments.get("domain")
            entities = await client.get_area_entities(area, domain=domain)

            # Get states for each entity
            entity_info = []
            for entity_id in entities:
                try:
                    state = await client.get_state(entity_id)
                    entity_info.append({
                        "entity_id": entity_id,
                        "state": state.state,
                        "friendly_name": state.attributes.get("friendly_name", entity_id),
                    })
                except Exception:
                    entity_info.append({
                        "entity_id": entity_id,
                        "state": "unknown",
                        "friendly_name": entity_id,
                    })

            filter_msg = f" (domain: {domain})" if domain else ""
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(entities)} entities in area '{area}'{filter_msg}:\n{json.dumps(entity_info, indent=2)}",
                )
            ]

        elif name == "ha_get_area_devices":
            area = arguments["area"]
            devices = await client.get_area_devices(area)
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(devices)} devices in area '{area}':\n{json.dumps(devices, indent=2)}",
                )
            ]

        elif name == "ha_get_entity_area":
            entity_id = arguments["entity_id"]
            area = await client.get_entity_area(entity_id)
            if area:
                return [TextContent(type="text", text=f"Entity '{entity_id}' is in area: {area}")]
            else:
                return [TextContent(type="text", text=f"Entity '{entity_id}' is not assigned to any area")]

        elif name == "ha_render_template":
            template = arguments["template"]
            result = await client.render_template(template)
            return [TextContent(type="text", text=f"Template result:\n{result}")]

        elif name == "ha_list_dashboards":
            dashboards = await client.list_dashboards()
            dashboard_list = [
                {
                    "id": d.id,
                    "url_path": d.url_path,
                    "title": d.title,
                    "icon": d.icon,
                    "show_in_sidebar": d.show_in_sidebar,
                    "require_admin": d.require_admin,
                }
                for d in dashboards
            ]
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(dashboards)} dashboards:\n{json.dumps(dashboard_list, indent=2)}",
                )
            ]

        elif name == "ha_get_dashboard":
            url_path = arguments.get("url_path")
            config = await client.get_dashboard_config(url_path)
            return [TextContent(type="text", text=format_response(config))]

        elif name == "ha_create_dashboard":
            url_path = arguments["url_path"]
            title = arguments["title"]
            icon = arguments.get("icon")
            show_in_sidebar = arguments.get("show_in_sidebar", True)
            require_admin = arguments.get("require_admin", False)

            dashboard = await client.create_dashboard(
                url_path=url_path,
                title=title,
                icon=icon,
                show_in_sidebar=show_in_sidebar,
                require_admin=require_admin,
            )
            return [
                TextContent(
                    type="text",
                    text=f"Dashboard created successfully:\n{format_response(dashboard)}",
                )
            ]

        elif name == "ha_update_dashboard":
            dashboard_id = arguments["dashboard_id"]
            updates = {k: v for k, v in arguments.items() if k != "dashboard_id"}
            dashboard = await client.update_dashboard(dashboard_id, **updates)
            return [
                TextContent(
                    type="text",
                    text=f"Dashboard updated successfully:\n{format_response(dashboard)}",
                )
            ]

        elif name == "ha_delete_dashboard":
            dashboard_id = arguments["dashboard_id"]
            await client.delete_dashboard(dashboard_id)
            return [TextContent(type="text", text=f"Dashboard '{dashboard_id}' deleted successfully.")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except HomeAssistantError as e:
        return [TextContent(type="text", text=f"Home Assistant error: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def run_server() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Main entry point."""
    import asyncio

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
