
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_delete_dashboard",
    description="Delete a dashboard",
    inputSchema={
        "type": "object",
        "properties": {
            "dashboard_id": {
                "type": "string",
                "description": "Dashboard ID to delete",
            },
        },
        "required": ["dashboard_id"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    dashboard_id = arguments["dashboard_id"]
    await client.delete_dashboard(dashboard_id)
    return [TextContent(type="text", text=f"Dashboard '{dashboard_id}' deleted successfully.")]
