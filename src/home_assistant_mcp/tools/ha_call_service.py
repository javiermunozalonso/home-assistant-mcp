
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient
from .utils import format_response

TOOL_DEF = Tool(
    name="ha_call_service",
    description="Call a Home Assistant service to control devices",
    inputSchema={
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Service domain (e.g., 'light', 'switch', 'climate')",
            },
            "service": {
                "type": "string",
                "description": "Service name (e.g., 'turn_on', 'turn_off', 'toggle')",
            },
            "entity_id": {
                "type": "string",
                "description": "Target entity ID or comma-separated list of IDs",
            },
            "data": {
                "type": "object",
                "description": "Additional service data (e.g., brightness, color_temp)",
            },
        },
        "required": ["domain", "service"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    domain = arguments["domain"]
    service = arguments["service"]
    entity_id = arguments.get("entity_id")
    data = arguments.get("data", {})

    # Handle comma-separated entity IDs
    if entity_id and "," in entity_id:
        entity_id = [e.strip() for e in entity_id.split(",")]

    result = await client.call_service(domain, service, entity_id=entity_id, data=data)
    return [
        TextContent(
            type="text",
            text=f"Service {domain}.{service} called successfully.\nChanged states: {format_response(result.changed_states)}",
        )
    ]
