"""Unit tests for Pydantic models."""

from datetime import datetime

import pytest

from ha_mcp_server.models import (
    ApiStatus,
    ConfigEntry,
    EntityState,
    HistoryEntry,
    Service,
    ServiceCallResponse,
    ServiceDomain,
    ServiceField,
)


class TestEntityState:
    """Tests for EntityState model."""

    def test_minimal_entity_state(self):
        """Test creating entity state with minimal data."""
        state = EntityState(entity_id="light.test", state="on")
        assert state.entity_id == "light.test"
        assert state.state == "on"
        assert state.attributes == {}

    def test_full_entity_state(self):
        """Test creating entity state with all fields."""
        state = EntityState(
            entity_id="light.living_room",
            state="on",
            attributes={"brightness": 255, "friendly_name": "Living Room"},
            last_changed=datetime(2024, 1, 15, 10, 30, 0),
            last_updated=datetime(2024, 1, 15, 10, 30, 0),
            context={"id": "abc123"},
        )
        assert state.entity_id == "light.living_room"
        assert state.attributes["brightness"] == 255
        assert state.last_changed == datetime(2024, 1, 15, 10, 30, 0)

    def test_entity_state_from_dict(self, mock_entity_state):
        """Test creating entity state from dictionary."""
        state = EntityState(**mock_entity_state)
        assert state.entity_id == "light.living_room"
        assert state.state == "on"
        assert state.attributes["brightness"] == 255


class TestServiceModels:
    """Tests for service-related models."""

    def test_service_field(self):
        """Test ServiceField model."""
        field = ServiceField(
            name="brightness",
            description="Brightness level 0-255",
            required=False,
            example=255,
        )
        assert field.name == "brightness"
        assert field.required is False

    def test_service(self):
        """Test Service model."""
        service = Service(
            name="turn_on",
            description="Turn on a light",
            fields={
                "brightness": ServiceField(description="Brightness", example=255),
            },
        )
        assert service.name == "turn_on"
        assert "brightness" in service.fields

    def test_service_domain(self):
        """Test ServiceDomain model."""
        domain = ServiceDomain(
            domain="light",
            services={
                "turn_on": Service(name="Turn on", description="Turn on"),
                "turn_off": Service(name="Turn off", description="Turn off"),
            },
        )
        assert domain.domain == "light"
        assert len(domain.services) == 2


class TestApiStatus:
    """Tests for ApiStatus model."""

    def test_api_status(self, mock_api_status):
        """Test ApiStatus model."""
        status = ApiStatus(**mock_api_status)
        assert status.message == "API running."


class TestConfigEntry:
    """Tests for ConfigEntry model."""

    def test_config_entry(self, mock_config):
        """Test ConfigEntry model."""
        config = ConfigEntry(**mock_config)
        assert config.version == "2024.1.0"
        assert config.location_name == "Home"
        assert "light" in config.components


class TestServiceCallResponse:
    """Tests for ServiceCallResponse model."""

    def test_successful_response(self):
        """Test successful service call response."""
        response = ServiceCallResponse(
            success=True,
            changed_states=[
                EntityState(entity_id="light.test", state="on"),
            ],
        )
        assert response.success is True
        assert len(response.changed_states) == 1

    def test_empty_response(self):
        """Test response with no changed states."""
        response = ServiceCallResponse(success=True)
        assert response.success is True
        assert response.changed_states == []


class TestHistoryEntry:
    """Tests for HistoryEntry model."""

    def test_history_entry(self):
        """Test HistoryEntry model."""
        entry = HistoryEntry(
            entity_id="sensor.temperature",
            state="22.5",
            attributes={"unit_of_measurement": "°C"},
            last_changed=datetime(2024, 1, 15, 10, 0, 0),
        )
        assert entry.entity_id == "sensor.temperature"
        assert entry.state == "22.5"
