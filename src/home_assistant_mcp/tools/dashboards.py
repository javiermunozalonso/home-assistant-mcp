"""Dashboard management tools for Home Assistant MCP server."""

import json
import logging

from ..core import get_client, mcp
from ..tool_models import (
    CreateDashboardInput,
    DeleteDashboardInput,
    GetDashboardInput,
    ListDashboardsInput,
    ResponseFormat,
    UpdateDashboardInput,
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
async def ha_list_dashboards(params: ListDashboardsInput) -> str:
    """List all Lovelace dashboards.

    Returns all configured dashboards in Home Assistant.

    Examples:
        - List dashboards: ha_list_dashboards()
        - Get as JSON: ha_list_dashboards(response_format="json")

    Args:
        params: Parameters including response format

    Returns:
        str: List of dashboards
    """
    try:
        ha_client = get_client()
        dashboards = await ha_client.list_dashboards()

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(
                {"dashboards": [d.model_dump() for d in dashboards]},
                indent=2
            )
        else:
            lines = [f"# Dashboards ({len(dashboards)} total)", ""]
            lines.append("| ID | Title | URL Path | Sidebar |")
            lines.append("|----|-------|----------|---------|")
            for d in dashboards:
                sidebar = "✓" if d.show_in_sidebar else "✗"
                lines.append(f"| {d.id} | {d.title} | {d.url_path} | {sidebar} |")
            return "\n".join(lines)

    except Exception as e:
        logger.exception("Error listing dashboards")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    }
)
async def ha_get_dashboard(params: GetDashboardInput) -> str:
    """Get configuration of a specific dashboard.

    Returns the full configuration of a dashboard.

    Examples:
        - Get default: ha_get_dashboard()
        - Get specific: ha_get_dashboard(url_path="energy")

    Args:
        params: Parameters including optional url_path

    Returns:
        str: Dashboard configuration
    """
    try:
        ha_client = get_client()
        config = await ha_client.get_dashboard_config(url_path=params.url_path)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(config.model_dump(), indent=2, default=str)
        else:
            return f"""# Dashboard Configuration

**Views**: {len(config.views)}
**Configured**: {config is not None}

Use response_format="json" for full configuration details.
"""

    except Exception as e:
        logger.exception(f"Error getting dashboard {params.url_path}")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,  # Creating same dashboard twice fails
        "openWorldHint": True,
    }
)
async def ha_create_dashboard(params: CreateDashboardInput) -> str:
    """Create a new Lovelace dashboard.

    Creates a new dashboard with specified configuration.

    Examples:
        - Create: ha_create_dashboard(url_path="energy", title="Energy Monitor")
        - With icon: ha_create_dashboard(url_path="cameras", title="Cameras", icon="mdi:cctv")

    Args:
        params: Dashboard creation parameters

    Returns:
        str: Created dashboard information
    """
    try:
        ha_client = get_client()
        dashboard = await ha_client.create_dashboard(
            url_path=params.url_path,
            title=params.title,
            icon=params.icon,
            show_in_sidebar=params.show_in_sidebar,
            require_admin=params.require_admin,
        )

        return f"""✓ Dashboard created successfully

**ID**: {dashboard.id}
**Title**: {dashboard.title}
**URL Path**: {dashboard.url_path}
**Icon**: {dashboard.icon or 'None'}
**Show in Sidebar**: {dashboard.show_in_sidebar}
"""

    except Exception as e:
        logger.exception(f"Error creating dashboard {params.url_path}")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,  # Updating with same values has no effect
        "openWorldHint": True,
    }
)
async def ha_update_dashboard(params: UpdateDashboardInput) -> str:
    """Update an existing dashboard.

    Updates dashboard properties like title, icon, etc.

    Examples:
        - Update title: ha_update_dashboard(dashboard_id="energy", title="Energy Monitoring")
        - Update icon: ha_update_dashboard(dashboard_id="cameras", icon="mdi:camera")

    Args:
        params: Dashboard update parameters

    Returns:
        str: Updated dashboard information
    """
    try:
        ha_client = get_client()

        updates = {}
        if params.title is not None:
            updates["title"] = params.title
        if params.icon is not None:
            updates["icon"] = params.icon
        if params.show_in_sidebar is not None:
            updates["show_in_sidebar"] = params.show_in_sidebar
        if params.require_admin is not None:
            updates["require_admin"] = params.require_admin

        dashboard = await ha_client.update_dashboard(
            dashboard_id=params.dashboard_id,
            **updates
        )

        return f"""✓ Dashboard updated successfully

**ID**: {dashboard.id}
**Title**: {dashboard.title}
**URL Path**: {dashboard.url_path}
"""

    except Exception as e:
        logger.exception(f"Error updating dashboard {params.dashboard_id}")
        return f"✗ Error: {e}"


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,  # Deleting already deleted dashboard is ok
        "openWorldHint": True,
    }
)
async def ha_delete_dashboard(params: DeleteDashboardInput) -> str:
    """Delete a dashboard.

    Permanently removes a dashboard.

    Examples:
        - Delete: ha_delete_dashboard(dashboard_id="old_dashboard")

    Args:
        params: Dashboard deletion parameters

    Returns:
        str: Deletion confirmation
    """
    try:
        ha_client = get_client()
        await ha_client.delete_dashboard(dashboard_id=params.dashboard_id)

        return f"✓ Dashboard '{params.dashboard_id}' deleted successfully"

    except Exception as e:
        logger.exception(f"Error deleting dashboard {params.dashboard_id}")
        return f"✗ Error: {e}"
