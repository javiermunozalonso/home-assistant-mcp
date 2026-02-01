"""Unit tests for ha_list_areas tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.areas import ha_list_areas
from home_assistant_mcp.tool_models import ListAreasInput


class TestListAreasTool:
    """Tests for ha_list_areas tool."""



    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test listing areas successfully."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_areas.return_value = ["living_room", "kitchen", "bedroom"]
        mock_client.get_area_name.side_effect = [
            "Living Room",
            "Kitchen",
            "Bedroom",
        ]
        core.client = mock_client

        # Execute tool
        result = await ha_list_areas(ListAreasInput(response_format="json"))

        # Verify
        # Verify
        # Verify JSON structure
        json_data = json.loads(result)
        areas = json_data["areas"]
        assert len(areas) == 3
        assert areas[0] == "living_room"
        assert areas[1] == "kitchen"

        mock_client.get_areas.assert_called_once()
        # get_area_name is not called when using JSON format
        # assert mock_client.get_area_name.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_empty_areas(self):
        """Test listing when no areas exist."""
        mock_client = AsyncMock()
        mock_client.get_areas.return_value = []
        core.client = mock_client

        result = await ha_list_areas(ListAreasInput(response_format="json"))

        json_data = json.loads(result)
        areas = json_data["areas"]
        assert len(areas) == 0

    @pytest.mark.asyncio
    async def test_execute_area_without_friendly_name(self):
        """Test listing areas when friendly name is not available."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_areas.return_value = ["basement"]
        mock_client.get_area_name.return_value = None  # No friendly name
        core.client = mock_client

        result = await ha_list_areas(ListAreasInput(response_format="json"))

        # Verify area_id is used as fallback
        # Verify area_id is used as fallback
        json_data = json.loads(result)
        areas = json_data["areas"]
        assert areas[0] == "basement"

    @pytest.mark.asyncio
    async def test_execute_multiple_areas(self):
        """Test listing multiple areas."""
        mock_client = AsyncMock()
        mock_client.get_areas.return_value = [
            "living_room",
            "kitchen",
            "bedroom",
            "bathroom",
            "office",
        ]
        mock_client.get_area_name.side_effect = [
            "Living Room",
            "Kitchen",
            "Bedroom",
            "Bathroom",
            "Office",
        ]
        core.client = mock_client

        result = await ha_list_areas(ListAreasInput(response_format="json"))

        json_data = json.loads(result)
        areas = json_data["areas"]
        assert len(areas) == 5
