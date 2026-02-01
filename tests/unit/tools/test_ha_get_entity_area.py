"""Unit tests for ha_get_entity_area tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.areas import ha_get_entity_area
from home_assistant_mcp.tool_models import GetEntityAreaInput


class TestGetEntityAreaTool:
    """Tests for ha_get_entity_area tool."""



    @pytest.mark.asyncio
    async def test_execute_entity_with_area(self):
        """Test getting area for an entity that has one."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_entity_area.return_value = "Living Room"
        core.client = mock_client

        # Execute tool
        result = await ha_get_entity_area(GetEntityAreaInput(entity_id="light.living_room"))

        # Verify
        assert "light.living_room" in result
        assert "Living Room" in result
        mock_client.get_entity_area.assert_called_once_with(entity_id="light.living_room")

    @pytest.mark.asyncio
    async def test_execute_entity_without_area(self):
        """Test getting area for an entity not assigned to any area."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_entity_area.return_value = None
        core.client = mock_client

        # Execute tool
        result = await ha_get_entity_area(GetEntityAreaInput(entity_id="sensor.orphan"))

        # Verify
        # Verify
        assert "sensor.orphan" in result
        assert "is not assigned to any area" in result
        mock_client.get_entity_area.assert_called_once_with(entity_id="sensor.orphan")

    @pytest.mark.asyncio
    async def test_execute_different_entity_types(self):
        """Test with different entity types."""
        mock_client = AsyncMock()
        core.client = mock_client

        # Test light entity
        mock_client.get_entity_area.return_value = "Bedroom"
        result = await ha_get_entity_area(GetEntityAreaInput(entity_id="light.bedroom_lamp"))
        assert "is in area: Bedroom" in result

        # Test sensor entity
        mock_client.get_entity_area.return_value = "Kitchen"
        result = await ha_get_entity_area(GetEntityAreaInput(entity_id="sensor.kitchen_temp"))
        assert "is in area: Kitchen" in result

        # Test switch entity
        mock_client.get_entity_area.return_value = "Office"
        result = await ha_get_entity_area(GetEntityAreaInput(entity_id="switch.office_fan"))
        assert "is in area: Office" in result

    @pytest.mark.asyncio
    async def test_execute_area_with_special_characters(self):
        """Test area names with special characters."""
        mock_client = AsyncMock()
        mock_client.get_entity_area.return_value = "Master Bedroom #1"
        core.client = mock_client

        result = await ha_get_entity_area(GetEntityAreaInput(entity_id="light.master"))

        assert "is in area: Master Bedroom #1" in result
