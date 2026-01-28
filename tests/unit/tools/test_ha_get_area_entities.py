"""Unit tests for ha_get_area_entities tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_get_area_entities import TOOL_DEF, execute
from home_assistant_mcp.models import EntityState


class TestGetAreaEntitiesTool:
    """Tests for ha_get_area_entities tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_get_area_entities"
        assert "entities assigned to a specific area" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "area" in TOOL_DEF.inputSchema["required"]

        # Check optional domain parameter
        props = TOOL_DEF.inputSchema["properties"]
        assert "domain" in props

    @pytest.mark.asyncio
    async def test_execute_without_domain_filter(self):
        """Test getting all entities in an area."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_area_entities.return_value = [
            "light.living_room",
            "switch.living_room_fan",
            "sensor.living_room_temp",
        ]

        # Mock get_state for each entity
        mock_states = [
            EntityState(
                entity_id="light.living_room",
                state="on",
                attributes={"friendly_name": "Living Room Light"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
            EntityState(
                entity_id="switch.living_room_fan",
                state="off",
                attributes={"friendly_name": "Living Room Fan"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
            EntityState(
                entity_id="sensor.living_room_temp",
                state="22.5",
                attributes={"friendly_name": "Living Room Temperature"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
        ]
        mock_client.get_state.side_effect = mock_states

        # Execute tool
        result = await execute(mock_client, {"area": "living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found 3 entities in area 'living_room'" in result[0].text

        # Verify JSON structure
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 3
        assert json_data[0]["entity_id"] == "light.living_room"
        assert json_data[0]["state"] == "on"
        assert json_data[0]["friendly_name"] == "Living Room Light"

        mock_client.get_area_entities.assert_called_once_with("living_room", domain=None)

    @pytest.mark.asyncio
    async def test_execute_with_domain_filter(self):
        """Test getting entities filtered by domain."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_area_entities.return_value = [
            "light.kitchen_ceiling",
            "light.kitchen_cabinet",
        ]

        mock_states = [
            EntityState(
                entity_id="light.kitchen_ceiling",
                state="on",
                attributes={"friendly_name": "Kitchen Ceiling Light"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
            EntityState(
                entity_id="light.kitchen_cabinet",
                state="off",
                attributes={"friendly_name": "Kitchen Cabinet Light"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
        ]
        mock_client.get_state.side_effect = mock_states

        # Execute tool with domain filter
        result = await execute(mock_client, {"area": "kitchen", "domain": "light"})

        # Verify domain filter is reflected in output
        assert "(domain: light)" in result[0].text
        mock_client.get_area_entities.assert_called_once_with("kitchen", domain="light")

    @pytest.mark.asyncio
    async def test_execute_empty_area(self):
        """Test getting entities from an empty area."""
        mock_client = AsyncMock()
        mock_client.get_area_entities.return_value = []

        result = await execute(mock_client, {"area": "basement"})

        assert "Found 0 entities in area 'basement'" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_handles_entity_error(self):
        """Test handling error when getting entity state fails."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_area_entities.return_value = ["light.broken"]

        # Mock get_state to raise an exception
        mock_client.get_state.side_effect = Exception("Entity not found")

        # Execute tool
        result = await execute(mock_client, {"area": "test_area"})

        # Verify error is handled gracefully
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert json_data[0]["entity_id"] == "light.broken"
        assert json_data[0]["state"] == "unknown"
        assert json_data[0]["friendly_name"] == "light.broken"

    @pytest.mark.asyncio
    async def test_execute_entity_without_friendly_name(self):
        """Test entity without friendly_name attribute."""
        mock_client = AsyncMock()
        mock_client.get_area_entities.return_value = ["sensor.test"]

        mock_state = EntityState(
            entity_id="sensor.test",
            state="42",
            attributes={},  # No friendly_name
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_client.get_state.return_value = mock_state

        result = await execute(mock_client, {"area": "test"})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        # Should use entity_id as fallback
        assert json_data[0]["friendly_name"] == "sensor.test"
