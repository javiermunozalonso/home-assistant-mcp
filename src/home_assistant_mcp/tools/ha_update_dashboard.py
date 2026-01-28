
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
    name="ha_update_dashboard",
    description="Update an existing dashboard",
    inputSchema={
        "type": "object",
        "properties": {
            "dashboard_id": {
                "type": "string",
                "description": "Dashboard ID to update",
            },
            "title": {
                "type": "string",
                "description": "New title",
            },
            "icon": {
                "type": "string",
                "description": "New icon",
            },
            "show_in_sidebar": {
                "type": "boolean",
                "description": "Show in sidebar",
            },
        },
        "required": ["dashboard_id"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    dashboard_id = arguments["dashboard_id"]
    updates = {k: v for k, v in arguments.items() if k != "dashboard_id"}
    dashboard = await client.update_dashboard(dashboard_id, **updates)
    return [
        TextContent(
            type="text",
            text=f"Dashboard updated successfully:\n{format_response(dashboard)}",
        )
    ]
