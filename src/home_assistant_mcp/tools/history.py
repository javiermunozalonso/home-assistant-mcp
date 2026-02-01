"""Historical state data tools for Home Assistant MCP server."""

import json
import logging

from ..core import get_client, mcp
from ..tool_models import GetHistoryInput, ResponseFormat

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_get_history(params: GetHistoryInput) -> str:
    """Get historical state changes for entities.

    Returns state history for specified time period.

    Examples:
        - Get recent history: ha_get_history(entity_id="sensor.temperature")
        - Limit results: ha_get_history(entity_id="light.living_room", limit=20)

    Args:
        params: History parameters including entity_id, time range, and pagination

    Returns:
        str: Historical state changes
    """
    try:
        ha_client = get_client()
        history = await ha_client.get_history(
            entity_id=params.entity_id,
            start_time=params.start_time,
            end_time=params.end_time,
        )

        # Flatten history and apply pagination
        all_entries = []
        for entity_history in history:
            all_entries.extend(entity_history)

        total = len(all_entries)
        start = params.offset
        end = min(start + params.limit, total)
        paginated = all_entries[start:end]
        has_more = end < total

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({
                "total": total,
                "count": len(paginated),
                "offset": params.offset,
                "limit": params.limit,
                "has_more": has_more,
                "next_offset": end if has_more else None,
                "entries": [e.model_dump(mode="json") for e in paginated],
            }, indent=2, default=str)
        else:
            lines = [f"# History (Showing {start + 1}-{end} of {total})", ""]
            for entry in paginated:
                lines.append(f"- **{entry.entity_id}**: {entry.state} at {entry.last_changed}")
            if has_more:
                lines.append("")
                lines.append(f"*Use offset={end} to see next {params.limit} entries*")
            return "\n".join(lines)

    except Exception as e:
        logger.exception("Error getting history")
        return f"✗ Error: {e}"
