"""Unit tests for ha_health_check tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_health_check import TOOL_DEF, execute
from home_assistant_mcp.models import ApiStatus


class TestHealthCheckTool:
    """Tests for ha_health_check tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_health_check"
        assert "Home Assistant API" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert TOOL_DEF.inputSchema["required"] == []

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful health check execution."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ApiStatus(message="API running.")
        mock_client.check_api.return_value = mock_response

        # Execute tool
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "API running." in result[0].text
        assert "Home Assistant API is running" in result[0].text
        mock_client.check_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_different_message(self):
        """Test health check with different API message."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ApiStatus(message="System operational")
        mock_client.check_api.return_value = mock_response

        # Execute tool
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert "System operational" in result[0].text
