"""Unit tests for ha_get_config tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_get_config import TOOL_DEF, execute
from home_assistant_mcp.models import ConfigEntry


class TestGetConfigTool:
    """Tests for ha_get_config tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_get_config"
        assert "configuration" in TOOL_DEF.description.lower()
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert TOOL_DEF.inputSchema["required"] == []

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful configuration retrieval."""
        # Create mock client and response
        mock_client = AsyncMock()
        mock_config = ConfigEntry(
            message="Home",
            version="2024.1.0",
            location_name="Home",
            latitude=40.7128,
            longitude=-74.0060,
            elevation=100,
            time_zone="America/New_York",
            unit_system={"length": "km", "temperature": "°C"},
            components=["homeassistant", "light", "switch"],
        )
        mock_client.get_config.return_value = mock_config

        # Execute tool
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "2024.1.0" in result[0].text
        assert "Home" in result[0].text
        mock_client.get_config.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_includes_all_config_fields(self):
        """Test that response includes all configuration fields."""
        mock_client = AsyncMock()
        mock_config = ConfigEntry(
            message="Test Location",
            version="2024.2.0",
            location_name="Test Location",
            latitude=51.5074,
            longitude=-0.1278,
            elevation=50,
            time_zone="Europe/London",
            unit_system={"length": "mi", "temperature": "°F"},
            components=["homeassistant"],
        )
        mock_client.get_config.return_value = mock_config

        result = await execute(mock_client, {})

        # Verify key information is present
        assert "2024.2.0" in result[0].text
        assert "Test Location" in result[0].text
