"""Unit tests for ha_health_check tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.health import ha_health_check
from home_assistant_mcp.models import ApiStatus


class TestHealthCheckTool:
    """Tests for ha_health_check tool."""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful health check execution."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ApiStatus(message="API running.")
        mock_client.check_api.return_value = mock_response
        
        # Set global client
        core.client = mock_client

        # Execute tool
        result = await ha_health_check()

        # Verify
        assert "API is running" in result
        assert "✓" in result
        mock_client.check_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_different_message(self):
        """Test health check with different API message."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ApiStatus(message="System operational")
        mock_client.check_api.return_value = mock_response

        # Set global client
        core.client = mock_client

        # Execute tool
        result = await ha_health_check()

        # Verify
        assert "System operational" in result

