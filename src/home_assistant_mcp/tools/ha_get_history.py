
import json
from datetime import datetime, timedelta
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_get_history",
    description="Get historical state changes for an entity",
    inputSchema={
        "type": "object",
        "properties": {
            "entity_id": {
                "type": "string",
                "description": "Entity ID to get history for",
            },
            "hours_ago": {
                "type": "integer",
                "description": "Number of hours of history to retrieve (default: 24)",
                "default": 24,
            },
        },
        "required": ["entity_id"],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    entity_id = arguments["entity_id"]
    hours_ago = arguments.get("hours_ago", 24)

    start_time = datetime.now() - timedelta(hours=hours_ago)
    history = await client.get_history(entity_id=entity_id, start_time=start_time)

    # Flatten and format history
    entries = []
    for entity_history in history:
        for entry in entity_history:
            entries.append(
                {
                    "entity_id": entry.entity_id,
                    "state": entry.state,
                    "last_changed": str(entry.last_changed) if entry.last_changed else None,
                }
            )
    return [
        TextContent(
            type="text",
            text=f"History for {entity_id} (last {hours_ago} hours):\n{json.dumps(entries, indent=2)}",
        )
    ]
