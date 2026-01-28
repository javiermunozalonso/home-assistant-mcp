"""Unit tests for ha_fire_event tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_fire_event import TOOL_DEF, execute


class TestFireEventTool:
    """Tests for ha_fire_event tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_fire_event"
        assert "Fire a custom event" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "event_type" in TOOL_DEF.inputSchema["required"]

        # Check properties
        props = TOOL_DEF.inputSchema["properties"]
        assert "event_type" in props
        assert "event_data" in props

    @pytest.mark.asyncio
    async def test_execute_without_data(self):
        """Test firing event without event data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True

        # Execute tool
        result = await execute(mock_client, {"event_type": "test_event"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Event 'test_event' fired successfully" in result[0].text
        mock_client.fire_event.assert_called_once_with("test_event", {})

    @pytest.mark.asyncio
    async def test_execute_with_data(self):
        """Test firing event with event data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True

        # Execute tool with event data
        event_data = {"message": "Hello", "value": 42}
        result = await execute(
            mock_client, {"event_type": "custom_event", "event_data": event_data}
        )

        # Verify
        assert "Event 'custom_event' fired successfully" in result[0].text
        mock_client.fire_event.assert_called_once_with("custom_event", event_data)

    @pytest.mark.asyncio
    async def test_execute_with_complex_data(self):
        """Test firing event with complex event data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True

        # Execute tool with complex data
        event_data = {
            "user": "test_user",
            "action": "button_press",
            "details": {"button_id": 1, "duration": 500},
            "tags": ["automation", "test"],
        }
        result = await execute(
            mock_client, {"event_type": "button_event", "event_data": event_data}
        )

        # Verify complex data was passed
        mock_client.fire_event.assert_called_once_with("button_event", event_data)
        assert "button_event" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_different_event_types(self):
        """Test firing different types of events."""
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True

        # Test various event types
        event_types = [
            "state_changed",
            "automation_triggered",
            "service_called",
            "custom_event_123",
        ]

        for event_type in event_types:
            result = await execute(mock_client, {"event_type": event_type})
            assert f"Event '{event_type}' fired successfully" in result[0].text
