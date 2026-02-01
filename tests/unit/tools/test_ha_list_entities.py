"""Unit tests for ha_list_entities tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.entities import ha_list_entities
from home_assistant_mcp.tool_models import ListEntitiesInput
from home_assistant_mcp.models import EntityState


class TestListEntitiesTool:
    """Tests for ha_list_entities tool."""



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
        core.client = mock_client

        # Execute tool
        result = await ha_list_entities(ListEntitiesInput(response_format="json"))

        # Verify
        # Verify JSON structure
        json_data = json.loads(result)
        entities = json_data["entities"]
        assert len(entities) == 3
        assert entities[0]["entity_id"] == "light.living_room"
        assert entities[0]["state"] == "on"
        assert entities[0]["friendly_name"] == "Living Room Light"

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
        core.client = mock_client

        # Execute tool with domain filter
        result = await ha_list_entities(
            ListEntitiesInput(domain="light", response_format="json")
        )

        # Verify
        json_data = json.loads(result)
        entities = json_data["entities"]
        assert all(e["entity_id"].startswith("light.") for e in entities)

        mock_client.get_entities_by_domain.assert_called_once_with("light")

    @pytest.mark.asyncio
    async def test_execute_empty_result(self):
        """Test listing entities when no entities exist."""
        mock_client = AsyncMock()
        mock_client.get_states.return_value = []
        core.client = mock_client

        result = await ha_list_entities(ListEntitiesInput(response_format="json"))

        json_data = json.loads(result)
        entities = json_data["entities"]
        assert len(entities) == 0

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
        core.client = mock_client

        result = await ha_list_entities(ListEntitiesInput(response_format="json"))

        json_data = json.loads(result)
        entities = json_data["entities"]
        # Should use entity_id as fallback
        assert entities[0]["friendly_name"] == "sensor.test"
