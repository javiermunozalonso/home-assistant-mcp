
import json
from typing import Any
from mcp.types import Tool, TextContent
from home_assistant_mcp.client import HomeAssistantClient

TOOL_DEF = Tool(
    name="ha_list_services",
    description="List all available services, optionally filtered by domain",
    inputSchema={
        "type": "object",
        "properties": {
            "domain": {
                "type": "string",
                "description": "Optional domain to filter services (e.g., 'light', 'switch')",
            },
        },
        "required": [],
    },
)

async def execute(client: HomeAssistantClient, arguments: dict[str, Any]) -> list[TextContent]:
    services = await client.get_services()
    domain = arguments.get("domain")
    if domain:
        services = [s for s in services if s.domain == domain]

    # Simplified service list
    service_list = []
    for domain_obj in services:
        for service_name, service_def in domain_obj.services.items():
            service_list.append(
                {
                    "service": f"{domain_obj.domain}.{service_name}",
                    "description": service_def.description or "No description",
                }
            )
    return [
        TextContent(
            type="text",
            text=f"Found {len(service_list)} services:\n{json.dumps(service_list, indent=2)}",
        )
    ]
