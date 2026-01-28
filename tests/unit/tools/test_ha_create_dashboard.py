"""Unit tests for ha_create_dashboard tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_create_dashboard import TOOL_DEF, execute
from home_assistant_mcp.models import Dashboard


class TestCreateDashboardTool:
    """Tests for ha_create_dashboard tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_create_dashboard"
        assert "Create a new Lovelace dashboard" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "url_path" in TOOL_DEF.inputSchema["required"]
        assert "title" in TOOL_DEF.inputSchema["required"]

        # Check properties
        props = TOOL_DEF.inputSchema["properties"]
        assert "icon" in props
        assert "show_in_sidebar" in props
        assert "require_admin" in props

    @pytest.mark.asyncio
    async def test_execute_basic_dashboard(self):
        """Test creating a basic dashboard with required fields only."""
        # Create mock client
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="test_dashboard",
            url_path="test-dashboard",
            title="Test Dashboard",
            icon=None,
            show_in_sidebar=True,
            require_admin=False,
        )
        mock_client.create_dashboard.return_value = mock_dashboard

        # Execute tool
        arguments = {
            "url_path": "test-dashboard",
            "title": "Test Dashboard",
        }
        result = await execute(mock_client, arguments)

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Dashboard created successfully" in result[0].text
        assert "test-dashboard" in result[0].text

        mock_client.create_dashboard.assert_called_once_with(
            url_path="test-dashboard",
            title="Test Dashboard",
            icon=None,
            show_in_sidebar=True,
            require_admin=False,
        )

    @pytest.mark.asyncio
    async def test_execute_dashboard_with_icon(self):
        """Test creating dashboard with custom icon."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="energy_dash",
            url_path="energy",
            title="Energy",
            icon="mdi:lightning-bolt",
            show_in_sidebar=True,
            require_admin=False,
        )
        mock_client.create_dashboard.return_value = mock_dashboard

        arguments = {
            "url_path": "energy",
            "title": "Energy",
            "icon": "mdi:lightning-bolt",
        }
        result = await execute(mock_client, arguments)

        mock_client.create_dashboard.assert_called_once_with(
            url_path="energy",
            title="Energy",
            icon="mdi:lightning-bolt",
            show_in_sidebar=True,
            require_admin=False,
        )

    @pytest.mark.asyncio
    async def test_execute_dashboard_hidden_from_sidebar(self):
        """Test creating dashboard not shown in sidebar."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="hidden_dash",
            url_path="hidden",
            title="Hidden Dashboard",
            icon=None,
            show_in_sidebar=False,
            require_admin=False,
        )
        mock_client.create_dashboard.return_value = mock_dashboard

        arguments = {
            "url_path": "hidden",
            "title": "Hidden Dashboard",
            "show_in_sidebar": False,
        }
        result = await execute(mock_client, arguments)

        mock_client.create_dashboard.assert_called_once_with(
            url_path="hidden",
            title="Hidden Dashboard",
            icon=None,
            show_in_sidebar=False,
            require_admin=False,
        )

    @pytest.mark.asyncio
    async def test_execute_admin_only_dashboard(self):
        """Test creating dashboard requiring admin access."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="admin_dash",
            url_path="admin",
            title="Admin Panel",
            icon="mdi:shield-account",
            show_in_sidebar=True,
            require_admin=True,
        )
        mock_client.create_dashboard.return_value = mock_dashboard

        arguments = {
            "url_path": "admin",
            "title": "Admin Panel",
            "icon": "mdi:shield-account",
            "require_admin": True,
        }
        result = await execute(mock_client, arguments)

        mock_client.create_dashboard.assert_called_once_with(
            url_path="admin",
            title="Admin Panel",
            icon="mdi:shield-account",
            show_in_sidebar=True,
            require_admin=True,
        )

    @pytest.mark.asyncio
    async def test_execute_dashboard_with_all_options(self):
        """Test creating dashboard with all options specified."""
        mock_client = AsyncMock()
        mock_dashboard = Dashboard(
            id="full_dash",
            url_path="full-dashboard",
            title="Full Dashboard",
            icon="mdi:view-dashboard",
            show_in_sidebar=False,
            require_admin=True,
        )
        mock_client.create_dashboard.return_value = mock_dashboard

        arguments = {
            "url_path": "full-dashboard",
            "title": "Full Dashboard",
            "icon": "mdi:view-dashboard",
            "show_in_sidebar": False,
            "require_admin": True,
        }
        result = await execute(mock_client, arguments)

        assert "Dashboard created successfully" in result[0].text
        mock_client.create_dashboard.assert_called_once_with(
            url_path="full-dashboard",
            title="Full Dashboard",
            icon="mdi:view-dashboard",
            show_in_sidebar=False,
            require_admin=True,
        )
