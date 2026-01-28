
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
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
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    url_path = arguments.get("url_path")
    config = await client.get_dashboard_config(url_path)
    return [TextContent(type="text", text=format_response(config))]
