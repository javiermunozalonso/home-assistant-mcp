"""Unit tests for ha_list_dashboards tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_list_dashboards import TOOL_DEF, execute
from home_assistant_mcp.models import Dashboard


class TestListDashboardsTool:
    """Tests for ha_list_dashboards tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_list_dashboards"
        assert "Lovelace dashboards" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert TOOL_DEF.inputSchema["required"] == []

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

        # Execute tool
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found 2 dashboards" in result[0].text

        # Verify JSON structure
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 2
        assert json_data[0]["id"] == "lovelace"
        assert json_data[0]["title"] == "Home"
        assert json_data[0]["icon"] == "mdi:home"
        assert json_data[1]["id"] == "energy"

        mock_client.list_dashboards.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_empty_dashboards(self):
        """Test listing when no dashboards exist."""
        mock_client = AsyncMock()
        mock_client.list_dashboards.return_value = []

        result = await execute(mock_client, {})

        assert "Found 0 dashboards" in result[0].text

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

        result = await execute(mock_client, {})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert json_data[0]["require_admin"] is True
        assert json_data[0]["show_in_sidebar"] is False

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

        result = await execute(mock_client, {})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        dashboard = json_data[0]

        # Verify all expected fields are present
        assert "id" in dashboard
        assert "url_path" in dashboard
        assert "title" in dashboard
        assert "icon" in dashboard
        assert "show_in_sidebar" in dashboard
        assert "require_admin" in dashboard
