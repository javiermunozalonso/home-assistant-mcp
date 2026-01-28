"""Unit tests for ha_get_area_devices tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_get_area_devices import TOOL_DEF, execute


class TestGetAreaDevicesTool:
    """Tests for ha_get_area_devices tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_get_area_devices"
        assert "devices assigned to a specific area" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "area" in TOOL_DEF.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test getting devices from an area."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_area_devices.return_value = [
            "device_id_1",
            "device_id_2",
            "device_id_3",
        ]

        # Execute tool
        result = await execute(mock_client, {"area": "living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found 3 devices in area 'living_room'" in result[0].text

        # Verify JSON structure
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 3
        assert "device_id_1" in json_data
        assert "device_id_2" in json_data
        assert "device_id_3" in json_data

        mock_client.get_area_devices.assert_called_once_with("living_room")

    @pytest.mark.asyncio
    async def test_execute_empty_area(self):
        """Test getting devices from an area with no devices."""
        mock_client = AsyncMock()
        mock_client.get_area_devices.return_value = []

        result = await execute(mock_client, {"area": "basement"})

        assert "Found 0 devices in area 'basement'" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_different_area_names(self):
        """Test with different area names and IDs."""
        mock_client = AsyncMock()
        mock_client.get_area_devices.return_value = ["device_1"]

        # Test with area ID
        result = await execute(mock_client, {"area": "kitchen"})
        assert "'kitchen'" in result[0].text

        # Test with area name
        mock_client.get_area_devices.return_value = ["device_2", "device_3"]
        result = await execute(mock_client, {"area": "Master Bedroom"})
        assert "'Master Bedroom'" in result[0].text
        assert "Found 2 devices" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_single_device(self):
        """Test area with single device."""
        mock_client = AsyncMock()
        mock_client.get_area_devices.return_value = ["single_device_id"]

        result = await execute(mock_client, {"area": "office"})

        assert "Found 1 devices" in result[0].text  # Note: grammar could be improved in source
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 1
