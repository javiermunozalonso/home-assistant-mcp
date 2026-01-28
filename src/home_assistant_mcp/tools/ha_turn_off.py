
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
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
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    entity_id = arguments["entity_id"]
    result = await client.turn_off(entity_id)
    return [
        TextContent(
            type="text",
            text=f"Turned off {entity_id}.\nNew state: {format_response(result.changed_states)}",
        )
    ]
