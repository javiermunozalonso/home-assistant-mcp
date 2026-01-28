
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
    name="ha_create_dashboard",
    description="Create a new Lovelace dashboard",
    inputSchema={
        "type": "object",
        "properties": {
            "url_path": {
                "type": "string",
                "description": "URL path for the dashboard (e.g., 'my-dashboard')",
            },
            "title": {
                "type": "string",
                "description": "Dashboard title",
            },
            "icon": {
                "type": "string",
                "description": "Optional dashboard icon (e.g., 'mdi:home')",
            },
            "show_in_sidebar": {
                "type": "boolean",
                "description": "Show in sidebar (default: true)",
            },
            "require_admin": {
                "type": "boolean",
                "description": "Require admin access (default: false)",
            },
        },
        "required": ["url_path", "title"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    url_path = arguments["url_path"]
    title = arguments["title"]
    icon = arguments.get("icon")
    show_in_sidebar = arguments.get("show_in_sidebar", True)
    require_admin = arguments.get("require_admin", False)

    dashboard = await client.create_dashboard(
        url_path=url_path,
        title=title,
        icon=icon,
        show_in_sidebar=show_in_sidebar,
        require_admin=require_admin,
    )
    return [
        TextContent(
            type="text",
            text=f"Dashboard created successfully:\n{format_response(dashboard)}",
        )
    ]
