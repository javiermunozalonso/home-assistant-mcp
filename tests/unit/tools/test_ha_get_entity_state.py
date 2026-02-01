"""Unit tests for ha_get_entity_state tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.entities import ha_get_entity_state
from home_assistant_mcp.tool_models import GetEntityStateInput
from home_assistant_mcp.models import EntityState


class TestGetEntityStateTool:
    """Tests for ha_get_entity_state tool."""



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
        core.client = mock_client

        # Execute tool
        result = await ha_get_entity_state(GetEntityStateInput(entity_id="light.living_room"))

        # Verify
        # Verify
        assert "light.living_room" in result
        assert "on" in result
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
        core.client = mock_client

        result = await ha_get_entity_state(GetEntityStateInput(entity_id="sensor.temperature"))

        assert "sensor.temperature" in result
        assert "22.5" in result

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
        core.client = mock_client

        result = await ha_get_entity_state(GetEntityStateInput(entity_id="climate.living_room"))

        assert "climate.living_room" in result
        assert "heat" in result
