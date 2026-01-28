
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
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
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
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
