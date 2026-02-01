"""Unit tests for ha_delete_dashboard tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.dashboards import ha_delete_dashboard
from home_assistant_mcp.tool_models import DeleteDashboardInput


class TestDeleteDashboardTool:
    """Tests for ha_delete_dashboard tool."""



    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful dashboard deletion."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.delete_dashboard.return_value = True
        core.client = mock_client

        # Execute tool
        params = DeleteDashboardInput(dashboard_id="test_dashboard")
        result = await ha_delete_dashboard(params)

        # Verify
        assert "Dashboard 'test_dashboard' deleted successfully" in result
        mock_client.delete_dashboard.assert_called_once_with(dashboard_id="test_dashboard")

    @pytest.mark.asyncio
    async def test_execute_different_dashboard_ids(self):
        """Test deleting dashboards with different IDs."""
        mock_client = AsyncMock()
        mock_client.delete_dashboard.return_value = True
        core.client = mock_client

        dashboard_ids = ["lovelace", "energy", "admin_panel", "custom_123"]

        for dashboard_id in dashboard_ids:
            params = DeleteDashboardInput(dashboard_id=dashboard_id)
            result = await ha_delete_dashboard(params)
            assert f"Dashboard '{dashboard_id}' deleted successfully" in result

    @pytest.mark.asyncio
    async def test_execute_with_special_characters(self):
        """Test deleting dashboard with special characters in ID."""
        mock_client = AsyncMock()
        mock_client.delete_dashboard.return_value = True
        core.client = mock_client

        params = DeleteDashboardInput(dashboard_id="my-custom-dashboard_123")
        result = await ha_delete_dashboard(params)

        assert "Dashboard 'my-custom-dashboard_123' deleted successfully" in result
        mock_client.delete_dashboard.assert_called_once_with(dashboard_id="my-custom-dashboard_123")
