
import json
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_list_areas",
    description="List all configured areas in Home Assistant",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
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
