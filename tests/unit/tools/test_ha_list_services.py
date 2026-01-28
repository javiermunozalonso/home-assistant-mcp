"""Unit tests for ha_list_services tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_list_services import TOOL_DEF, execute
from home_assistant_mcp.models import ServiceDomain


class TestListServicesTool:
    """Tests for ha_list_services tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_list_services"
        assert "available services" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert TOOL_DEF.inputSchema["required"] == []
        assert "domain" in TOOL_DEF.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_execute_list_all_services(self):
        """Test listing all services without domain filter."""
        # Create mock client with multiple service domains
        mock_client = AsyncMock()
        mock_services = [
            ServiceDomain(
                domain="light",
                services={
                    "turn_on": {
                        "description": "Turn on a light",
                        "fields": {"brightness": {"description": "Brightness"}},
                    },
                    "turn_off": {"description": "Turn off a light", "fields": {}},
                },
            ),
            ServiceDomain(
                domain="switch",
                services={
                    "turn_on": {"description": "Turn on a switch", "fields": {}},
                    "turn_off": {"description": "Turn off a switch", "fields": {}},
                },
            ),
        ]
        mock_client.get_services.return_value = mock_services

        # Execute tool
        result = await execute(mock_client, {})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Found 4 services" in result[0].text

        # Verify JSON structure
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 4

        # Check that services are formatted correctly
        service_names = [s["service"] for s in json_data]
        assert "light.turn_on" in service_names
        assert "light.turn_off" in service_names
        assert "switch.turn_on" in service_names
        assert "switch.turn_off" in service_names

        mock_client.get_services.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_filter_by_domain(self):
        """Test listing services filtered by domain."""
        # Create mock client
        mock_client = AsyncMock()
        mock_services = [
            ServiceDomain(
                domain="light",
                services={
                    "turn_on": {"description": "Turn on a light", "fields": {}},
                    "turn_off": {"description": "Turn off a light", "fields": {}},
                    "toggle": {"description": "Toggle a light", "fields": {}},
                },
            ),
            ServiceDomain(
                domain="switch",
                services={
                    "turn_on": {"description": "Turn on a switch", "fields": {}},
                },
            ),
        ]
        mock_client.get_services.return_value = mock_services

        # Execute tool with domain filter
        result = await execute(mock_client, {"domain": "light"})

        # Verify only light services are returned
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 3
        assert all(s["service"].startswith("light.") for s in json_data)

    @pytest.mark.asyncio
    async def test_execute_empty_result(self):
        """Test listing services when no services exist."""
        mock_client = AsyncMock()
        mock_client.get_services.return_value = []

        result = await execute(mock_client, {})

        assert "Found 0 services" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_service_without_description(self):
        """Test listing services when description is missing."""
        mock_client = AsyncMock()
        mock_services = [
            ServiceDomain(
                domain="test",
                services={
                    "test_service": {"description": None, "fields": {}},
                },
            ),
        ]
        mock_client.get_services.return_value = mock_services

        result = await execute(mock_client, {})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        # Should use fallback description
        assert json_data[0]["description"] == "No description"

    @pytest.mark.asyncio
    async def test_execute_includes_service_descriptions(self):
        """Test that service descriptions are included."""
        mock_client = AsyncMock()
        mock_services = [
            ServiceDomain(
                domain="climate",
                services={
                    "set_temperature": {
                        "description": "Set target temperature",
                        "fields": {},
                    },
                },
            ),
        ]
        mock_client.get_services.return_value = mock_services

        result = await execute(mock_client, {})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert json_data[0]["service"] == "climate.set_temperature"
        assert json_data[0]["description"] == "Set target temperature"
