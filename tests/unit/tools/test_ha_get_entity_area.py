"""Unit tests for ha_get_entity_area tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_get_entity_area import TOOL_DEF, execute


class TestGetEntityAreaTool:
    """Tests for ha_get_entity_area tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_get_entity_area"
        assert "area name for a specific entity" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "entity_id" in TOOL_DEF.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_execute_entity_with_area(self):
        """Test getting area for an entity that has one."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_entity_area.return_value = "Living Room"

        # Execute tool
        result = await execute(mock_client, {"entity_id": "light.living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Entity 'light.living_room' is in area: Living Room" in result[0].text
        mock_client.get_entity_area.assert_called_once_with("light.living_room")

    @pytest.mark.asyncio
    async def test_execute_entity_without_area(self):
        """Test getting area for an entity not assigned to any area."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_entity_area.return_value = None

        # Execute tool
        result = await execute(mock_client, {"entity_id": "sensor.orphan"})

        # Verify
        assert "Entity 'sensor.orphan' is not assigned to any area" in result[0].text
        mock_client.get_entity_area.assert_called_once_with("sensor.orphan")

    @pytest.mark.asyncio
    async def test_execute_different_entity_types(self):
        """Test with different entity types."""
        mock_client = AsyncMock()

        # Test light entity
        mock_client.get_entity_area.return_value = "Bedroom"
        result = await execute(mock_client, {"entity_id": "light.bedroom_lamp"})
        assert "is in area: Bedroom" in result[0].text

        # Test sensor entity
        mock_client.get_entity_area.return_value = "Kitchen"
        result = await execute(mock_client, {"entity_id": "sensor.kitchen_temp"})
        assert "is in area: Kitchen" in result[0].text

        # Test switch entity
        mock_client.get_entity_area.return_value = "Office"
        result = await execute(mock_client, {"entity_id": "switch.office_fan"})
        assert "is in area: Office" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_area_with_special_characters(self):
        """Test area names with special characters."""
        mock_client = AsyncMock()
        mock_client.get_entity_area.return_value = "Master Bedroom #1"

        result = await execute(mock_client, {"entity_id": "light.master"})

        assert "is in area: Master Bedroom #1" in result[0].text
