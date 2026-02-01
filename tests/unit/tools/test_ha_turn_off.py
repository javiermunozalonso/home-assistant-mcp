"""Unit tests for ha_turn_off tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.control import ha_turn_off
from home_assistant_mcp.tool_models import TurnOffInput
from home_assistant_mcp.models import ServiceCallResponse, EntityState


class TestTurnOffTool:
    """Tests for ha_turn_off tool."""



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
        core.client = mock_client

        # Execute tool
        result = await ha_turn_off(TurnOffInput(entity_id="light.living_room"))

        # Verify
        assert "Turned off light.living_room" in result
        assert "Changed states:" in result
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
        core.client = mock_client

        result = await ha_turn_off(TurnOffInput(entity_id="switch.kitchen"))

        assert "Turned off switch.kitchen" in result
        mock_client.turn_off.assert_called_once_with("switch.kitchen")
