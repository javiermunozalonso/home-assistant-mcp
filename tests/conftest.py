"""Pytest fixtures for Home Assistant MCP Server tests."""

import pytest

from home_assistant_mcp.config import HomeAssistantConfig
from home_assistant_mcp.client import HomeAssistantClient


@pytest.fixture
def ha_config() -> HomeAssistantConfig:
    """Create a test Home Assistant configuration."""
    return HomeAssistantConfig(
        url="http://localhost:8123",
        token="test_token_12345",
        verify_ssl=False,
        timeout=10.0,
    )


@pytest.fixture
def ha_client(ha_config: HomeAssistantConfig) -> HomeAssistantClient:
    """Create a test Home Assistant client."""
    return HomeAssistantClient(ha_config)


@pytest.fixture
def mock_entity_state() -> dict:
    """Create a mock entity state response."""
    return {
        "entity_id": "light.living_room",
        "state": "on",
        "attributes": {
            "friendly_name": "Living Room Light",
            "brightness": 255,
            "color_mode": "brightness",
            "supported_features": 1,
        },
        "last_changed": "2024-01-15T10:30:00+00:00",
        "last_updated": "2024-01-15T10:30:00+00:00",
        "context": {"id": "abc123", "parent_id": None, "user_id": None},
    }


@pytest.fixture
def mock_entity_states() -> list[dict]:
    """Create a list of mock entity states."""
    return [
        {
            "entity_id": "light.living_room",
            "state": "on",
            "attributes": {"friendly_name": "Living Room Light", "brightness": 255},
            "last_changed": "2024-01-15T10:30:00+00:00",
            "last_updated": "2024-01-15T10:30:00+00:00",
        },
        {
            "entity_id": "light.bedroom",
            "state": "off",
            "attributes": {"friendly_name": "Bedroom Light"},
            "last_changed": "2024-01-15T09:00:00+00:00",
            "last_updated": "2024-01-15T09:00:00+00:00",
        },
        {
            "entity_id": "switch.kitchen",
            "state": "on",
            "attributes": {"friendly_name": "Kitchen Switch"},
            "last_changed": "2024-01-15T08:00:00+00:00",
            "last_updated": "2024-01-15T08:00:00+00:00",
        },
        {
            "entity_id": "sensor.temperature",
            "state": "22.5",
            "attributes": {"friendly_name": "Temperature", "unit_of_measurement": "°C"},
            "last_changed": "2024-01-15T10:35:00+00:00",
            "last_updated": "2024-01-15T10:35:00+00:00",
        },
    ]


@pytest.fixture
def mock_services() -> list[dict]:
    """Create mock services response."""
    return [
        {
            "domain": "light",
            "services": {
                "turn_on": {
                    "name": "Turn on",
                    "description": "Turn on a light",
                    "fields": {
                        "brightness": {
                            "description": "Brightness level",
                            "example": 255,
                        },
                    },
                },
                "turn_off": {
                    "name": "Turn off",
                    "description": "Turn off a light",
                    "fields": {},
                },
                "toggle": {
                    "name": "Toggle",
                    "description": "Toggle a light",
                    "fields": {},
                },
            },
        },
        {
            "domain": "switch",
            "services": {
                "turn_on": {
                    "name": "Turn on",
                    "description": "Turn on a switch",
                    "fields": {},
                },
                "turn_off": {
                    "name": "Turn off",
                    "description": "Turn off a switch",
                    "fields": {},
                },
            },
        },
    ]


@pytest.fixture
def mock_api_status() -> dict:
    """Create mock API status response."""
    return {"message": "API running."}


@pytest.fixture
def mock_config() -> dict:
    """Create mock Home Assistant config response."""
    return {
        "components": ["homeassistant", "light", "switch", "sensor"],
        "config_dir": "/config",
        "elevation": 100,
        "latitude": 40.7128,
        "longitude": -74.0060,
        "location_name": "Home",
        "time_zone": "America/New_York",
        "unit_system": {"length": "km", "temperature": "°C"},
        "version": "2024.1.0",
    }


@pytest.fixture
def mock_dashboard() -> dict:
    """Create a mock dashboard."""
    return {
        "id": "test_dashboard",
        "url_path": "test-dashboard",
        "title": "Test Dashboard",
        "icon": "mdi:view-dashboard",
        "show_in_sidebar": True,
        "require_admin": False,
        "mode": "storage",
    }


@pytest.fixture
def mock_dashboards_list() -> list[dict]:
    """Create a list of mock dashboards."""
    return [
        {
            "id": "lovelace",
            "url_path": "lovelace",
            "title": "Home",
            "icon": "mdi:home",
            "show_in_sidebar": True,
            "require_admin": False,
            "mode": "storage",
        },
        {
            "id": "energy",
            "url_path": "energy",
            "title": "Energy",
            "icon": "mdi:lightning-bolt",
            "show_in_sidebar": True,
            "require_admin": False,
            "mode": "storage",
        },
    ]


@pytest.fixture
def mock_dashboard_config() -> dict:
    """Create a mock dashboard configuration."""
    return {
        "title": "Test Dashboard",
        "views": [
            {
                "title": "Overview",
                "path": "overview",
                "cards": [
                    {
                        "type": "entities",
                        "entities": ["light.living_room", "switch.kitchen"],
                    }
                ],
            }
        ],
    }
