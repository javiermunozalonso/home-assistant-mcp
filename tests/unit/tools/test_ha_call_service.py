"""Unit tests for ha_call_service tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_call_service import TOOL_DEF, execute
from home_assistant_mcp.models import ServiceCallResponse, EntityState


class TestCallServiceTool:
    """Tests for ha_call_service tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_call_service"
        assert "Call a Home Assistant service" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "domain" in TOOL_DEF.inputSchema["required"]
        assert "service" in TOOL_DEF.inputSchema["required"]

        # Check properties
        props = TOOL_DEF.inputSchema["properties"]
        assert "entity_id" in props
        assert "data" in props

    @pytest.mark.asyncio
    async def test_execute_basic_service_call(self):
        """Test basic service call without entity_id or data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ServiceCallResponse(success=True, changed_states=[])
        mock_client.call_service.return_value = mock_response

        # Execute tool
        arguments = {
            "domain": "homeassistant",
            "service": "restart",
        }
        result = await execute(mock_client, arguments)

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Service homeassistant.restart called successfully" in result[0].text
        mock_client.call_service.assert_called_once_with(
            "homeassistant",
            "restart",
            entity_id=None,
            data={},
        )

    @pytest.mark.asyncio
    async def test_execute_with_entity_id(self):
        """Test service call with entity_id."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.living_room",
            state="on",
            attributes={},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.call_service.return_value = mock_response

        # Execute tool
        arguments = {
            "domain": "light",
            "service": "turn_on",
            "entity_id": "light.living_room",
        }
        result = await execute(mock_client, arguments)

        # Verify
        assert "Service light.turn_on called successfully" in result[0].text
        mock_client.call_service.assert_called_once_with(
            "light",
            "turn_on",
            entity_id="light.living_room",
            data={},
        )

    @pytest.mark.asyncio
    async def test_execute_with_comma_separated_entities(self):
        """Test service call with multiple comma-separated entity IDs."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ServiceCallResponse(success=True, changed_states=[])
        mock_client.call_service.return_value = mock_response

        # Execute tool with comma-separated entities
        arguments = {
            "domain": "light",
            "service": "turn_off",
            "entity_id": "light.living_room, light.bedroom, light.kitchen",
        }
        result = await execute(mock_client, arguments)

        # Verify entities were split into a list
        call_args = mock_client.call_service.call_args
        assert call_args[1]["entity_id"] == ["light.living_room", "light.bedroom", "light.kitchen"]

    @pytest.mark.asyncio
    async def test_execute_with_data(self):
        """Test service call with additional data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.bedroom",
            state="on",
            attributes={"brightness": 128},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.call_service.return_value = mock_response

        # Execute tool with data
        arguments = {
            "domain": "light",
            "service": "turn_on",
            "entity_id": "light.bedroom",
            "data": {"brightness": 128, "color_temp": 300},
        }
        result = await execute(mock_client, arguments)

        # Verify
        assert "Service light.turn_on called successfully" in result[0].text
        mock_client.call_service.assert_called_once_with(
            "light",
            "turn_on",
            entity_id="light.bedroom",
            data={"brightness": 128, "color_temp": 300},
        )

    @pytest.mark.asyncio
    async def test_execute_with_entity_and_data(self):
        """Test service call with both entity_id and data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ServiceCallResponse(success=True, changed_states=[])
        mock_client.call_service.return_value = mock_response

        # Execute tool
        arguments = {
            "domain": "climate",
            "service": "set_temperature",
            "entity_id": "climate.living_room",
            "data": {"temperature": 22, "hvac_mode": "heat"},
        }
        result = await execute(mock_client, arguments)

        # Verify both entity_id and data were passed
        mock_client.call_service.assert_called_once_with(
            "climate",
            "set_temperature",
            entity_id="climate.living_room",
            data={"temperature": 22, "hvac_mode": "heat"},
        )

    @pytest.mark.asyncio
    async def test_execute_response_includes_changed_states(self):
        """Test that response includes changed states information."""
        # Create mock client with multiple changed states
        mock_client = AsyncMock()
        mock_states = [
            EntityState(
                entity_id="light.living_room",
                state="on",
                attributes={},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
            EntityState(
                entity_id="light.bedroom",
                state="on",
                attributes={},
                last_changed="2024-01-15T10:30:00+00:00",
                last_updated="2024-01-15T10:30:00+00:00",
            ),
        ]
        mock_response = ServiceCallResponse(success=True, changed_states=mock_states)
        mock_client.call_service.return_value = mock_response

        # Execute tool
        arguments = {
            "domain": "light",
            "service": "turn_on",
            "entity_id": "light.living_room, light.bedroom",
        }
        result = await execute(mock_client, arguments)

        # Verify response includes changed states
        assert "Changed states:" in result[0].text
        assert "light.living_room" in result[0].text or "on" in result[0].text
