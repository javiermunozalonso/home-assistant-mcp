"""Pydantic models for Home Assistant API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EntityState(BaseModel):
    """Represents the state of a Home Assistant entity."""

    entity_id: str = Field(..., description="Unique identifier for the entity")
    state: str = Field(..., description="Current state value")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Entity attributes")
    last_changed: datetime | None = Field(None, description="When state last changed")
    last_updated: datetime | None = Field(None, description="When state was last updated")
    last_reported: datetime | None = Field(None, description="When state was last reported")
    context: dict[str, Any] | None = Field(None, description="Context information")


class ServiceField(BaseModel):
    """Represents a field in a service definition."""

    name: str | None = Field(None, description="Field name")
    description: str | None = Field(None, description="Field description")
    required: bool = Field(default=False, description="Whether field is required")
    example: Any = Field(None, description="Example value")
    selector: dict[str, Any] | None = Field(None, description="Field selector type")


class Service(BaseModel):
    """Represents a Home Assistant service."""

    name: str | None = Field(None, description="Service name")
    description: str | None = Field(None, description="Service description")
    fields: dict[str, ServiceField] = Field(default_factory=dict, description="Service fields")
    target: dict[str, Any] | None = Field(None, description="Target specification")


class ServiceDomain(BaseModel):
    """Represents a domain with its services."""

    domain: str = Field(..., description="Domain name (e.g., 'light', 'switch')")
    services: dict[str, Service] = Field(default_factory=dict, description="Available services")


class ApiStatus(BaseModel):
    """Represents Home Assistant API status."""

    message: str = Field(..., description="Status message")


class ConfigEntry(BaseModel):
    """Represents Home Assistant configuration."""

    components: list[str] = Field(default_factory=list, description="Loaded components")
    config_dir: str | None = Field(None, description="Configuration directory")
    elevation: int | None = Field(None, description="Elevation in meters")
    latitude: float | None = Field(None, description="Latitude")
    longitude: float | None = Field(None, description="Longitude")
    location_name: str | None = Field(None, description="Location name")
    time_zone: str | None = Field(None, description="Time zone")
    unit_system: dict[str, str] | None = Field(None, description="Unit system")
    version: str | None = Field(None, description="Home Assistant version")


class ServiceCallResponse(BaseModel):
    """Response from a service call."""

    success: bool = Field(..., description="Whether the call was successful")
    changed_states: list[EntityState] = Field(
        default_factory=list, description="States that changed"
    )


class HistoryEntry(BaseModel):
    """Represents a history entry for an entity."""

    entity_id: str = Field(..., description="Entity ID")
    state: str = Field(..., description="State value")
    attributes: dict[str, Any] = Field(default_factory=dict, description="Attributes")
    last_changed: datetime | None = Field(None, description="When state changed")
    last_updated: datetime | None = Field(None, description="When state was updated")


class Dashboard(BaseModel):
    """Represents a Lovelace dashboard."""

    id: str = Field(..., description="Dashboard ID")
    url_path: str = Field(..., description="URL path for the dashboard")
    title: str = Field(..., description="Dashboard title")
    icon: str | None = Field(None, description="Dashboard icon (e.g., 'mdi:home')")
    show_in_sidebar: bool = Field(default=True, description="Show in sidebar")
    require_admin: bool = Field(default=False, description="Require admin access")
    mode: str | None = Field(None, description="Dashboard mode (storage or yaml)")


class DashboardConfig(BaseModel):
    """Represents the configuration of a Lovelace dashboard."""

    views: list[dict[str, Any]] = Field(default_factory=list, description="Dashboard views")
    title: str | None = Field(None, description="Dashboard title")
    strategy: dict[str, Any] | None = Field(None, description="Dashboard strategy")


class DashboardList(BaseModel):
    """Represents a list of dashboards."""

    dashboards: list[Dashboard] = Field(default_factory=list, description="List of dashboards")
