"""Unit tests for ha_delete_dashboard tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_delete_dashboard import TOOL_DEF, execute


class TestDeleteDashboardTool:
    """Tests for ha_delete_dashboard tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_delete_dashboard"
        assert "Delete a dashboard" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "dashboard_id" in TOOL_DEF.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful dashboard deletion."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.delete_dashboard.return_value = True

        # Execute tool
        result = await execute(mock_client, {"dashboard_id": "test_dashboard"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Dashboard 'test_dashboard' deleted successfully" in result[0].text
        mock_client.delete_dashboard.assert_called_once_with("test_dashboard")

    @pytest.mark.asyncio
    async def test_execute_different_dashboard_ids(self):
        """Test deleting dashboards with different IDs."""
        mock_client = AsyncMock()
        mock_client.delete_dashboard.return_value = True

        dashboard_ids = ["lovelace", "energy", "admin_panel", "custom_123"]

        for dashboard_id in dashboard_ids:
            result = await execute(mock_client, {"dashboard_id": dashboard_id})
            assert f"Dashboard '{dashboard_id}' deleted successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_with_special_characters(self):
        """Test deleting dashboard with special characters in ID."""
        mock_client = AsyncMock()
        mock_client.delete_dashboard.return_value = True

        result = await execute(mock_client, {"dashboard_id": "my-custom-dashboard_123"})

        assert "Dashboard 'my-custom-dashboard_123' deleted successfully" in result[0].text
        mock_client.delete_dashboard.assert_called_once_with("my-custom-dashboard_123")
