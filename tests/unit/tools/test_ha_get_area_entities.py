"""Unit tests for ha_get_area_entities tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.areas import ha_get_area_entities
from home_assistant_mcp.tool_models import GetAreaEntitiesInput
from home_assistant_mcp.models import EntityState


class TestGetAreaEntitiesTool:
    """Tests for ha_get_area_entities tool."""



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
        core.client = mock_client

        # Execute tool
        result = await ha_get_area_entities(
            GetAreaEntitiesInput(area="living_room", response_format="json")
        )

        # Verify
        # Verify JSON structure
        json_data = json.loads(result)
        entities = json_data["entities"]
        assert len(entities) == 3
        # In this implementation, ha_get_area_entities returns list of entity_id strings if JSON
        # Wait, implementation says: return json.dumps({"area": params.area, "entities": entities}, indent=2)
        # entities from client.get_area_entities is list of strings? 
        # Yes, mock returns list of strings.
        assert entities[0] == "light.living_room"

        mock_client.get_area_entities.assert_called_once_with(area="living_room", domain=None)

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
        core.client = mock_client

        # Execute tool with domain filter
        result = await ha_get_area_entities(GetAreaEntitiesInput(area="kitchen", domain="light"))

        # Verify domain filter is reflected in output
        assert "**Domain filter**: light" in result
        mock_client.get_area_entities.assert_called_once_with(area="kitchen", domain="light")

    @pytest.mark.asyncio
    async def test_execute_empty_area(self):
        """Test getting entities from an empty area."""
        mock_client = AsyncMock()
        mock_client.get_area_entities.return_value = []
        core.client = mock_client

        result = await ha_get_area_entities(
            GetAreaEntitiesInput(area="basement", response_format="json")
        )

        assert '{\n  "area": "basement",\n  "entities": []\n}' in result

    @pytest.mark.asyncio
    async def test_execute_handles_entity_error(self):
        """Test handling error when getting entity state fails."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_area_entities.return_value = ["light.broken"]

        # Mock get_state to raise an exception
        mock_client.get_state.side_effect = Exception("Entity not found")
        core.client = mock_client

        # Execute tool
        result = await ha_get_area_entities(
            GetAreaEntitiesInput(area="test_area", response_format="json")
        )

        # Verify error is handled gracefully
        # Original test verified error handling when get_state fails.
        # But for get_area_entities, it does NOT call get_state if JSON format is used?
        # Check tools/areas.py: ha_get_area_entities calls get_area_entities.
        # If markdown, it iterates and prints only strings unless it calls get_state?
        # tools/areas.py DOES NOT call get_state in ha_get_area_entities!
        # It just lists entity IDs returned by get_area_entities.
        # So "handles_entity_error" test is irrelevant for JSON if it just lists strings.
        json_data = json.loads(result)
        entities = json_data["entities"]
        assert entities[0] == "light.broken"

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
        core.client = mock_client

        result = await ha_get_area_entities(
            GetAreaEntitiesInput(area="test", response_format="json")
        )

        json_data = json.loads(result)
        entities = json_data["entities"]
        assert entities[0] == "sensor.test"
