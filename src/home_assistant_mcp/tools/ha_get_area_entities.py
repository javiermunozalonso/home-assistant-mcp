
import json
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_get_area_entities",
    description="Get all entities assigned to a specific area",
    inputSchema={
        "type": "object",
        "properties": {
            "area": {
                "type": "string",
                "description": "Area ID or name (e.g., 'salon', 'kitchen')",
            },
            "domain": {
                "type": "string",
                "description": "Optional domain to filter entities (e.g., 'light', 'switch', 'sensor')",
            },
        },
        "required": ["area"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    area = arguments["area"]
    domain = arguments.get("domain")
    entities = await client.get_area_entities(area, domain=domain)

    # Get states for each entity
    entity_info = []
    for entity_id in entities:
        try:
            state = await client.get_state(entity_id)
            entity_info.append({
                "entity_id": entity_id,
                "state": state.state,
                "friendly_name": state.attributes.get("friendly_name", entity_id),
            })
        except Exception:
            entity_info.append({
                "entity_id": entity_id,
                "state": "unknown",
                "friendly_name": entity_id,
            })

    filter_msg = f" (domain: {domain})" if domain else ""
    return [
        TextContent(
            type="text",
            text=f"Found {len(entities)} entities in area '{area}'{filter_msg}:\n{json.dumps(entity_info, indent=2)}",
        )
    ]
