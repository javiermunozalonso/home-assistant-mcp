"""Area and room management tools for Home Assistant MCP server."""

import json
import logging

from ..core import get_client, mcp
from ..tool_models import (
    GetAreaDevicesInput,
    GetAreaEntitiesInput,
    GetEntityAreaInput,
    ListAreasInput,
    ResponseFormat,
)

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_list_areas(params: ListAreasInput) -> str:
    """List all configured areas.

    Returns all areas/rooms configured in Home Assistant.

    Examples:
        - List areas: ha_list_areas()
        - Get as JSON: ha_list_areas(response_format="json")

    Args:
        params: Parameters including response format

    Returns:
        str: List of areas
    """
    try:
        ha_client = get_client()
        areas = await ha_client.get_areas()

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"areas": areas}, indent=2)
        else:
            lines = [f"# Areas ({len(areas)} total)", ""]
            for i, area in enumerate(areas, 1):
                lines.append(f"{i}. {area}")
            return "\n".join(lines)

    except Exception as e:
        logger.exception("Error listing areas")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_get_area_entities(params: GetAreaEntitiesInput) -> str:
    """Get all entities in an area.

    Returns entities within a specific area, optionally filtered by domain.

    Examples:
        - Get all entities: ha_get_area_entities(area="kitchen")
        - Get lights only: ha_get_area_entities(area="bedroom", domain="light")

    Args:
        params: Parameters including area name/ID and optional domain filter

    Returns:
        str: List of entities in the area
    """
    try:
        ha_client = get_client()
        entities = await ha_client.get_area_entities(
            area=params.area,
            domain=params.domain,
        )

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"area": params.area, "entities": entities}, indent=2)
        else:
            lines = [f"# Entities in '{params.area}' ({len(entities)} total)"]
            if params.domain:
                lines.append(f"**Domain filter**: {params.domain}")
            lines.append("")
            for entity in entities:
                lines.append(f"- {entity}")
            return "\n".join(lines)

    except Exception as e:
        logger.exception(f"Error getting entities for area {params.area}")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_get_area_devices(params: GetAreaDevicesInput) -> str:
    """Get all devices in an area.

    Returns devices within a specific area.

    Examples:
        - Get devices: ha_get_area_devices(area="living_room")

    Args:
        params: Parameters including area name/ID

    Returns:
        str: List of devices in the area
    """
    try:
        ha_client = get_client()
        devices = await ha_client.get_area_devices(area=params.area)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps({"area": params.area, "devices": devices}, indent=2)
        else:
            lines = [f"# Devices in '{params.area}' ({len(devices)} total)", ""]
            for device in devices:
                lines.append(f"- {device}")
            return "\n".join(lines)

    except Exception as e:
        logger.exception(f"Error getting devices for area {params.area}")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_get_entity_area(params: GetEntityAreaInput) -> str:
    """Get the area name for an entity.

    Returns which area/room an entity is located in.

    Examples:
        - Get entity area: ha_get_entity_area(entity_id="light.kitchen_main")

    Args:
        params: Parameters including entity_id

    Returns:
        str: Area name or message if not assigned to an area
    """
    try:
        ha_client = get_client()
        area = await ha_client.get_entity_area(entity_id=params.entity_id)

        if area:
            return f"Entity '{params.entity_id}' is in area: {area}"
        else:
            return f"Entity '{params.entity_id}' is not assigned to any area"

    except Exception as e:
        logger.exception(f"Error getting area for {params.entity_id}")
        return f"✗ Error: {e}"
