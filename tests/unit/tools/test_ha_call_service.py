"""Unit tests for ha_call_service tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.services import ha_call_service
from home_assistant_mcp.tool_models import CallServiceInput
from home_assistant_mcp.models import ServiceCallResponse, EntityState


class TestCallServiceTool:
    """Tests for ha_call_service tool."""


    @pytest.mark.asyncio
    async def test_execute_basic_service_call(self):
        """Test basic service call without entity_id or data."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = ServiceCallResponse(success=True, changed_states=[])
        mock_client.call_service.return_value = mock_response

        # Set global client
        core.client = mock_client

        # Execute tool
        params = CallServiceInput(
            domain="homeassistant",
            service="restart",
        )
        result = await ha_call_service(params)

        # Verify
        assert "Service homeassistant.restart called successfully" in result
        mock_client.call_service.assert_called_once_with(
            domain="homeassistant",
            service="restart",
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
        core.client = mock_client

        # Execute tool
        params = CallServiceInput(
            domain="light",
            service="turn_on",
            entity_id="light.living_room",
        )
        result = await ha_call_service(params)

        # Verify
        assert "Service light.turn_on called successfully" in result
        mock_client.call_service.assert_called_once_with(
            domain="light",
            service="turn_on",
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
        core.client = mock_client

        # Execute tool with comma-separated entities
        params = CallServiceInput(
            domain="light",
            service="turn_off",
            entity_id="light.living_room, light.bedroom, light.kitchen",
        )
        await ha_call_service(params)

        # Verify entities were split into a list
        call_args = mock_client.call_service.call_args
        assert call_args.kwargs["entity_id"] == ["light.living_room", "light.bedroom", "light.kitchen"]


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
        core.client = mock_client

        # Execute tool with data
        params = CallServiceInput(
            domain="light",
            service="turn_on",
            entity_id="light.bedroom",
            data={"brightness": 128, "color_temp": 300},
        )
        result = await ha_call_service(params)

        # Verify
        assert "Service light.turn_on called successfully" in result
        mock_client.call_service.assert_called_once_with(
            domain="light",
            service="turn_on",
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
        core.client = mock_client

        # Execute tool
        params = CallServiceInput(
            domain="climate",
            service="set_temperature",
            entity_id="climate.living_room",
            data={"temperature": 22, "hvac_mode": "heat"},
        )
        await ha_call_service(params)

        # Verify both entity_id and data were passed
        mock_client.call_service.assert_called_once_with(
            domain="climate",
            service="set_temperature",
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
        core.client = mock_client

        # Execute tool
        params = CallServiceInput(
            domain="light",
            service="turn_on",
            entity_id="light.living_room, light.bedroom",
        )
        result = await ha_call_service(params)

        # Verify
        assert "called successfully" in result
        assert "light.living_room" in result
        assert "on" in result
