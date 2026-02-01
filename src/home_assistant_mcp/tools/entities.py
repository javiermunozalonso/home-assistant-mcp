"""Entity management tools for Home Assistant MCP server."""

import json
import logging

from ..core import get_client, mcp
from ..tool_models import GetEntityStateInput, ListEntitiesInput, ResponseFormat

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_list_entities(params: ListEntitiesInput) -> str:
    """List all entities or filter by domain.

    Returns a list of entities with their current states. Supports pagination
    for large installations and filtering by domain (e.g., only lights).

    Examples:
        - List all entities: ha_list_entities()
        - List lights only: ha_list_entities(domain="light")
        - Paginate results: ha_list_entities(limit=20, offset=20)
        - Get as JSON: ha_list_entities(response_format="json")

    Args:
        params: Parameters including domain filter, pagination, and format

    Returns:
        str: List of entities in requested format
    """
    try:
        ha_client = get_client()

        # Get entities (filtered by domain if specified)
        if params.domain:
            entities = await ha_client.get_entities_by_domain(params.domain)
        else:
            entities = await ha_client.get_states()

        # Calculate pagination
        total = len(entities)
        start = params.offset
        end = min(start + params.limit, total)
        paginated = entities[start:end]
        has_more = end < total

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({
                "total": total,
                "count": len(paginated),
                "offset": params.offset,
                "limit": params.limit,
                "has_more": has_more,
                "next_offset": end if has_more else None,
                "entities": [
                    {
                        "entity_id": e.entity_id,
                        "state": e.state,
                        "friendly_name": e.attributes.get("friendly_name", e.entity_id),
                        "last_changed": e.last_changed.isoformat() if e.last_changed else None,
                    }
                    for e in paginated
                ],
            }, indent=2)
        else:
            # Markdown format
            lines = [f"# Entities (Showing {start + 1}-{end} of {total})"]
            if params.domain:
                lines.append(f"**Domain**: {params.domain}")
            lines.append("")
            lines.append("| Entity ID | State | Friendly Name |")
            lines.append("|-----------|-------|---------------|")

            for e in paginated:
                friendly_name = e.attributes.get("friendly_name", e.entity_id)
                lines.append(f"| {e.entity_id} | {e.state} | {friendly_name} |")

            if has_more:
                lines.append("")
                lines.append(f"*Use offset={end} to see next {params.limit} entities*")

            return "\n".join(lines)

    except Exception as e:
        logger.exception("Error listing entities")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_get_entity_state(params: GetEntityStateInput) -> str:
    """Get detailed state information for a specific entity.

    Returns the current state, attributes, and metadata for an entity.

    Examples:
        - Get light state: ha_get_entity_state(entity_id="light.living_room")
        - Get as JSON: ha_get_entity_state(entity_id="sensor.temperature", response_format="json")

    Args:
        params: Parameters including entity_id and response_format

    Returns:
        str: Entity state information in requested format
    """
    try:
        ha_client = get_client()
        state = await ha_client.get_state(params.entity_id)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(state.model_dump(), indent=2, default=str)
        else:
            # Markdown format
            friendly_name = state.attributes.get("friendly_name", params.entity_id)
            lines = [
                f"# {friendly_name}",
                f"**Entity ID**: {state.entity_id}",
                f"**State**: {state.state}",
                f"**Last Changed**: {state.last_changed}",
                f"**Last Updated**: {state.last_updated}",
                "",
                "## Attributes",
            ]

            for key, value in state.attributes.items():
                lines.append(f"- **{key}**: {value}")

            return "\n".join(lines)

    except Exception as e:
        logger.exception(f"Error getting state for {params.entity_id}")
        return f"✗ Error: {e}. Use ha_list_entities to see available entities."
