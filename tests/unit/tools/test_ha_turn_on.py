"""Unit tests for ha_turn_on tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_turn_on import TOOL_DEF, execute
from home_assistant_mcp.models import ServiceCallResponse, EntityState


class TestTurnOnTool:
    """Tests for ha_turn_on tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_turn_on"
        assert "Turn on" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "entity_id" in TOOL_DEF.inputSchema["required"]

        # Check optional parameters
        props = TOOL_DEF.inputSchema["properties"]
        assert "brightness" in props
        assert "brightness_pct" in props
        assert "color_temp" in props
        assert "rgb_color" in props

    @pytest.mark.asyncio
    async def test_execute_basic(self):
        """Test basic turn on without parameters."""
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
        mock_client.turn_on.return_value = mock_response

        # Execute tool
        result = await execute(mock_client, {"entity_id": "light.living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Turned on light.living_room" in result[0].text
        assert "New state:" in result[0].text
        mock_client.turn_on.assert_called_once_with("light.living_room")

    @pytest.mark.asyncio
    async def test_execute_with_brightness(self):
        """Test turn on with brightness parameter."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.bedroom",
            state="on",
            attributes={"brightness": 200},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_on.return_value = mock_response

        # Execute tool
        arguments = {"entity_id": "light.bedroom", "brightness": 200}
        result = await execute(mock_client, arguments)

        # Verify
        assert len(result) == 1
        assert "Turned on light.bedroom" in result[0].text
        mock_client.turn_on.assert_called_once_with("light.bedroom", brightness=200)

    @pytest.mark.asyncio
    async def test_execute_with_brightness_pct(self):
        """Test turn on with brightness percentage."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.kitchen",
            state="on",
            attributes={"brightness_pct": 50},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_on.return_value = mock_response

        # Execute tool
        arguments = {"entity_id": "light.kitchen", "brightness_pct": 50}
        result = await execute(mock_client, arguments)

        # Verify
        mock_client.turn_on.assert_called_once_with("light.kitchen", brightness_pct=50)

    @pytest.mark.asyncio
    async def test_execute_with_color_temp(self):
        """Test turn on with color temperature."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.office",
            state="on",
            attributes={"color_temp": 300},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_on.return_value = mock_response

        # Execute tool
        arguments = {"entity_id": "light.office", "color_temp": 300}
        result = await execute(mock_client, arguments)

        # Verify
        mock_client.turn_on.assert_called_once_with("light.office", color_temp=300)

    @pytest.mark.asyncio
    async def test_execute_with_rgb_color(self):
        """Test turn on with RGB color."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.led_strip",
            state="on",
            attributes={"rgb_color": [255, 0, 0]},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_on.return_value = mock_response

        # Execute tool
        arguments = {"entity_id": "light.led_strip", "rgb_color": [255, 0, 0]}
        result = await execute(mock_client, arguments)

        # Verify
        mock_client.turn_on.assert_called_once_with("light.led_strip", rgb_color=[255, 0, 0])

    @pytest.mark.asyncio
    async def test_execute_with_multiple_parameters(self):
        """Test turn on with multiple parameters."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.smart_bulb",
            state="on",
            attributes={"brightness": 255, "rgb_color": [0, 255, 0]},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_on.return_value = mock_response

        # Execute tool
        arguments = {
            "entity_id": "light.smart_bulb",
            "brightness": 255,
            "rgb_color": [0, 255, 0],
        }
        result = await execute(mock_client, arguments)

        # Verify
        mock_client.turn_on.assert_called_once_with(
            "light.smart_bulb",
            brightness=255,
            rgb_color=[0, 255, 0],
        )

    @pytest.mark.asyncio
    async def test_execute_ignores_unknown_parameters(self):
        """Test that unknown parameters are ignored."""
        # Create mock client
        mock_client = AsyncMock()
        mock_state = EntityState(
            entity_id="light.test",
            state="on",
            attributes={},
            last_changed="2024-01-15T10:30:00+00:00",
            last_updated="2024-01-15T10:30:00+00:00",
        )
        mock_response = ServiceCallResponse(success=True, changed_states=[mock_state])
        mock_client.turn_on.return_value = mock_response

        # Execute tool with unknown parameter
        arguments = {
            "entity_id": "light.test",
            "unknown_param": "should_be_ignored",
        }
        result = await execute(mock_client, arguments)

        # Verify unknown param was not passed
        mock_client.turn_on.assert_called_once_with("light.test")
