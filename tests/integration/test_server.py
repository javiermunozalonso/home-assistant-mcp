"""Integration tests for MCP Server."""

import json
import os
from unittest.mock import AsyncMock, patch

import pytest

from home_assistant_mcp.client import HomeAssistantClient
from home_assistant_mcp.config import HomeAssistantConfig
from home_assistant_mcp.models import (
    ApiStatus,
    ConfigEntry,
    Dashboard,
    DashboardConfig,
    EntityState,
    ServiceCallResponse,
    ServiceDomain,
)
from home_assistant_mcp.server import call_tool, list_tools
import home_assistant_mcp.server as server_module


@pytest.fixture(autouse=True)
def reset_server_state():
    """Reset server global state before each test."""
    server_module._client = None
    server_module._config = None
    yield
    server_module._client = None
    server_module._config = None


@pytest.fixture
def mock_ha_client(ha_config: HomeAssistantConfig) -> HomeAssistantClient:
    """Create a mock Home Assistant client."""
    client = HomeAssistantClient(ha_config)
    return client


class TestListTools:
    """Tests for the list_tools function."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Test that list_tools returns all expected tools."""
        tools = await list_tools()

        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "ha_health_check",
            "ha_get_config",
            "ha_list_entities",
            "ha_get_entity_state",
            "ha_list_services",
            "ha_call_service",
            "ha_turn_on",
            "ha_turn_off",
            "ha_toggle",
            "ha_get_history",
            "ha_fire_event",
            "ha_list_areas",
            "ha_get_area_entities",
            "ha_get_area_devices",
            "ha_get_entity_area",
            "ha_render_template",
            "ha_list_dashboards",
            "ha_get_dashboard",
            "ha_create_dashboard",
            "ha_update_dashboard",
            "ha_delete_dashboard",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    @pytest.mark.asyncio
    async def test_tools_have_valid_schema(self):
        """Test that all tools have valid input schemas."""
        tools = await list_tools()

        for tool in tools:
            assert tool.name is not None
            assert tool.description is not None
            assert tool.inputSchema is not None
            assert tool.inputSchema.get("type") == "object"
            assert "properties" in tool.inputSchema


