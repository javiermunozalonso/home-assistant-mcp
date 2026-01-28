
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
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
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    entity_id = arguments["entity_id"]
    result = await client.get_state(entity_id)
    return [TextContent(type="text", text=format_response(result))]
