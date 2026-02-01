"""Unit tests for ha_get_area_devices tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.areas import ha_get_area_devices
from home_assistant_mcp.tool_models import GetAreaDevicesInput


class TestGetAreaDevicesTool:
    """Tests for ha_get_area_devices tool."""



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
        core.client = mock_client

        # Execute tool
        result = await ha_get_area_devices(
            GetAreaDevicesInput(area="living_room", response_format="json")
        )

        # Verify
        # Verify JSON structure
        json_data = json.loads(result)
        devices = json_data["devices"]
        assert len(devices) == 3
        assert "device_id_1" in devices
        assert "device_id_2" in devices
        assert "device_id_3" in devices

        mock_client.get_area_devices.assert_called_once_with(area="living_room")

    @pytest.mark.asyncio
    async def test_execute_empty_area(self):
        """Test getting devices from an area with no devices."""
        mock_client = AsyncMock()
        mock_client.get_area_devices.return_value = []
        core.client = mock_client

        result = await ha_get_area_devices(GetAreaDevicesInput(area="basement"))

        assert "# Devices in 'basement' (0 total)" in result

    @pytest.mark.asyncio
    async def test_execute_different_area_names(self):
        """Test with different area names and IDs."""
        mock_client = AsyncMock()
        mock_client.get_area_devices.return_value = ["device_1"]
        core.client = mock_client

        # Test with area ID
        result = await ha_get_area_devices(GetAreaDevicesInput(area="kitchen"))
        assert "'kitchen'" in result

        # Test with area name
        mock_client.get_area_devices.return_value = ["device_2", "device_3"]
        result = await ha_get_area_devices(GetAreaDevicesInput(area="Master Bedroom"))
        # Verify
        assert "# Devices in 'Master Bedroom' (2 total)" in result

    @pytest.mark.asyncio
    async def test_execute_single_device(self):
        """Test area with single device."""
        mock_client = AsyncMock()
        mock_client.get_area_devices.return_value = ["single_device_id"]
        core.client = mock_client

        result = await ha_get_area_devices(
            GetAreaDevicesInput(area="office", response_format="json")
        )

        json_data = json.loads(result)
        devices = json_data["devices"]
        assert len(devices) == 1