class TestCallTool:
    """Tests for the call_tool function."""

    @pytest.mark.asyncio
    async def test_health_check_tool(self, ha_config: HomeAssistantConfig):
        """Test the health check tool."""
        with patch.dict(os.environ, {"HA_URL": ha_config.url, "HA_TOKEN": ha_config.token}):
            mock_client = AsyncMock(spec=HomeAssistantClient)
            mock_client.check_api = AsyncMock(return_value=ApiStatus(message="API running."))

            with patch.object(server_module, "_client", mock_client):
                with patch.object(server_module, "_config", ha_config):
                    # Need to also patch get_client to return our mock
                    with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
                        result = await call_tool("ha_health_check", {})

            assert len(result) == 1
            assert "API running" in result[0].text

    @pytest.mark.asyncio
    async def test_get_config_tool(self, ha_config: HomeAssistantConfig, mock_config: dict):
        """Test the get config tool."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.get_config = AsyncMock(return_value=ConfigEntry(**mock_config))

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_get_config", {})

        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["version"] == "2024.1.0"

    @pytest.mark.asyncio
    async def test_list_entities_tool(self, ha_config: HomeAssistantConfig, mock_entity_states: list[dict]):
        """Test the list entities tool."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.get_states = AsyncMock(
            return_value=[EntityState(**state) for state in mock_entity_states]
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_list_entities", {})

        assert len(result) == 1
        assert "Found 4 entities" in result[0].text

    @pytest.mark.asyncio
    async def test_list_entities_filtered_by_domain(
        self, ha_config: HomeAssistantConfig, mock_entity_states: list[dict]
    ):
        """Test filtering entities by domain."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        light_states = [
            EntityState(**state)
            for state in mock_entity_states
            if state["entity_id"].startswith("light.")
        ]
        mock_client.get_entities_by_domain = AsyncMock(return_value=light_states)

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_list_entities", {"domain": "light"})

        assert len(result) == 1
        assert "Found 2 entities" in result[0].text

    @pytest.mark.asyncio
    async def test_get_entity_state_tool(self, ha_config: HomeAssistantConfig, mock_entity_state: dict):
        """Test getting entity state."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.get_state = AsyncMock(return_value=EntityState(**mock_entity_state))

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_get_entity_state", {"entity_id": "light.living_room"})

        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["entity_id"] == "light.living_room"
        assert response_data["state"] == "on"

    @pytest.mark.asyncio
    async def test_list_services_tool(self, ha_config: HomeAssistantConfig, mock_services: list[dict]):
        """Test listing services."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.get_services = AsyncMock(
            return_value=[ServiceDomain(**svc) for svc in mock_services]
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_list_services", {})

        assert len(result) == 1
        assert "services" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_call_service_tool(self, ha_config: HomeAssistantConfig, mock_entity_state: dict):
        """Test calling a service."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.call_service = AsyncMock(
            return_value=ServiceCallResponse(
                success=True,
                changed_states=[EntityState(**mock_entity_state)],
            )
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool(
                "ha_call_service",
                {
                    "domain": "light",
                    "service": "turn_on",
                    "entity_id": "light.living_room",
                },
            )

        assert len(result) == 1
        assert "called successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_turn_on_tool(self, ha_config: HomeAssistantConfig, mock_entity_state: dict):
        """Test turn on tool."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.turn_on = AsyncMock(
            return_value=ServiceCallResponse(
                success=True,
                changed_states=[EntityState(**mock_entity_state)],
            )
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool(
                "ha_turn_on",
                {"entity_id": "light.living_room", "brightness": 255},
            )

        assert len(result) == 1
        assert "Turned on" in result[0].text
        mock_client.turn_on.assert_called_once_with("light.living_room", brightness=255)

    @pytest.mark.asyncio
    async def test_turn_off_tool(self, ha_config: HomeAssistantConfig, mock_entity_state: dict):
        """Test turn off tool."""
        mock_entity_state["state"] = "off"
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.turn_off = AsyncMock(
            return_value=ServiceCallResponse(
                success=True,
                changed_states=[EntityState(**mock_entity_state)],
            )
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_turn_off", {"entity_id": "light.living_room"})

        assert len(result) == 1
        assert "Turned off" in result[0].text

    @pytest.mark.asyncio
    async def test_toggle_tool(self, ha_config: HomeAssistantConfig, mock_entity_state: dict):
        """Test toggle tool."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.toggle = AsyncMock(
            return_value=ServiceCallResponse(
                success=True,
                changed_states=[EntityState(**mock_entity_state)],
            )
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_toggle", {"entity_id": "light.living_room"})

        assert len(result) == 1
        assert "Toggled" in result[0].text

    @pytest.mark.asyncio
    async def test_fire_event_tool(self, ha_config: HomeAssistantConfig):
        """Test firing an event."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.fire_event = AsyncMock(return_value=True)

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool(
                "ha_fire_event",
                {"event_type": "custom_event", "event_data": {"key": "value"}},
            )

        assert len(result) == 1
        assert "fired successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_unknown_tool(self, ha_config: HomeAssistantConfig):
        """Test handling unknown tool."""
        mock_client = AsyncMock(spec=HomeAssistantClient)

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling(self, ha_config: HomeAssistantConfig):
        """Test error handling in tool calls."""
        from home_assistant_mcp.client import HomeAssistantError

        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.get_state = AsyncMock(
            side_effect=HomeAssistantError("Entity not found", status_code=404)
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_get_entity_state", {"entity_id": "invalid.entity"})

        assert len(result) == 1
        assert "error" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_call_service_with_multiple_entities(self, ha_config: HomeAssistantConfig, mock_entity_state: dict):
        """Test calling service with comma-separated entity IDs."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.call_service = AsyncMock(
            return_value=ServiceCallResponse(success=True, changed_states=[])
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            await call_tool(
                "ha_call_service",
                {
                    "domain": "light",
                    "service": "turn_on",
                    "entity_id": "light.living_room, light.bedroom",
                },
            )

        mock_client.call_service.assert_called_once()
        call_args = mock_client.call_service.call_args
        assert call_args[1]["entity_id"] == ["light.living_room", "light.bedroom"]

    @pytest.mark.asyncio
    async def test_list_dashboards_tool(self, ha_config: HomeAssistantConfig, mock_dashboards_list: list[dict]):
        """Test listing dashboards."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.list_dashboards = AsyncMock(
            return_value=[Dashboard(**dashboard) for dashboard in mock_dashboards_list]
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_list_dashboards", {})

        assert len(result) == 1
        assert "Found 2 dashboards" in result[0].text
        assert "lovelace" in result[0].text
        assert "energy" in result[0].text

    @pytest.mark.asyncio
    async def test_get_dashboard_tool(self, ha_config: HomeAssistantConfig, mock_dashboard_config: dict):
        """Test getting dashboard configuration."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.get_dashboard_config = AsyncMock(
            return_value=DashboardConfig(**mock_dashboard_config)
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_get_dashboard", {"url_path": "test-dashboard"})

        assert len(result) == 1
        response_data = json.loads(result[0].text)
        assert response_data["title"] == "Test Dashboard"
        assert len(response_data["views"]) == 1

    @pytest.mark.asyncio
    async def test_get_dashboard_default(self, ha_config: HomeAssistantConfig, mock_dashboard_config: dict):
        """Test getting default dashboard configuration."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.get_dashboard_config = AsyncMock(
            return_value=DashboardConfig(**mock_dashboard_config)
        )

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_get_dashboard", {})

        assert len(result) == 1
        mock_client.get_dashboard_config.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_create_dashboard_tool(self, ha_config: HomeAssistantConfig, mock_dashboard: dict):
        """Test creating a new dashboard."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.create_dashboard = AsyncMock(return_value=Dashboard(**mock_dashboard))

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool(
                "ha_create_dashboard",
                {
                    "url_path": "test-dashboard",
                    "title": "Test Dashboard",
                    "icon": "mdi:view-dashboard",
                    "show_in_sidebar": True,
                    "require_admin": False,
                },
            )

        assert len(result) == 1
        assert "created successfully" in result[0].text
        mock_client.create_dashboard.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_dashboard_tool(self, ha_config: HomeAssistantConfig, mock_dashboard: dict):
        """Test updating a dashboard."""
        updated_dashboard = mock_dashboard.copy()
        updated_dashboard["title"] = "Updated Dashboard"

        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.update_dashboard = AsyncMock(return_value=Dashboard(**updated_dashboard))

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool(
                "ha_update_dashboard",
                {"dashboard_id": "test_dashboard", "title": "Updated Dashboard"},
            )

        assert len(result) == 1
        assert "updated successfully" in result[0].text
        response_data = json.loads(result[0].text.split(":\n")[1])
        assert response_data["title"] == "Updated Dashboard"

    @pytest.mark.asyncio
    async def test_delete_dashboard_tool(self, ha_config: HomeAssistantConfig):
        """Test deleting a dashboard."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.delete_dashboard = AsyncMock(return_value=True)

        with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
            result = await call_tool("ha_delete_dashboard", {"dashboard_id": "test_dashboard"})

        assert len(result) == 1
        assert "deleted successfully" in result[0].text
        assert "test_dashboard" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_key_error(self, ha_config: HomeAssistantConfig):
        """Test handling missing arguments (KeyError)."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        
        # Simulate a tool that raises KeyError for missing argument
        async def mock_tool_execution(client, args):
            raise KeyError("required_arg")

        with patch("home_assistant_mcp.server.TOOLS_MAP", {"mock_tool": mock_tool_execution}):
            with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
                result = await call_tool("mock_tool", {})
        
        assert len(result) == 1
        assert "Missing required argument" in result[0].text
        assert "required_arg" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_type_error(self, ha_config: HomeAssistantConfig):
        """Test handling invalid argument types (TypeError)."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        
        # Simulate a tool that raises TypeError
        async def mock_tool_execution(client, args):
            raise TypeError("invalid type")

        with patch("home_assistant_mcp.server.TOOLS_MAP", {"mock_tool": mock_tool_execution}):
            with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
                result = await call_tool("mock_tool", {})
        
        assert len(result) == 1
        assert "Invalid argument type" in result[0].text
        assert "invalid type" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_timeout(self, ha_config: HomeAssistantConfig):
        """Test handling request timeouts (httpx.TimeoutException)."""
        import httpx
        mock_client = AsyncMock(spec=HomeAssistantClient)
        
        # Simulate a tool that raises TimeoutException
        async def mock_tool_execution(client, args):
            raise httpx.TimeoutException("Timeout")

        with patch("home_assistant_mcp.server.TOOLS_MAP", {"mock_tool": mock_tool_execution}):
            with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
                result = await call_tool("mock_tool", {})
        
        assert len(result) == 1
        assert "Request timed out" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling_unexpected_exception(self, ha_config: HomeAssistantConfig):
        """Test handling unexpected exceptions."""
        mock_client = AsyncMock(spec=HomeAssistantClient)
        
        # Simulate a tool that raises a generic Exception
        async def mock_tool_execution(client, args):
            raise Exception("Unexpected error")

        with patch("home_assistant_mcp.server.TOOLS_MAP", {"mock_tool": mock_tool_execution}):
            with patch("home_assistant_mcp.server.get_client", return_value=mock_client):
                result = await call_tool("mock_tool", {})
        
        assert len(result) == 1
        assert "Internal error" in result[0].text
        assert "Unexpected error" in result[0].text
