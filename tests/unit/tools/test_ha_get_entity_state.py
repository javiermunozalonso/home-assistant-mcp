"""Unit tests for ha_get_entity_state tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_get_entity_state import TOOL_DEF, execute
from home_assistant_mcp.models import EntityState


class TestGetEntityStateTool:
    """Tests for ha_get_entity_state tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_get_entity_state"
        assert "state and attributes" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "entity_id" in TOOL_DEF.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful entity state retrieval."""
        # Create mock client and response
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.living_room",
            state="on",
            attributes={
                "friendly_name": "Living Room Light",
                "brightness": 255,
                "color_mode": "brightness",
            },
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_client.get_state.return_value = mock_state

        # Execute tool
        result = await execute(mock_client, {"entity_id": "light.living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "light.living_room" in result[0].text
        assert "on" in result[0].text
        mock_client.get_state.assert_called_once_with("light.living_room")

    @pytest.mark.asyncio
    async def test_execute_different_entity_types(self):
        """Test getting state for different entity types."""
        # Test sensor
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="sensor.temperature",
            state="22.5",
            attributes={
                "unit_of_measurement": "°C",
                "friendly_name": "Temperature",
            },
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_client.get_state.return_value = mock_state

        result = await execute(mock_client, {"entity_id": "sensor.temperature"})

        assert "sensor.temperature" in result[0].text
        assert "22.5" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_with_complex_attributes(self):
        """Test entity state with complex attributes."""
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="climate.living_room",
            state="heat",
            attributes={
                "friendly_name": "Living Room Climate",
                "temperature": 22,
                "current_temperature": 21,
                "hvac_modes": ["heat", "cool", "off"],
                "preset_modes": ["home", "away"],
            },
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_client.get_state.return_value = mock_state

        result = await execute(mock_client, {"entity_id": "climate.living_room"})

        assert "climate.living_room" in result[0].text
        assert "heat" in result[0].text
