"""Event firing tools for Home Assistant MCP server."""

import logging

from ..core import get_client, mcp
from ..tool_models import FireEventInput

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    }
)
async def ha_fire_event(params: FireEventInput) -> str:
    """Fire a custom event.

    Triggers a custom event that can be used in automations.

    Examples:
        - Fire event: ha_fire_event(event_type="my_event")
        - With data: ha_fire_event(event_type="notification", event_data={"message": "Hello"})

    Args:
        params: Event parameters including type and data

    Returns:
        str: Result of firing event
    """
    try:
        ha_client = get_client()
        await ha_client.fire_event(
            event_type=params.event_type,
            event_data=params.event_data or {},
        )
        return f"✓ Event '{params.event_type}' fired successfully"

    except Exception as e:
        logger.exception(f"Error firing event {params.event_type}")
        return f"✗ Error: {e}"
