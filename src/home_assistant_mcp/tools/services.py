"""Service management and calling tools for Home Assistant MCP server."""

import json
import logging

from ..core import get_client, mcp
from ..tool_models import CallServiceInput, ListServicesInput, ResponseFormat

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_list_services(params: ListServicesInput) -> str:
    """List all available Home Assistant services.

    Returns a list of all services grouped by domain.

    Examples:
        - List all services: ha_list_services()
        - Get as JSON: ha_list_services(response_format="json")

    Args:
        params: Parameters including pagination and format

    Returns:
        str: List of services in requested format
    """
    try:
        ha_client = get_client()
        services = await ha_client.get_services()

        # Calculate pagination
        total = len(services)
        start = params.offset
        end = min(start + params.limit, total)
        paginated = services[start:end]
        has_more = end < total

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({
                "total": total,
                "count": len(paginated),
                "offset": params.offset,
                "limit": params.limit,
                "has_more": has_more,
                "next_offset": end if has_more else None,
                "services": [s.model_dump() for s in paginated],
            }, indent=2)
        else:
            # Markdown format
            lines = [f"# Services (Showing {start + 1}-{end} of {total})", ""]

            for domain in paginated:
                lines.append(f"## {domain.domain}")
                for service_name, service_def in domain.services.items():
                    desc = service_def.get("description", "No description")
                    lines.append(f"- **{service_name}**: {desc}")
                lines.append("")

            if has_more:
                lines.append(f"*Use offset={end} to see next {params.limit} services*")

            return "\n".join(lines)

    except Exception as e:
        logger.exception("Error listing services")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_call_service(params: CallServiceInput) -> str:
    """Call a Home Assistant service to control devices.

    Executes a service call with optional entity targets and data.

    Examples:
        - Turn on light: ha_call_service(domain="light", service="turn_on", entity_id="light.living_room")
        - Set brightness: ha_call_service(domain="light", service="turn_on", entity_id="light.kitchen", data={"brightness": 128})

    Args:
        params: Service parameters including domain, service name, entity_id, and data

    Returns:
        str: Service call result
    """
    try:
        ha_client = get_client()

        # Handle comma-separated entity IDs
        entity_id = params.entity_id
        if entity_id and "," in entity_id:
            entity_id = [e.strip() for e in entity_id.split(",")]

        result = await ha_client.call_service(
            domain=params.domain,
            service=params.service,
            entity_id=entity_id,
            data=params.data or {},
        )

        changed_entities = [
            f"{e.entity_id} → {e.state}"
            for e in result.changed_states
        ]

        return f"""✓ Service {params.domain}.{params.service} called successfully

Changed states:
{chr(10).join(f"  - {e}" for e in changed_entities) if changed_entities else "  (no state changes reported)"}
"""

    except Exception as e:
        logger.exception(f"Error calling service {params.domain}.{params.service}")
        return f"✗ Error: {e}"
