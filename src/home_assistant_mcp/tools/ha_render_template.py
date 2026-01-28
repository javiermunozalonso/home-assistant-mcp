
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_render_template",
    description="Render a Home Assistant Jinja2 template. Useful for advanced queries using HA template functions like areas(), area_entities(), states(), etc.",
    inputSchema={
        "type": "object",
        "properties": {
            "template": {
                "type": "string",
                "description": "Jinja2 template string (e.g., '{{ states(\"sensor.temperature\") }}' or '{{ areas() | list }}')",
            },
        },
        "required": ["template"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    template = arguments["template"]
    result = await client.render_template(template)
    return [TextContent(type="text", text=f"Template result:\n{result}")]
