"""Unit tests for ha_toggle tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.control import ha_toggle
from home_assistant_mcp.tool_models import ToggleInput
from home_assistant_mcp.models import ServiceCallResponse, EntityState


class TestToggleTool:
    """Tests for ha_toggle tool."""



    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful toggle execution."""
        # Create mock client and response
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.living_room",
            state="on",
            attributes={"friendly_name": "Living Room"},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.toggle.return_value = mock_response
        core.client = mock_client

        # Execute tool
        result = await ha_toggle(ToggleInput(entity_id="light.living_room"))

        # Verify
        assert "Toggled light.living_room" in result
        assert "Changed states:" in result
        assert "on" in result
        mock_client.toggle.assert_called_once_with("light.living_room")

    @pytest.mark.asyncio
    async def test_execute_toggle_off_to_on(self):
        """Test toggling from off to on."""
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="switch.fan",
            state="on",
            attributes={},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.toggle.return_value = mock_response
        core.client = mock_client

        result = await ha_toggle(ToggleInput(entity_id="switch.fan"))

        assert "Toggled switch.fan" in result
        assert "on" in result.lower()

    @pytest.mark.asyncio
    async def test_execute_toggle_on_to_off(self):
        """Test toggling from on to off."""
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.bedroom",
            state="off",
            attributes={},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.toggle.return_value = mock_response
        core.client = mock_client

        result = await ha_toggle(ToggleInput(entity_id="light.bedroom"))

        assert "Toggled light.bedroom" in result
        assert "off" in result.lower()
