"""Unit tests for ha_list_areas tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_list_areas import TOOL_DEF, execute


class TestListAreasTool:
    """Tests for ha_list_areas tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_list_areas"
        assert "configured areas" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert TOOL_DEF.inputSchema["required"] == []

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

        # Execute tool
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found 3 areas" in result[0].text

        # Verify JSON structure
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 3
        assert json_data[0]["area_id"] == "living_room"
        assert json_data[0]["name"] == "Living Room"
        assert json_data[1]["area_id"] == "kitchen"
        assert json_data[1]["name"] == "Kitchen"

        mock_client.get_areas.assert_called_once()
        assert mock_client.get_area_name.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_empty_areas(self):
        """Test listing when no areas exist."""
        mock_client = AsyncMock()
        mock_client.get_areas.return_value = []

        result = await execute(mock_client, {})

        assert "Found 0 areas" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_area_without_friendly_name(self):
        """Test listing areas when friendly name is not available."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.get_areas.return_value = ["basement"]
        mock_client.get_area_name.return_value = None  # No friendly name

        result = await execute(mock_client, {})

        # Verify area_id is used as fallback
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert json_data[0]["area_id"] == "basement"
        assert json_data[0]["name"] == "basement"

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

        result = await execute(mock_client, {})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 5
        assert all("area_id" in area for area in json_data)
        assert all("name" in area for area in json_data)
