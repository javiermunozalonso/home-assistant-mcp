"""Unit tests for ha_get_history tool."""

import json
import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.history import ha_get_history
from home_assistant_mcp.tool_models import GetHistoryInput
from home_assistant_mcp.models import HistoryEntry


class TestGetHistoryTool:
    """Tests for ha_get_history tool."""



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
        core.client = mock_client
        result = await ha_get_history(
            GetHistoryInput(entity_id="light.living_room", response_format="json")
        )

        # Verify
        # Verify
        # Verify JSON structure
        json_data = json.loads(result)
        entries = json_data["entries"]
        assert len(entries) == 2
        assert entries[0]["state"] == "on"
        assert entries[1]["state"] == "off"



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
        core.client = mock_client

        result = await ha_get_history(
            GetHistoryInput(entity_id="switch.fan", response_format="json")
        )

        json_data = json.loads(result)
        entries = json_data["entries"]
        assert len(entries) == 4
        assert entries[0]["state"] == "off"
        assert entries[3]["state"] == "on"

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
        core.client = mock_client

        result = await ha_get_history(
            GetHistoryInput(entity_id="sensor.test", response_format="json")
        )

        json_data = json.loads(result)
        entries = json_data["entries"]
        assert entries[0]["last_changed"] is None
