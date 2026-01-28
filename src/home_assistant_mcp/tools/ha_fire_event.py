
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_fire_event",
    description="Fire a custom event in Home Assistant",
    inputSchema={
        "type": "object",
        "properties": {
            "event_type": {
                "type": "string",
                "description": "Type of event to fire",
            },
            "event_data": {
                "type": "object",
                "description": "Optional data to include with the event",
            },
        },
        "required": ["event_type"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    event_type = arguments["event_type"]
    event_data = arguments.get("event_data", {})
    await client.fire_event(event_type, event_data)
    return [TextContent(type="text", text=f"Event '{event_type}' fired successfully.")]
