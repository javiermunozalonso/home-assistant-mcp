"""Unit tests for ha_update_dashboard tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.dashboards import ha_update_dashboard
from home_assistant_mcp.tool_models import UpdateDashboardInput
from home_assistant_mcp.models import Dashboard


class TestUpdateDashboardTool:
    """Tests for ha_update_dashboard tool."""



    @pytest.mark.asyncio
    async def test_execute_update_title(self):
        """Test updating dashboard title."""
        # Create mock client
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="test_dash",
            url_path="test",
            title="New Title",
            icon="mdi:home",
            show_in_sidebar=True,
            require_admin=False,
        )
        mock_client.update_dashboard.return_value = mock_dashboard
        core.client = mock_client

        # Execute tool
        params = UpdateDashboardInput(
            dashboard_id="test_dash",
            title="New Title",
        )
        result = await ha_update_dashboard(params)

        # Verify
        assert "Dashboard updated successfully" in result
        assert "New Title" in result

        mock_client.update_dashboard.assert_called_once_with(
            dashboard_id="test_dash",
            title="New Title",
        )

    @pytest.mark.asyncio
    async def test_execute_update_icon(self):
        """Test updating dashboard icon."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="energy",
            url_path="energy",
            title="Energy",
            icon="mdi:flash",
            show_in_sidebar=True,
            require_admin=False,
        )
        mock_client.update_dashboard.return_value = mock_dashboard
        core.client = mock_client

        params = UpdateDashboardInput(
            dashboard_id="energy",
            icon="mdi:flash",
        )
        await ha_update_dashboard(params)

        mock_client.update_dashboard.assert_called_once_with(
            dashboard_id="energy",
            icon="mdi:flash",
        )

    @pytest.mark.asyncio
    async def test_execute_update_sidebar_visibility(self):
        """Test updating dashboard sidebar visibility."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="hidden",
            url_path="hidden",
            title="Hidden",
            icon=None,
            show_in_sidebar=False,
            require_admin=False,
        )
        mock_client.update_dashboard.return_value = mock_dashboard
        core.client = mock_client

        params = UpdateDashboardInput(
            dashboard_id="hidden",
            show_in_sidebar=False,
        )
        await ha_update_dashboard(params)

        mock_client.update_dashboard.assert_called_once_with(
            dashboard_id="hidden",
            show_in_sidebar=False,
        )

    @pytest.mark.asyncio
    async def test_execute_update_multiple_fields(self):
        """Test updating multiple dashboard fields."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="multi",
            url_path="multi",
            title="Updated Dashboard",
            icon="mdi:update",
            show_in_sidebar=True,
            require_admin=False,
        )
        mock_client.update_dashboard.return_value = mock_dashboard
        core.client = mock_client

        params = UpdateDashboardInput(
            dashboard_id="multi",
            title="Updated Dashboard",
            icon="mdi:update",
            show_in_sidebar=True,
        )
        await ha_update_dashboard(params)

        # Verify all updates were passed (excluding dashboard_id)
        mock_client.update_dashboard.assert_called_once_with(
            dashboard_id="multi",
            title="Updated Dashboard",
            icon="mdi:update",
            show_in_sidebar=True,
        )

    @pytest.mark.asyncio
    async def test_execute_filters_dashboard_id(self):
        """Test that dashboard_id is not passed as an update parameter."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="test",
            url_path="test",
            title="Test",
            icon=None,
            show_in_sidebar=True,
            require_admin=False,
        )
        mock_client.update_dashboard.return_value = mock_dashboard
        core.client = mock_client

        params = UpdateDashboardInput(
            dashboard_id="test",
            title="New Title",
        )
        await ha_update_dashboard(params)

        # Verify dashboard_id was used as kwarg
        call_args = mock_client.update_dashboard.call_args
        assert call_args[1]["dashboard_id"] == "test"
        assert call_args[1]["title"] == "New Title"
