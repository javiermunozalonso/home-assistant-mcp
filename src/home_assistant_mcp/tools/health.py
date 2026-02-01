"""Health check and configuration tools for Home Assistant MCP server."""

import json
import logging

from ..client import HomeAssistantError
from ..core import get_client, mcp
from ..tool_models import GetConfigInput, ResponseFormat

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_health_check() -> str:
    """Check if Home Assistant API is accessible and running.

    This tool verifies connectivity to the Home Assistant server and returns
    the API status message. Use this before other operations to verify that
    the connection is working properly.

    Examples:
        - Check connectivity: ha_health_check()

    Returns:
        str: API status message indicating Home Assistant is running
    """
    try:
        ha_client = get_client()
        result = await ha_client.check_api()
        return f"✓ Home Assistant API is running: {result.message}"
    except HomeAssistantError as e:
        logger.error(f"Health check failed: {e}")
        return f"✗ Health check failed: {e}"
    except Exception as e:
        logger.exception("Unexpected error in health check")
        return f"✗ Unexpected error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_get_config(params: GetConfigInput) -> str:
    """Get Home Assistant configuration information.

    Returns configuration details including location, time zone, version,
    and other settings.

    Examples:
        - Get config: ha_get_config()
        - Get as JSON: ha_get_config(response_format="json")

    Args:
        params: Configuration parameters (optional response_format)

    Returns:
        str: Configuration information in requested format
    """
    try:
        ha_client = get_client()
        config = await ha_client.get_config()

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(config.model_dump(), indent=2)
        else:
            # Markdown format
            return f"""# Home Assistant Configuration

**Location**: {config.location_name}
**Latitude**: {config.latitude}
**Longitude**: {config.longitude}
**Elevation**: {config.elevation}m
**Time Zone**: {config.time_zone}
**Unit System**: {config.unit_system.get('length', 'N/A')} (length), {config.unit_system.get('temperature', 'N/A')} (temp)
**Version**: {config.version}
**Config Directory**: {config.config_dir}
"""
    except Exception as e:
        logger.exception("Error getting configuration")
        return f"✗ Error: {e}"
