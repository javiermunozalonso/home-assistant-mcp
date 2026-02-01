"""Unit tests for ha_fire_event tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.events import ha_fire_event
from home_assistant_mcp.tool_models import FireEventInput


class TestFireEventTool:
    """Tests for ha_fire_event tool."""



    @pytest.mark.asyncio
    async def test_execute_without_data(self):
        """Test firing event without event data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True
        core.client = mock_client

        # Execute tool
        result = await ha_fire_event(FireEventInput(event_type="test_event"))

        # Verify
        # Verify
        assert "Event 'test_event' fired successfully" in result
        mock_client.fire_event.assert_called_once_with(event_type="test_event", event_data={})

    @pytest.mark.asyncio
    async def test_execute_with_data(self):
        """Test firing event with event data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True
        core.client = mock_client

        # Execute tool with event data
        event_data = {"message": "Hello", "value": 42}
        result = await ha_fire_event(
            FireEventInput(event_type="custom_event", event_data=event_data)
        )

        # Verify
        # Verify
        assert "Event 'custom_event' fired successfully" in result
        mock_client.fire_event.assert_called_once_with(event_type="custom_event", event_data=event_data)

    @pytest.mark.asyncio
    async def test_execute_with_complex_data(self):
        """Test firing event with complex event data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True
        core.client = mock_client

        # Execute tool with complex data
        event_data = {
            "user": "test_user",
            "action": "button_press",
            "details": {"button_id": 1, "duration": 500},
            "tags": ["automation", "test"],
        }
        result = await ha_fire_event(
            FireEventInput(event_type="button_event", event_data=event_data)
        )

        # Verify complex data was passed
        mock_client.fire_event.assert_called_once_with(event_type="button_event", event_data=event_data)
        assert "button_event" in result

    @pytest.mark.asyncio
    async def test_execute_different_event_types(self):
        """Test firing different types of events."""
        mock_client = AsyncMock()
        mock_client.fire_event.return_value = True
        core.client = mock_client

        # Test various event types
        event_types = [
            "state_changed",
            "automation_triggered",
            "service_called",
            "custom_event_123",
        ]

        for event_type in event_types:
            result = await ha_fire_event(FireEventInput(event_type=event_type))
            assert f"Event '{event_type}' fired successfully" in result
