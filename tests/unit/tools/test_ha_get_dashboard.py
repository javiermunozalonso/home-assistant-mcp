"""Unit tests for ha_get_dashboard tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_get_dashboard import TOOL_DEF, execute
from home_assistant_mcp.models import DashboardConfig


class TestGetDashboardTool:
    """Tests for ha_get_dashboard tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_get_dashboard"
        assert "configuration of a specific dashboard" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert TOOL_DEF.inputSchema["required"] == []

        # Check optional url_path parameter
        props = TOOL_DEF.inputSchema["properties"]
        assert "url_path" in props

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

        # Execute tool without url_path (default dashboard)
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Home" in result[0].text
        mock_client.get_dashboard_config.assert_called_once_with(None)

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

        result = await execute(mock_client, {"url_path": "energy"})

        assert "Energy Dashboard" in result[0].text
        mock_client.get_dashboard_config.assert_called_once_with("energy")

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

        result = await execute(mock_client, {"url_path": "multi-view"})

        assert "Multi-View Dashboard" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_empty_dashboard(self):
        """Test getting dashboard with no views."""
        mock_client = AsyncMock()
        mock_config = DashboardConfig(
            title="Empty Dashboard",
            views=[],
        )
        mock_client.get_dashboard_config.return_value = mock_config

        result = await execute(mock_client, {"url_path": "empty"})

        assert "Empty Dashboard" in result[0].text
