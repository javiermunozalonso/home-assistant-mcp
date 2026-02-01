"""Unit tests for ha_create_dashboard tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.dashboards import ha_create_dashboard
from home_assistant_mcp.tool_models import CreateDashboardInput
from home_assistant_mcp.models import Dashboard


class TestCreateDashboardTool:
    """Tests for ha_create_dashboard tool."""



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
        core.client = mock_client

        # Execute tool
        params = CreateDashboardInput(
            url_path="test-dashboard",
            title="Test Dashboard",
        )
        result = await ha_create_dashboard(params)

        # Verify
        assert "Dashboard created successfully" in result
        assert "test-dashboard" in result

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
        core.client = mock_client

        params = CreateDashboardInput(
            url_path="energy",
            title="Energy",
            icon="mdi:lightning-bolt",
        )
        await ha_create_dashboard(params)

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
        core.client = mock_client

        params = CreateDashboardInput(
            url_path="hidden",
            title="Hidden Dashboard",
            show_in_sidebar=False,
        )
        await ha_create_dashboard(params)

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
        core.client = mock_client

        params = CreateDashboardInput(
            url_path="admin",
            title="Admin Panel",
            icon="mdi:shield-account",
            require_admin=True,
        )
        await ha_create_dashboard(params)

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
        core.client = mock_client

        params = CreateDashboardInput(
            url_path="full-dashboard",
            title="Full Dashboard",
            icon="mdi:view-dashboard",
            show_in_sidebar=False,
            require_admin=True,
        )
        result = await ha_create_dashboard(params)

        assert "Dashboard created successfully" in result
        mock_client.create_dashboard.assert_called_once_with(
            url_path="full-dashboard",
            title="Full Dashboard",
            icon="mdi:view-dashboard",
            show_in_sidebar=False,
            require_admin=True,
        )
