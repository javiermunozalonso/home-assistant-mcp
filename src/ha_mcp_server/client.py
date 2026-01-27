"""Home Assistant REST API client."""

import asyncio
import json
from datetime import datetime
from typing import Any

import httpx
import websockets
from websockets.client import WebSocketClientProtocol

from .config import HomeAssistantConfig
from .models import (
    ApiStatus,
    ConfigEntry,
    Dashboard,
    DashboardConfig,
    EntityState,
    HistoryEntry,
    ServiceCallResponse,
    ServiceDomain,
)


class HomeAssistantError(Exception):
    """Base exception for Home Assistant client errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class HomeAssistantClient:
    """Async client for Home Assistant REST API."""

    def __init__(self, config: HomeAssistantConfig):
        """Initialize the client with configuration.

        Args:
            config: Home Assistant configuration
        """
        self.config = config
        self._client: httpx.AsyncClient | None = None
        self._ws_client: WebSocketClientProtocol | None = None
        self._ws_id: int = 1
        self._ws_lock = asyncio.Lock()

    @property
    def _headers(self) -> dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.config.url,
                headers=self._headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP and WebSocket clients."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
        if self._ws_client:
            try:
                await self._ws_client.close()
            except Exception:
                pass  # Already closed or error closing
            finally:
                self._ws_client = None

    async def __aenter__(self) -> "HomeAssistantClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Make an API request.

        Args:
            method: HTTP method
            endpoint: API endpoint (without /api prefix)
            json: JSON body for POST requests

        Returns:
            Parsed JSON response

        Raises:
            HomeAssistantError: If the request fails
        """
        client = await self._get_client()
        url = f"/api{endpoint}"

        try:
            response = await client.request(method, url, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HomeAssistantError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise HomeAssistantError(f"Request error: {e}") from e

    async def check_api(self) -> ApiStatus:
        """Check if the API is running.

        Returns:
            API status message
        """
        data = await self._request("GET", "/")
        return ApiStatus(**data)

    async def get_config(self) -> ConfigEntry:
        """Get Home Assistant configuration.

        Returns:
            Configuration entry
        """
        data = await self._request("GET", "/config")
        return ConfigEntry(**data)

    async def get_states(self) -> list[EntityState]:
        """Get all entity states.

        Returns:
            List of all entity states
        """
        data = await self._request("GET", "/states")
        return [EntityState(**item) for item in data]

    async def get_state(self, entity_id: str) -> EntityState:
        """Get state of a specific entity.

        Args:
            entity_id: Entity ID (e.g., 'light.living_room')

        Returns:
            Entity state
        """
        data = await self._request("GET", f"/states/{entity_id}")
        return EntityState(**data)

    async def get_services(self) -> list[ServiceDomain]:
        """Get all available services.

        Returns:
            List of service domains with their services
        """
        data = await self._request("GET", "/services")
        return [ServiceDomain(**item) for item in data]

    async def call_service(
        self,
        domain: str,
        service: str,
        entity_id: str | list[str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> ServiceCallResponse:
        """Call a Home Assistant service.

        Args:
            domain: Service domain (e.g., 'light', 'switch')
            service: Service name (e.g., 'turn_on', 'turn_off')
            entity_id: Target entity ID(s)
            data: Additional service data

        Returns:
            Service call response with changed states
        """
        payload: dict[str, Any] = data.copy() if data else {}
        if entity_id:
            payload["entity_id"] = entity_id

        result = await self._request("POST", f"/services/{domain}/{service}", json=payload)

        changed_states = [EntityState(**item) for item in result] if result else []
        return ServiceCallResponse(success=True, changed_states=changed_states)

    async def get_history(
        self,
        entity_id: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[list[HistoryEntry]]:
        """Get history for entities.

        Args:
            entity_id: Optional entity ID to filter
            start_time: Start of history period
            end_time: End of history period

        Returns:
            List of history entries grouped by entity
        """
        endpoint = "/history/period"
        if start_time:
            endpoint += f"/{start_time.isoformat()}"

        params = []
        if entity_id:
            params.append(f"filter_entity_id={entity_id}")
        if end_time:
            params.append(f"end_time={end_time.isoformat()}")

        if params:
            endpoint += "?" + "&".join(params)

        data = await self._request("GET", endpoint)
        return [
            [HistoryEntry(**entry) for entry in entity_history] for entity_history in data
        ]

    async def fire_event(self, event_type: str, event_data: dict[str, Any] | None = None) -> bool:
        """Fire an event.

        Args:
            event_type: Type of event to fire
            event_data: Optional event data

        Returns:
            True if successful
        """
        await self._request("POST", f"/events/{event_type}", json=event_data or {})
        return True

    async def get_entities_by_domain(self, domain: str) -> list[EntityState]:
        """Get all entities for a specific domain.

        Args:
            domain: Domain to filter (e.g., 'light', 'switch', 'sensor')

        Returns:
            List of entity states in the domain
        """
        all_states = await self.get_states()
        return [state for state in all_states if state.entity_id.startswith(f"{domain}.")]

    async def toggle(self, entity_id: str) -> ServiceCallResponse:
        """Toggle an entity.

        Args:
            entity_id: Entity to toggle

        Returns:
            Service call response
        """
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "toggle", entity_id=entity_id)

    async def turn_on(
        self, entity_id: str, **kwargs: Any
    ) -> ServiceCallResponse:
        """Turn on an entity.

        Args:
            entity_id: Entity to turn on
            **kwargs: Additional parameters (brightness, color, etc.)

        Returns:
            Service call response
        """
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_on", entity_id=entity_id, data=kwargs)

    async def turn_off(self, entity_id: str) -> ServiceCallResponse:
        """Turn off an entity.

        Args:
            entity_id: Entity to turn off

        Returns:
            Service call response
        """
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_off", entity_id=entity_id)

    async def render_template(self, template: str) -> str:
        """Render a Home Assistant Jinja2 template.

        Args:
            template: Jinja2 template string to render

        Returns:
            Rendered template result as string
        """
        client = await self._get_client()
        url = "/api/template"

        try:
            response = await client.post(url, json={"template": template})
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            raise HomeAssistantError(
                f"HTTP error {e.response.status_code}: {e.response.text}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise HomeAssistantError(f"Request error: {e}") from e

    async def get_areas(self) -> list[str]:
        """Get all configured areas.

        Returns:
            List of area IDs
        """
        result = await self.render_template("{{ areas() | list }}")
        import ast
        return ast.literal_eval(result)

    async def get_area_entities(self, area: str, domain: str | None = None) -> list[str]:
        """Get all entities in an area.

        Args:
            area: Area ID or name
            domain: Optional domain to filter (e.g., 'light', 'switch')

        Returns:
            List of entity IDs in the area
        """
        if domain:
            template = f'{{{{ area_entities("{area}") | select("match", "{domain}") | list }}}}'
        else:
            template = f'{{{{ area_entities("{area}") | list }}}}'
        result = await self.render_template(template)
        import ast
        return ast.literal_eval(result)

    async def get_area_devices(self, area: str) -> list[str]:
        """Get all devices in an area.

        Args:
            area: Area ID or name

        Returns:
            List of device IDs in the area
        """
        result = await self.render_template(f'{{{{ area_devices("{area}") | list }}}}')
        import ast
        return ast.literal_eval(result)

    async def get_entity_area(self, entity_id: str) -> str | None:
        """Get the area name for an entity.

        Args:
            entity_id: Entity ID

        Returns:
            Area name or None if not assigned
        """
        result = await self.render_template(f'{{{{ area_name("{entity_id}") }}}}')
        return result.strip() if result.strip() else None

    async def get_area_id(self, area_name: str) -> str | None:
        """Get the area ID from an area name.

        Args:
            area_name: Area name

        Returns:
            Area ID or None if not found
        """
        result = await self.render_template(f'{{{{ area_id("{area_name}") }}}}')
        return result.strip() if result.strip() and result.strip() != "None" else None

    async def get_area_name(self, area_id: str) -> str | None:
        """Get the area name from an area ID.

        Args:
            area_id: Area ID

        Returns:
            Area name or None if not found
        """
        result = await self.render_template(f'{{{{ area_name("{area_id}") }}}}')
        return result.strip() if result.strip() and result.strip() != "None" else None

    def _get_ws_url(self) -> str:
        """Convert HTTP URL to WebSocket URL.

        Returns:
            WebSocket URL
        """
        url = self.config.url
        if url.startswith("https://"):
            return url.replace("https://", "wss://") + "/api/websocket"
        elif url.startswith("http://"):
            return url.replace("http://", "ws://") + "/api/websocket"
        else:
            raise HomeAssistantError(f"Invalid URL format: {url}")

    async def _get_ws_client(self) -> WebSocketClientProtocol:
        """Get or create the WebSocket client with authentication.

        Returns:
            Authenticated WebSocket connection

        Raises:
            HomeAssistantError: If connection or authentication fails
        """
        # Check if we have an existing open connection
        if self._ws_client:
            try:
                # Try to check if connection is still open
                if hasattr(self._ws_client, 'closed'):
                    if not self._ws_client.closed:
                        return self._ws_client
                elif hasattr(self._ws_client, 'open'):
                    if self._ws_client.open:
                        return self._ws_client
                else:
                    # If we can't determine state, assume we need a new connection
                    return self._ws_client
            except Exception:
                # Connection check failed, create a new one
                pass

        ws_url = self._get_ws_url()

        try:
            # Connect to WebSocket
            self._ws_client = await websockets.connect(
                ws_url,
                ssl=self.config.verify_ssl if ws_url.startswith("wss://") else None,
            )

            # Receive auth_required message
            auth_msg = await self._ws_client.recv()
            auth_data = json.loads(auth_msg)

            if auth_data.get("type") != "auth_required":
                raise HomeAssistantError(f"Unexpected message: {auth_data}")

            # Send auth token
            await self._ws_client.send(
                json.dumps({"type": "auth", "access_token": self.config.token})
            )

            # Receive auth response
            auth_response = await self._ws_client.recv()
            auth_result = json.loads(auth_response)

            if auth_result.get("type") == "auth_invalid":
                raise HomeAssistantError(
                    f"Authentication failed: {auth_result.get('message', 'Invalid token')}"
                )
            elif auth_result.get("type") != "auth_ok":
                raise HomeAssistantError(f"Unexpected auth response: {auth_result}")

            return self._ws_client

        except websockets.exceptions.WebSocketException as e:
            raise HomeAssistantError(f"WebSocket connection error: {e}") from e
        except json.JSONDecodeError as e:
            raise HomeAssistantError(f"Failed to parse WebSocket message: {e}") from e

    async def _ws_request(self, message_type: str, **kwargs: Any) -> Any:
        """Send a WebSocket request and receive the response.

        Args:
            message_type: WebSocket message type
            **kwargs: Additional message parameters

        Returns:
            Response result

        Raises:
            HomeAssistantError: If the request fails
        """
        async with self._ws_lock:
            ws = await self._get_ws_client()

            # Prepare message with auto-incrementing ID
            message_id = self._ws_id
            self._ws_id += 1

            message = {"id": message_id, "type": message_type, **kwargs}

            try:
                # Send message
                await ws.send(json.dumps(message))

                # Receive response
                response_raw = await ws.recv()
                response = json.loads(response_raw)

                # Verify message ID matches
                if response.get("id") != message_id:
                    raise HomeAssistantError(
                        f"Message ID mismatch: expected {message_id}, got {response.get('id')}"
                    )

                # Check for success
                if not response.get("success", False):
                    error = response.get("error", {})
                    error_msg = error.get("message", "Unknown error")
                    raise HomeAssistantError(f"WebSocket request failed: {error_msg}")

                return response.get("result")

            except websockets.exceptions.WebSocketException as e:
                raise HomeAssistantError(f"WebSocket error: {e}") from e
            except json.JSONDecodeError as e:
                raise HomeAssistantError(f"Failed to parse response: {e}") from e

    async def list_dashboards(self) -> list[Dashboard]:
        """List all Lovelace dashboards.

        Returns:
            List of dashboards
        """
        result = await self._ws_request("lovelace/dashboards/list")
        return [Dashboard(**item) for item in result]

    async def get_dashboard_config(self, url_path: str | None = None) -> DashboardConfig:
        """Get configuration of a specific dashboard.

        Args:
            url_path: Dashboard URL path (None for default dashboard)

        Returns:
            Dashboard configuration
        """
        params = {}
        if url_path is not None:
            params["url_path"] = url_path

        result = await self._ws_request("lovelace/config", **params)
        return DashboardConfig(**result)

    async def create_dashboard(
        self,
        url_path: str,
        title: str,
        icon: str | None = None,
        show_in_sidebar: bool = True,
        require_admin: bool = False,
    ) -> Dashboard:
        """Create a new Lovelace dashboard.

        Args:
            url_path: URL path for the dashboard
            title: Dashboard title
            icon: Optional dashboard icon (e.g., 'mdi:home')
            show_in_sidebar: Show in sidebar (default: True)
            require_admin: Require admin access (default: False)

        Returns:
            Created dashboard
        """
        params: dict[str, Any] = {
            "url_path": url_path,
            "title": title,
            "show_in_sidebar": show_in_sidebar,
            "require_admin": require_admin,
        }
        if icon:
            params["icon"] = icon

        result = await self._ws_request("lovelace/dashboards/create", **params)
        return Dashboard(**result)

    async def update_dashboard(self, dashboard_id: str, **updates: Any) -> Dashboard:
        """Update an existing dashboard.

        Args:
            dashboard_id: Dashboard ID to update
            **updates: Fields to update (title, icon, show_in_sidebar, etc.)

        Returns:
            Updated dashboard
        """
        params = {"dashboard_id": dashboard_id, **updates}
        result = await self._ws_request("lovelace/dashboards/update", **params)
        return Dashboard(**result)

    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard.

        Args:
            dashboard_id: Dashboard ID to delete

        Returns:
            True if successful
        """
        await self._ws_request("lovelace/dashboards/delete", dashboard_id=dashboard_id)
        return True

    async def save_dashboard_config(
        self, config: dict[str, Any], url_path: str | None = None
    ) -> bool:
        """Save dashboard configuration.

        Args:
            config: Dashboard configuration (views, etc.)
            url_path: Dashboard URL path (None for default)

        Returns:
            True if successful
        """
        params: dict[str, Any] = {"config": config}
        if url_path is not None:
            params["url_path"] = url_path

        await self._ws_request("lovelace/config/save", **params)
        return True
