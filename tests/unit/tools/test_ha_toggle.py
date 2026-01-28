"""Unit tests for ha_toggle tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_toggle import TOOL_DEF, execute
from home_assistant_mcp.models import ServiceCallResponse, EntityState


class TestToggleTool:
    """Tests for ha_toggle tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_toggle"
        assert "Toggle" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "entity_id" in TOOL_DEF.inputSchema["required"]

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

        # Execute tool
        result = await execute(mock_client, {"entity_id": "light.living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Toggled light.living_room" in result[0].text
        assert "New state:" in result[0].text
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

        result = await execute(mock_client, {"entity_id": "switch.fan"})

        assert "Toggled switch.fan" in result[0].text
        assert "on" in result[0].text.lower()

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

        result = await execute(mock_client, {"entity_id": "light.bedroom"})

        assert "Toggled light.bedroom" in result[0].text
        assert "off" in result[0].text.lower()
