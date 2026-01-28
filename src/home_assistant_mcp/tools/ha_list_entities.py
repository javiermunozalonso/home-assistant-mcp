
import json
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_list_entities",
    description="List all entities or filter by domain (e.g., light, switch, sensor)",
    inputSchema={
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Optional domain to filter entities (e.g., 'light', 'switch', 'sensor', 'climate')",
            },
        },
        "required": [],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    domain = arguments.get("domain")
    if domain:
        entities = await client.get_entities_by_domain(domain)
    else:
        entities = await client.get_states()

    # Return simplified list
    entity_list = [
        {
            "entity_id": e.entity_id,
            "state": e.state,
            "friendly_name": e.attributes.get("friendly_name", e.entity_id),
        }
        for e in entities
    ]
    return [
        TextContent(
            type="text",
            text=f"Found {len(entity_list)} entities:\n{json.dumps(entity_list, indent=2)}",
        )
    ]
