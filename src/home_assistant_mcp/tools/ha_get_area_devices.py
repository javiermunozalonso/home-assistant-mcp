
import json
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
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
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    area = arguments["area"]
    devices = await client.get_area_devices(area)
    return [
        TextContent(
            type="text",
            text=f"Found {len(devices)} devices in area '{area}':\n{json.dumps(devices, indent=2)}",
        )
    ]
