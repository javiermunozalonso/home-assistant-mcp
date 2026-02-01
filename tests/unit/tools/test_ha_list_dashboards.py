"""Unit tests for ha_list_dashboards tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.dashboards import ha_list_dashboards
from home_assistant_mcp.tool_models import ListDashboardsInput
from home_assistant_mcp.models import Dashboard


class TestListDashboardsTool:
    """Tests for ha_list_dashboards tool."""



    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test listing dashboards successfully."""
        # Create mock client with dashboards
        mock_client = AsyncMock()
        mock_dashboards = [
            Dashboard(
                id="lovelace",
                url_path="lovelace",
                title="Home",
                icon="mdi:home",
                show_in_sidebar=True,
                require_admin=False,
            ),
            Dashboard(
                id="energy",
                url_path="energy",
                title="Energy",
                icon="mdi:lightning-bolt",
                show_in_sidebar=True,
                require_admin=False,
            ),
        ]
        mock_client.list_dashboards.return_value = mock_dashboards
        core.client = mock_client

        # Execute tool
        result = await ha_list_dashboards(ListDashboardsInput(response_format="json"))

        # Verify
        json_data = json.loads(result)
        dashboards = json_data["dashboards"]
        assert len(dashboards) == 2
        assert dashboards[0]["id"] == "lovelace"
        assert dashboards[0]["title"] == "Home"
        assert dashboards[0]["icon"] == "mdi:home"
        assert dashboards[1]["id"] == "energy"

        mock_client.list_dashboards.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_empty_dashboards(self):
        """Test listing when no dashboards exist."""
        mock_client = AsyncMock()
        mock_client.list_dashboards.return_value = []
        core.client = mock_client

        result = await ha_list_dashboards(ListDashboardsInput(response_format="json"))
        
        json_data = json.loads(result)
        dashboards = json_data["dashboards"]
        assert len(dashboards) == 0

    @pytest.mark.asyncio
    async def test_execute_dashboard_with_admin_requirement(self):
        """Test listing dashboards with admin requirement."""
        mock_client = AsyncMock()
        mock_dashboards = [
            Dashboard(
                id="admin_panel",
                url_path="admin",
                title="Admin Panel",
                icon="mdi:shield-account",
                show_in_sidebar=False,
                require_admin=True,
            ),
        ]
        mock_client.list_dashboards.return_value = mock_dashboards
        core.client = mock_client

        result = await ha_list_dashboards(ListDashboardsInput(response_format="json"))

        json_data = json.loads(result)
        dashboards = json_data["dashboards"]
        assert dashboards[0]["require_admin"] is True
        assert dashboards[0]["show_in_sidebar"] is False

    @pytest.mark.asyncio
    async def test_execute_includes_all_dashboard_fields(self):
        """Test that all dashboard fields are included."""
        mock_client = AsyncMock()
        mock_dashboards = [
            Dashboard(
                id="test_dash",
                url_path="test-dashboard",
                title="Test Dashboard",
                icon="mdi:test-tube",
                show_in_sidebar=True,
                require_admin=False,
            ),
        ]
        mock_client.list_dashboards.return_value = mock_dashboards
        core.client = mock_client

        result = await ha_list_dashboards(ListDashboardsInput(response_format="json"))

        json_data = json.loads(result)
        dashboards = json_data["dashboards"]
        dashboard = dashboards[0]

        # Verify all expected fields are present
        assert "id" in dashboard
        assert "url_path" in dashboard
        assert "title" in dashboard
        assert "icon" in dashboard
        assert "show_in_sidebar" in dashboard
        assert "require_admin" in dashboard
