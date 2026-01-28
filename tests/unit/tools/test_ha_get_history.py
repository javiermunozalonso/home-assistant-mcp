"""Unit tests for ha_get_history tool."""

import json
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from home_assistant_mcp.tools.ha_get_history import TOOL_DEF, execute
from home_assistant_mcp.models import HistoryEntry


class TestGetHistoryTool:
    """Tests for ha_get_history tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_get_history"
        assert "historical state changes" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "entity_id" in TOOL_DEF.inputSchema["required"]

        # Check optional parameters
        props = TOOL_DEF.inputSchema["properties"]
        assert "hours_ago" in props
        assert props["hours_ago"]["default"] == 24

    @pytest.mark.asyncio
    async def test_execute_default_hours(self):
        """Test history retrieval with default 24 hours."""
        # Create mock client and response
        mock_client = AsyncMock()
        mock_history = [
            [
                HistoryEntry(
                    entity_id="light.living_room",
                    state="on",
                    last_changed="2024-01-15T10:00:00+00:00",
                    last_updated="2024-01-15T10:00:00+00:00",
                    attributes={},
                ),
                HistoryEntry(
                    entity_id="light.living_room",
                    state="off",
                    last_changed="2024-01-15T12:00:00+00:00",
                    last_updated="2024-01-15T12:00:00+00:00",
                    attributes={},
                ),
            ]
        ]
        mock_client.get_history.return_value = mock_history

        # Execute tool with mocked datetime
        with patch("home_assistant_mcp.tools.ha_get_history.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 0, 0)
            mock_datetime.now.return_value = mock_now

            result = await execute(mock_client, {"entity_id": "light.living_room"})

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "History for light.living_room" in result[0].text
        assert "last 24 hours" in result[0].text

        # Verify JSON structure
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 2
        assert json_data[0]["state"] == "on"
        assert json_data[1]["state"] == "off"

    @pytest.mark.asyncio
    async def test_execute_custom_hours(self):
        """Test history retrieval with custom hours."""
        mock_client = AsyncMock()
        mock_history = [[]]
        mock_client.get_history.return_value = mock_history

        with patch("home_assistant_mcp.tools.ha_get_history.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 15, 14, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            result = await execute(
                mock_client, {"entity_id": "sensor.temperature", "hours_ago": 48}
            )

        # Verify custom hours is reflected in output
        assert "last 48 hours" in result[0].text

        # Verify the start_time calculation
        call_args = mock_client.get_history.call_args
        assert call_args[1]["entity_id"] == "sensor.temperature"
        # The start_time should be approximately 48 hours ago

    @pytest.mark.asyncio
    async def test_execute_empty_history(self):
        """Test history retrieval when no history exists."""
        mock_client = AsyncMock()
        mock_client.get_history.return_value = [[]]

        result = await execute(mock_client, {"entity_id": "light.bedroom"})

        # Verify empty result
        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 0

    @pytest.mark.asyncio
    async def test_execute_multiple_state_changes(self):
        """Test history with multiple state changes."""
        mock_client = AsyncMock()
        mock_history = [
            [
                HistoryEntry(
                    entity_id="switch.fan",
                    state="off",
                    last_changed="2024-01-15T08:00:00+00:00",
                    last_updated="2024-01-15T08:00:00+00:00",
                    attributes={},
                ),
                HistoryEntry(
                    entity_id="switch.fan",
                    state="on",
                    last_changed="2024-01-15T09:00:00+00:00",
                    last_updated="2024-01-15T09:00:00+00:00",
                    attributes={},
                ),
                HistoryEntry(
                    entity_id="switch.fan",
                    state="off",
                    last_changed="2024-01-15T10:00:00+00:00",
                    last_updated="2024-01-15T10:00:00+00:00",
                    attributes={},
                ),
                HistoryEntry(
                    entity_id="switch.fan",
                    state="on",
                    last_changed="2024-01-15T11:00:00+00:00",
                    last_updated="2024-01-15T11:00:00+00:00",
                    attributes={},
                ),
            ]
        ]
        mock_client.get_history.return_value = mock_history

        result = await execute(mock_client, {"entity_id": "switch.fan"})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert len(json_data) == 4
        assert json_data[0]["state"] == "off"
        assert json_data[3]["state"] == "on"

    @pytest.mark.asyncio
    async def test_execute_handles_none_timestamp(self):
        """Test history entry with None timestamp."""
        mock_client = AsyncMock()
        mock_history = [
            [
                HistoryEntry(
                    entity_id="sensor.test",
                    state="42",
                    last_changed=None,
                    last_updated=None,
                    attributes={},
                ),
            ]
        ]
        mock_client.get_history.return_value = mock_history

        result = await execute(mock_client, {"entity_id": "sensor.test"})

        text_lines = result[0].text.split("\n", 1)
        json_data = json.loads(text_lines[1])
        assert json_data[0]["last_changed"] is None
