
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_health_check",
    description="Check if Home Assistant API is accessible and running",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    result = await client.check_api()
    return [TextContent(type="text", text=f"Home Assistant API is running: {result.message}")]
