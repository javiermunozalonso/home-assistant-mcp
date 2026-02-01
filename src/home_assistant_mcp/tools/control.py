"""Device control tools for Home Assistant MCP server."""

import logging

from ..core import get_client, mcp
from ..tool_models import ToggleInput, TurnOffInput, TurnOnInput

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_turn_on(params: TurnOnInput) -> str:
    """Turn on an entity with optional parameters.

    Turns on lights, switches, or other controllable entities. Supports
    additional parameters like brightness and color for lights.

    Examples:
        - Turn on light: ha_turn_on(entity_id="light.living_room")
        - Set brightness: ha_turn_on(entity_id="light.kitchen", brightness=128)
        - Set brightness %: ha_turn_on(entity_id="light.bedroom", brightness_pct=50)
        - Set color: ha_turn_on(entity_id="light.rgb", rgb_color=[255, 0, 0])

    Common errors:
        - Entity not found: Use ha_list_entities to find valid entity IDs
        - Domain not supported: Only works with controllable entities

    Args:
        params: Turn on parameters including entity_id and optional settings

    Returns:
        str: Result of turn on operation
    """
    try:
        ha_client = get_client()

        kwargs = {}
        if params.brightness is not None:
            kwargs["brightness"] = params.brightness
        if params.brightness_pct is not None:
            kwargs["brightness_pct"] = params.brightness_pct
        if params.color_temp is not None:
            kwargs["color_temp"] = params.color_temp
        if params.rgb_color is not None:
            kwargs["rgb_color"] = params.rgb_color

        result = await ha_client.turn_on(params.entity_id, **kwargs)

        changed = [f"{e.entity_id} → {e.state}" for e in result.changed_states]
        return f"""✓ Turned on {params.entity_id}

Changed states:
{chr(10).join(f"  - {c}" for c in changed) if changed else "  (no state changes reported)"}
"""

    except Exception as e:
        logger.exception(f"Error turning on {params.entity_id}")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_turn_off(params: TurnOffInput) -> str:
    """Turn off an entity.

    Turns off lights, switches, or other controllable entities.

    Examples:
        - Turn off light: ha_turn_off(entity_id="light.living_room")
        - Turn off switch: ha_turn_off(entity_id="switch.coffee_maker")

    Args:
        params: Turn off parameters including entity_id

    Returns:
        str: Result of turn off operation
    """
    try:
        ha_client = get_client()
        result = await ha_client.turn_off(params.entity_id)

        changed = [f"{e.entity_id} → {e.state}" for e in result.changed_states]
        return f"""✓ Turned off {params.entity_id}

Changed states:
{chr(10).join(f"  - {c}" for c in changed) if changed else "  (no state changes reported)"}
"""

    except Exception as e:
        logger.exception(f"Error turning off {params.entity_id}")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,  # Toggle changes state each time
        "openWorldHint": True,
    }
)
async def ha_toggle(params: ToggleInput) -> str:
    """Toggle an entity's state.

    Switches an entity between on and off states.

    Examples:
        - Toggle light: ha_toggle(entity_id="light.living_room")

    Args:
        params: Toggle parameters including entity_id

    Returns:
        str: Result of toggle operation
    """
    try:
        ha_client = get_client()
        result = await ha_client.toggle(params.entity_id)

        changed = [f"{e.entity_id} → {e.state}" for e in result.changed_states]
        return f"""✓ Toggled {params.entity_id}

Changed states:
{chr(10).join(f"  - {c}" for c in changed) if changed else "  (no state changes reported)"}
"""

    except Exception as e:
        logger.exception(f"Error toggling {params.entity_id}")
        return f"✗ Error: {e}"
