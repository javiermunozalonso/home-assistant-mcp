"""Unit tests for ha_list_entities tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_list_entities import TOOL_DEF, execute
from home_assistant_mcp.models import EntityState


class TestListEntitiesTool:
    """Tests for ha_list_entities tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_list_entities"
        assert "List all entities" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert TOOL_DEF.inputSchema["required"] == []
        assert "domain" in TOOL_DEF.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_execute_list_all_entities(self):
        """Test listing all entities without domain filter."""
        # Create mock client with multiple entities
        mock_client = AsyncMock()
        mock_states = [
            EntityState(
                entity_id="light.living_room",
                state="on",
                attributes={"friendly_name": "Living Room Light"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
            EntityState(
                entity_id="switch.kitchen",
                state="off",
                attributes={"friendly_name": "Kitchen Switch"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
            EntityState(
                entity_id="sensor.temperature",
                state="22.5",
                attributes={"friendly_name": "Temperature Sensor"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
        ]
        mock_client.get_states.return_value = mock_states

        # Execute tool
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found 3 entities" in result[0].text

        # Verify JSON structure
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 3
        assert json_data[0]["entity_id"] == "light.living_room"
        assert json_data[0]["state"] == "on"
        assert json_data[0]["friendly_name"] == "Living Room Light"

        mock_client.get_states.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_filter_by_domain(self):
        """Test listing entities filtered by domain."""
        # Create mock client
        mock_client = AsyncMock()
        mock_states = [
            EntityState(
                entity_id="light.living_room",
                state="on",
                attributes={"friendly_name": "Living Room Light"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
            EntityState(
                entity_id="light.bedroom",
                state="off",
                attributes={"friendly_name": "Bedroom Light"},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
        ]
        mock_client.get_entities_by_domain.return_value = mock_states

        # Execute tool with domain filter
        result = await execute(mock_client, {"domain": "light"})

        # Verify
        assert "Found 2 entities" in result[0].text

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert all(e["entity_id"].startswith("light.") for e in json_data)

        mock_client.get_entities_by_domain.assert_called_once_with("light")

    @pytest.mark.asyncio
    async def test_execute_empty_result(self):
        """Test listing entities when no entities exist."""
        mock_client = AsyncMock()
        mock_client.get_states.return_value = []

        result = await execute(mock_client, {})

        assert "Found 0 entities" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_entity_without_friendly_name(self):
        """Test listing entities when friendly_name is missing."""
        mock_client = AsyncMock()
        mock_states = [
            EntityState(
                entity_id="sensor.test",
                state="42",
                attributes={},  # No friendly_name
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
        ]
        mock_client.get_states.return_value = mock_states

        result = await execute(mock_client, {})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        # Should use entity_id as fallback
        assert json_data[0]["friendly_name"] == "sensor.test"
