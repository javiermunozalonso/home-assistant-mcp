"""Unit tests for ha_get_dashboard tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.dashboards import ha_get_dashboard
from home_assistant_mcp.tool_models import GetDashboardInput
from home_assistant_mcp.models import DashboardConfig


class TestGetDashboardTool:
    """Tests for ha_get_dashboard tool."""



    @pytest.mark.asyncio
    async def test_execute_default_dashboard(self):
        """Test getting default dashboard configuration."""
        # Create mock client
        mock_client = AsyncMock()
        mock_config = DashboardConfig(
            title="Home",
            views=[
                {
                    "title": "Overview",
                    "path": "overview",
                    "cards": [
                        {"type": "entities", "entities": ["light.living_room"]},
                    ],
                }
            ],
        )
        mock_client.get_dashboard_config.return_value = mock_config
        core.client = mock_client

        # Execute tool
        result = await ha_get_dashboard(GetDashboardInput(response_format="json"))

        # Verify
        json_data = json.loads(result)
        assert json_data["title"] == "Home"
        assert json_data["title"] == "Home"
        # assert "lovelace-default" in result # Not in mock data
        mock_client.get_dashboard_config.assert_called_once_with(url_path=None)

    @pytest.mark.asyncio
    async def test_execute_specific_dashboard(self):
        """Test getting specific dashboard configuration."""
        mock_client = AsyncMock()
        mock_config = DashboardConfig(
            title="Energy Dashboard",
            views=[
                {
                    "title": "Energy",
                    "cards": [{"type": "energy-distribution"}],
                }
            ],
        )
        mock_client.get_dashboard_config.return_value = mock_config
        core.client = mock_client

        # Execute tool
        result = await ha_get_dashboard(
            GetDashboardInput(url_path="energy", response_format="json")
        )

        # Verify
        json_data = json.loads(result)
        assert json_data["title"] == "Energy Dashboard"
        mock_client.get_dashboard_config.assert_called_once_with(url_path="energy")

    @pytest.mark.asyncio
    async def test_execute_dashboard_with_multiple_views(self):
        """Test getting dashboard with multiple views."""
        mock_client = AsyncMock()
        mock_config = DashboardConfig(
            title="Multi-View Dashboard",
            views=[
                {"title": "View 1", "cards": []},
                {"title": "View 2", "cards": []},
                {"title": "View 3", "cards": []},
            ],
        )
        mock_client.get_dashboard_config.return_value = mock_config
        core.client = mock_client

        result = await ha_get_dashboard(
            GetDashboardInput(url_path="multi-view", response_format="json")
        )

        json_data = json.loads(result)
        assert json_data["title"] == "Multi-View Dashboard"
        assert len(json_data["views"]) == 3

    @pytest.mark.asyncio
    async def test_execute_empty_dashboard(self):
        """Test getting dashboard with no views."""
        mock_client = AsyncMock()
        mock_config = DashboardConfig(
            title="Empty Dashboard",
            views=[],
        )
        mock_client.get_dashboard_config.return_value = mock_config
        core.client = mock_client

        result = await ha_get_dashboard(
            GetDashboardInput(url_path="empty", response_format="json")
        )

        json_data = json.loads(result)
        assert json_data["title"] == "Empty Dashboard"
        assert len(json_data["views"]) == 0
