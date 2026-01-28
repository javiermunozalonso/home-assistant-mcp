
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
    name="ha_get_config",
    description="Get Home Assistant configuration including version, location, and loaded components",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    result = await client.get_config()
    return [TextContent(type="text", text=format_response(result))]
