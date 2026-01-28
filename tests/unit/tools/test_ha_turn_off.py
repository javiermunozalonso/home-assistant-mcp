"""Unit tests for ha_turn_off tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_turn_off import TOOL_DEF, execute
from home_assistant_mcp.models import ServiceCallResponse, EntityState


class TestTurnOffTool:
    """Tests for ha_turn_off tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_turn_off"
        assert "Turn off" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "entity_id" in TOOL_DEF.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful turn off execution."""
        # Create mock client and response
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.living_room",
            state="off",
            attributes={"friendly_name": "Living Room"},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_off.return_value = mock_response

        # Execute tool
        result = await execute(mock_client, {"entity_id": "light.living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Turned off light.living_room" in result[0].text
        assert "New state:" in result[0].text
        mock_client.turn_off.assert_called_once_with("light.living_room")

    @pytest.mark.asyncio
    async def test_execute_different_entity_types(self):
        """Test turn off with different entity types."""
        # Test with switch
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="switch.kitchen",
            state="off",
            attributes={},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_off.return_value = mock_response

        result = await execute(mock_client, {"entity_id": "switch.kitchen"})

        assert "Turned off switch.kitchen" in result[0].text
        mock_client.turn_off.assert_called_once_with("switch.kitchen")
