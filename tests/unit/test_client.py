"""Unit tests for Home Assistant client."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_httpx import HTTPXMock

from ha_mcp_server.client import HomeAssistantClient, HomeAssistantError
from ha_mcp_server.config import HomeAssistantConfig


class TestHomeAssistantClient:
    """Tests for HomeAssistantClient."""

    @pytest.fixture
    def client(self, ha_config: HomeAssistantConfig) -> HomeAssistantClient:
        """Create a client for testing."""
        return HomeAssistantClient(ha_config)

    @pytest.mark.asyncio
    async def test_check_api(self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_api_status: dict):
        """Test API health check."""
        httpx_mock.add_response(url="http://localhost:8123/api/", json=mock_api_status)

        async with client:
            result = await client.check_api()
            assert result.message == "API running."

    @pytest.mark.asyncio
    async def test_get_config(self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_config: dict):
        """Test getting Home Assistant config."""
        httpx_mock.add_response(url="http://localhost:8123/api/config", json=mock_config)

        async with client:
            result = await client.get_config()
            assert result.version == "2024.1.0"
            assert result.location_name == "Home"

    @pytest.mark.asyncio
    async def test_get_states(
        self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_states: list[dict]
    ):
        """Test getting all entity states."""
        httpx_mock.add_response(url="http://localhost:8123/api/states", json=mock_entity_states)

        async with client:
            result = await client.get_states()
            assert len(result) == 4
            assert result[0].entity_id == "light.living_room"

    @pytest.mark.asyncio
    async def test_get_state(
        self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_state: dict
    ):
        """Test getting a specific entity state."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/states/light.living_room",
            json=mock_entity_state,
        )

        async with client:
            result = await client.get_state("light.living_room")
            assert result.entity_id == "light.living_room"
            assert result.state == "on"
            assert result.attributes["brightness"] == 255

    @pytest.mark.asyncio
    async def test_get_services(
        self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_services: list[dict]
    ):
        """Test getting available services."""
        httpx_mock.add_response(url="http://localhost:8123/api/services", json=mock_services)

        async with client:
            result = await client.get_services()
            assert len(result) == 2
            assert result[0].domain == "light"
            assert "turn_on" in result[0].services

    @pytest.mark.asyncio
    async def test_call_service(self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_state: dict):
        """Test calling a service."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/services/light/turn_on",
            json=[mock_entity_state],
        )

        async with client:
            result = await client.call_service(
                "light", "turn_on", entity_id="light.living_room"
            )
            assert result.success is True
            assert len(result.changed_states) == 1

    @pytest.mark.asyncio
    async def test_call_service_with_data(
        self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_state: dict
    ):
        """Test calling a service with additional data."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/services/light/turn_on",
            json=[mock_entity_state],
        )

        async with client:
            result = await client.call_service(
                "light",
                "turn_on",
                entity_id="light.living_room",
                data={"brightness": 128},
            )
            assert result.success is True

            # Verify the request had the correct data
            request = httpx_mock.get_request()
            assert request is not None
            import json
            body = json.loads(request.content)
            assert body["entity_id"] == "light.living_room"
            assert body["brightness"] == 128

    @pytest.mark.asyncio
    async def test_turn_on(self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_state: dict):
        """Test turn_on helper method."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/services/light/turn_on",
            json=[mock_entity_state],
        )

        async with client:
            result = await client.turn_on("light.living_room", brightness=200)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_turn_off(self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_state: dict):
        """Test turn_off helper method."""
        mock_entity_state["state"] = "off"
        httpx_mock.add_response(
            url="http://localhost:8123/api/services/light/turn_off",
            json=[mock_entity_state],
        )

        async with client:
            result = await client.turn_off("light.living_room")
            assert result.success is True

    @pytest.mark.asyncio
    async def test_toggle(self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_state: dict):
        """Test toggle helper method."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/services/light/toggle",
            json=[mock_entity_state],
        )

        async with client:
            result = await client.toggle("light.living_room")
            assert result.success is True

    @pytest.mark.asyncio
    async def test_get_entities_by_domain(
        self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_entity_states: list[dict]
    ):
        """Test filtering entities by domain."""
        httpx_mock.add_response(url="http://localhost:8123/api/states", json=mock_entity_states)

        async with client:
            result = await client.get_entities_by_domain("light")
            assert len(result) == 2
            assert all(e.entity_id.startswith("light.") for e in result)

    @pytest.mark.asyncio
    async def test_fire_event(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test firing an event."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/events/custom_event",
            json={"message": "Event fired."},
        )

        async with client:
            result = await client.fire_event("custom_event", {"data": "value"})
            assert result is True

    @pytest.mark.asyncio
    async def test_http_error_handling(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test HTTP error handling."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/states/invalid.entity",
            status_code=404,
            json={"message": "Entity not found"},
        )

        async with client:
            with pytest.raises(HomeAssistantError) as exc_info:
                await client.get_state("invalid.entity")
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_context_manager(self, ha_config: HomeAssistantConfig, httpx_mock: HTTPXMock, mock_api_status: dict):
        """Test client as async context manager."""
        httpx_mock.add_response(url="http://localhost:8123/api/", json=mock_api_status)

        async with HomeAssistantClient(ha_config) as client:
            result = await client.check_api()
            assert result.message == "API running."

    @pytest.mark.asyncio
    async def test_headers(self, client: HomeAssistantClient, httpx_mock: HTTPXMock, mock_api_status: dict):
        """Test that correct headers are sent."""
        httpx_mock.add_response(url="http://localhost:8123/api/", json=mock_api_status)

        async with client:
            await client.check_api()

            request = httpx_mock.get_request()
            assert request is not None
            assert request.headers["Authorization"] == "Bearer test_token_12345"
            assert request.headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_render_template(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test rendering a Jinja2 template."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="['salon', 'cocina', 'dormitorio']",
        )

        async with client:
            result = await client.render_template("{{ areas() | list }}")
            assert result == "['salon', 'cocina', 'dormitorio']"

    @pytest.mark.asyncio
    async def test_get_areas(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting all areas."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="['salon', 'cocina', 'dormitorio']",
        )

        async with client:
            result = await client.get_areas()
            assert result == ["salon", "cocina", "dormitorio"]
            assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_area_entities(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting entities in an area."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="['light.salon', 'switch.salon', 'sensor.salon_temp']",
        )

        async with client:
            result = await client.get_area_entities("salon")
            assert len(result) == 3
            assert "light.salon" in result

    @pytest.mark.asyncio
    async def test_get_area_entities_with_domain(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting entities in an area filtered by domain."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="['light.salon', 'light.lampara']",
        )

        async with client:
            result = await client.get_area_entities("salon", domain="light")
            assert len(result) == 2
            assert all(e.startswith("light.") for e in result)

    @pytest.mark.asyncio
    async def test_get_area_devices(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting devices in an area."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="['device_1', 'device_2']",
        )

        async with client:
            result = await client.get_area_devices("salon")
            assert len(result) == 2
            assert "device_1" in result

    @pytest.mark.asyncio
    async def test_get_entity_area(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting the area for an entity."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="Salón",
        )

        async with client:
            result = await client.get_entity_area("light.lampara_tele")
            assert result == "Salón"

    @pytest.mark.asyncio
    async def test_get_entity_area_none(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting the area for an entity not assigned to any area."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="",
        )

        async with client:
            result = await client.get_entity_area("light.unassigned")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_area_id(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting area ID from area name."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="salon",
        )

        async with client:
            result = await client.get_area_id("Salón")
            assert result == "salon"

    @pytest.mark.asyncio
    async def test_get_area_name(self, client: HomeAssistantClient, httpx_mock: HTTPXMock):
        """Test getting area name from area ID."""
        httpx_mock.add_response(
            url="http://localhost:8123/api/template",
            text="Salón",
        )

        async with client:
            result = await client.get_area_name("salon")
            assert result == "Salón"

    @pytest.mark.asyncio
    async def test_get_ws_url_http(self, client: HomeAssistantClient):
        """Test WebSocket URL conversion from HTTP."""
        url = client._get_ws_url()
        assert url == "ws://localhost:8123/api/websocket"

    @pytest.mark.asyncio
    async def test_get_ws_url_https(self, ha_config: HomeAssistantConfig):
        """Test WebSocket URL conversion from HTTPS."""
        ha_config.url = "https://example.com:8123"
        client = HomeAssistantClient(ha_config)
        url = client._get_ws_url()
        assert url == "wss://example.com:8123/api/websocket"

    @pytest.mark.asyncio
    async def test_list_dashboards(self, client: HomeAssistantClient, mock_dashboards_list: list[dict]):
        """Test listing all dashboards."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": mock_dashboards_list}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            async with client:
                result = await client.list_dashboards()
                assert len(result) == 2
                assert result[0].id == "lovelace"
                assert result[0].title == "Home"
                assert result[1].id == "energy"

    @pytest.mark.asyncio
    async def test_get_dashboard_config(self, client: HomeAssistantClient, mock_dashboard_config: dict):
        """Test getting dashboard configuration."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": mock_dashboard_config}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            async with client:
                result = await client.get_dashboard_config()
                assert result.title == "Test Dashboard"
                assert len(result.views) == 1
                assert result.views[0]["title"] == "Overview"

    @pytest.mark.asyncio
    async def test_get_dashboard_config_with_url_path(self, client: HomeAssistantClient, mock_dashboard_config: dict):
        """Test getting specific dashboard configuration by URL path."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": mock_dashboard_config}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            async with client:
                result = await client.get_dashboard_config(url_path="test-dashboard")
                assert result.title == "Test Dashboard"

                # Verify the request included url_path
                sent_message = json.loads(mock_ws.send.call_args_list[1][0][0])
                assert sent_message["url_path"] == "test-dashboard"

    @pytest.mark.asyncio
    async def test_create_dashboard(self, client: HomeAssistantClient, mock_dashboard: dict):
        """Test creating a new dashboard."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": mock_dashboard}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            async with client:
                result = await client.create_dashboard(
                    url_path="test-dashboard",
                    title="Test Dashboard",
                    icon="mdi:view-dashboard",
                    show_in_sidebar=True,
                    require_admin=False,
                )
                assert result.id == "test_dashboard"
                assert result.url_path == "test-dashboard"
                assert result.title == "Test Dashboard"
                assert result.icon == "mdi:view-dashboard"

    @pytest.mark.asyncio
    async def test_update_dashboard(self, client: HomeAssistantClient, mock_dashboard: dict):
        """Test updating a dashboard."""
        updated_dashboard = mock_dashboard.copy()
        updated_dashboard["title"] = "Updated Dashboard"

        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": updated_dashboard}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            async with client:
                result = await client.update_dashboard("test_dashboard", title="Updated Dashboard")
                assert result.title == "Updated Dashboard"
                assert result.id == "test_dashboard"

    @pytest.mark.asyncio
    async def test_delete_dashboard(self, client: HomeAssistantClient):
        """Test deleting a dashboard."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": None}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            async with client:
                result = await client.delete_dashboard("test_dashboard")
                assert result is True

    @pytest.mark.asyncio
    async def test_save_dashboard_config(self, client: HomeAssistantClient):
        """Test saving dashboard configuration."""
        config = {
            "views": [
                {"title": "Home", "cards": [{"type": "entities", "entities": ["light.living_room"]}]}
            ]
        }

        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": None}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            async with client:
                result = await client.save_dashboard_config(config, url_path="test-dashboard")
                assert result is True

    @pytest.mark.asyncio
    async def test_ws_auth_failure(self, client: HomeAssistantClient):
        """Test WebSocket authentication failure."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_invalid", "message": "Invalid token"}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            with pytest.raises(HomeAssistantError) as exc_info:
                async with client:
                    await client.list_dashboards()
            assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ws_request_error(self, client: HomeAssistantClient):
        """Test WebSocket request error handling."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({
                "id": 1,
                "type": "result",
                "success": False,
                "error": {"message": "Dashboard not found"}
            }),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws):
            with pytest.raises(HomeAssistantError) as exc_info:
                async with client:
                    await client.list_dashboards()
            assert "Dashboard not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_ws_connection_reuse(self, client: HomeAssistantClient, mock_dashboard: dict):
        """Test that WebSocket connection is reused across multiple requests."""
        mock_ws = AsyncMock()
        mock_ws.closed = False
        mock_ws.recv = AsyncMock(side_effect=[
            json.dumps({"type": "auth_required"}),
            json.dumps({"type": "auth_ok"}),
            json.dumps({"id": 1, "type": "result", "success": True, "result": [mock_dashboard]}),
            json.dumps({"id": 2, "type": "result", "success": True, "result": [mock_dashboard]}),
        ])
        mock_ws.send = AsyncMock()

        with patch("ha_mcp_server.client.websockets.connect", new_callable=AsyncMock, return_value=mock_ws) as mock_connect:
            async with client:
                await client.list_dashboards()
                await client.list_dashboards()

                # WebSocket should only be connected once (auth happens once)
                assert mock_connect.call_count == 1
                # But we should have sent two requests (plus one auth message)
                assert mock_ws.send.call_count == 3  # 1 auth + 2 requests
