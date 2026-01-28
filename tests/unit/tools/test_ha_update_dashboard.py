"""Unit tests for ha_update_dashboard tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_update_dashboard import TOOL_DEF, execute
from home_assistant_mcp.models import Dashboard


class TestUpdateDashboardTool:
    """Tests for ha_update_dashboard tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_update_dashboard"
        assert "Update an existing dashboard" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "dashboard_id" in TOOL_DEF.inputSchema["required"]

        # Check optional properties
        props = TOOL_DEF.inputSchema["properties"]
        assert "title" in props
        assert "icon" in props
        assert "show_in_sidebar" in props

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

        # Execute tool
        arguments = {
            "dashboard_id": "test_dash",
            "title": "New Title",
        }
        result = await execute(mock_client, arguments)

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Dashboard updated successfully" in result[0].text
        assert "New Title" in result[0].text

        mock_client.update_dashboard.assert_called_once_with(
            "test_dash",
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

        arguments = {
            "dashboard_id": "energy",
            "icon": "mdi:flash",
        }
        result = await execute(mock_client, arguments)

        mock_client.update_dashboard.assert_called_once_with(
            "energy",
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

        arguments = {
            "dashboard_id": "hidden",
            "show_in_sidebar": False,
        }
        result = await execute(mock_client, arguments)

        mock_client.update_dashboard.assert_called_once_with(
            "hidden",
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

        arguments = {
            "dashboard_id": "multi",
            "title": "Updated Dashboard",
            "icon": "mdi:update",
            "show_in_sidebar": True,
        }
        result = await execute(mock_client, arguments)

        # Verify all updates were passed (excluding dashboard_id)
        mock_client.update_dashboard.assert_called_once_with(
            "multi",
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

        arguments = {
            "dashboard_id": "test",
            "title": "New Title",
        }
        result = await execute(mock_client, arguments)

        # Verify dashboard_id was used as first arg, not in kwargs
        call_args = mock_client.update_dashboard.call_args
        assert call_args[0][0] == "test"
        assert "dashboard_id" not in call_args[1]
        assert call_args[1]["title"] == "New Title"
