
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
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
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    entity_id = arguments["entity_id"]
    area = await client.get_entity_area(entity_id)
    if area:
        return [TextContent(type="text", text=f"Entity '{entity_id}' is in area: {area}")]
    else:
        return [TextContent(type="text", text=f"Entity '{entity_id}' is not assigned to any area")]
