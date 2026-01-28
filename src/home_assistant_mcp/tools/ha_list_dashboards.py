
import json
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_list_dashboards",
    description="List all Lovelace dashboards",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
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
