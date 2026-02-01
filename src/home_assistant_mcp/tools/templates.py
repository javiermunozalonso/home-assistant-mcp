"""Jinja2 template rendering tools for Home Assistant MCP server."""

import logging

from ..core import get_client, mcp
from ..tool_models import RenderTemplateInput

logger = logging.getLogger(__name__)


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_render_template(params: RenderTemplateInput) -> str:
    """Render a Jinja2 template using Home Assistant's template engine.

    Evaluates Jinja2 templates with access to Home Assistant state and functions.

    Examples:
        - Simple: ha_render_template(template="{{ states('light.living_room') }}")
        - Complex: ha_render_template(template="{{ states | count }}")

    Args:
        params: Parameters including the template string

    Returns:
        str: Rendered template result
    """
    try:
        ha_client = get_client()
        result = await ha_client.render_template(template=params.template)
        return f"Template result: {result}"

    except Exception as e:
        logger.exception("Error rendering template")
        return f"✗ Error: {e}"
