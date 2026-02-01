"""Pydantic models for tool input validation."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResponseFormat(str, Enum):
    """Output format for tool responses."""

    MARKDOWN = "markdown"
    JSON = "json"


# Base configuration for all models
class ToolInputBase(BaseModel):
    """Base configuration for all tool input models."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )


# ==================== Health & Config Tools ====================


class HealthCheckInput(ToolInputBase):
    """Input for health check (no parameters needed)."""

    pass


class GetConfigInput(ToolInputBase):
    """Input for getting configuration (no parameters needed)."""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


# ==================== Entity Tools ====================


class ListEntitiesInput(ToolInputBase):
    """Input for listing entities."""

    domain: Optional[str] = Field(
        default=None,
        description="Optional domain to filter entities (e.g., 'light', 'switch', 'sensor', 'climate')",
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum number of entities to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of entities to skip for pagination",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class GetEntityStateInput(ToolInputBase):
    """Input for getting entity state."""

    entity_id: str = Field(
        ...,
        description="Entity ID (e.g., 'light.living_room', 'switch.kitchen')",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        """Validate entity_id format."""
        if "." not in v:
            raise ValueError(
                "entity_id must be in format 'domain.entity' (e.g., 'light.living_room'). "
                "Use ha_list_entities to see available entities."
            )
        return v


# ==================== Service Tools ====================


class ListServicesInput(ToolInputBase):
    """Input for listing services."""

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of services to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of services to skip for pagination",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class CallServiceInput(ToolInputBase):
    """Input for calling a service."""

    domain: str = Field(
        ...,
        description="Service domain (e.g., 'light', 'switch', 'climate')",
    )
    service: str = Field(
        ...,
        description="Service name (e.g., 'turn_on', 'turn_off', 'toggle')",
    )
    entity_id: Optional[str] = Field(
        default=None,
        description="Target entity ID or comma-separated list of IDs",
    )
    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional service data (e.g., brightness, color_temp)",
    )


# ==================== Control Tools ====================


class TurnOnInput(ToolInputBase):
    """Input for turning on an entity."""

    entity_id: str = Field(
        ...,
        description="Entity ID to turn on (e.g., 'light.living_room')",
    )
    brightness: Optional[int] = Field(
        default=None,
        ge=0,
        le=255,
        description="Brightness level 0-255 (for lights)",
    )
    brightness_pct: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Brightness percentage 0-100 (for lights)",
    )
    color_temp: Optional[int] = Field(
        default=None,
        gt=0,
        description="Color temperature in mireds (for lights)",
    )
    rgb_color: Optional[list[int]] = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="RGB color as [r, g, b] array (for lights)",
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        """Validate entity_id format."""
        if "." not in v:
            raise ValueError(
                "entity_id must be in format 'domain.entity' (e.g., 'light.living_room'). "
                "Use ha_list_entities to see available entities."
            )
        return v

    @field_validator("rgb_color")
    @classmethod
    def validate_rgb(cls, v: Optional[list[int]]) -> Optional[list[int]]:
        """Validate RGB color values."""
        if v is not None:
            if not all(0 <= c <= 255 for c in v):
                raise ValueError(
                    "rgb_color values must be between 0 and 255. "
                    "Example: [255, 0, 0] for red"
                )
        return v


class TurnOffInput(ToolInputBase):
    """Input for turning off an entity."""

    entity_id: str = Field(
        ...,
        description="Entity ID to turn off (e.g., 'light.living_room')",
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        """Validate entity_id format."""
        if "." not in v:
            raise ValueError(
                "entity_id must be in format 'domain.entity' (e.g., 'light.living_room'). "
                "Use ha_list_entities to see available entities."
            )
        return v


class ToggleInput(ToolInputBase):
    """Input for toggling an entity."""

    entity_id: str = Field(
        ...,
        description="Entity ID to toggle (e.g., 'light.living_room')",
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        """Validate entity_id format."""
        if "." not in v:
            raise ValueError(
                "entity_id must be in format 'domain.entity' (e.g., 'light.living_room'). "
                "Use ha_list_entities to see available entities."
            )
        return v


# ==================== History Tools ====================


class GetHistoryInput(ToolInputBase):
    """Input for getting entity history."""

    entity_id: Optional[str] = Field(
        default=None,
        description="Optional entity ID to filter history",
    )
    start_time: Optional[datetime] = Field(
        default=None,
        description="Start of history period (ISO format)",
    )
    end_time: Optional[datetime] = Field(
        default=None,
        description="End of history period (ISO format)",
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of history entries to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of entries to skip for pagination",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate entity_id format if provided."""
        if v is not None and "." not in v:
            raise ValueError(
                "entity_id must be in format 'domain.entity' (e.g., 'sensor.temperature')"
            )
        return v


# ==================== Event Tools ====================


class FireEventInput(ToolInputBase):
    """Input for firing an event."""

    event_type: str = Field(
        ...,
        min_length=1,
        description="Type of event to fire",
    )
    event_data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional event data",
    )


# ==================== Area Tools ====================


class ListAreasInput(ToolInputBase):
    """Input for listing areas."""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class GetAreaEntitiesInput(ToolInputBase):
    """Input for getting entities in an area."""

    area: str = Field(
        ...,
        description="Area ID or name",
    )
    domain: Optional[str] = Field(
        default=None,
        description="Optional domain filter (e.g., 'light', 'switch')",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class GetAreaDevicesInput(ToolInputBase):
    """Input for getting devices in an area."""

    area: str = Field(
        ...,
        description="Area ID or name",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class GetEntityAreaInput(ToolInputBase):
    """Input for getting the area of an entity."""

    entity_id: str = Field(
        ...,
        description="Entity ID",
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, v: str) -> str:
        """Validate entity_id format."""
        if "." not in v:
            raise ValueError(
                "entity_id must be in format 'domain.entity' (e.g., 'light.living_room')"
            )
        return v


# ==================== Template Tools ====================


class RenderTemplateInput(ToolInputBase):
    """Input for rendering a Jinja2 template."""

    template: str = Field(
        ...,
        min_length=1,
        description="Jinja2 template to render",
    )


# ==================== Dashboard Tools ====================


class ListDashboardsInput(ToolInputBase):
    """Input for listing dashboards."""

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class GetDashboardInput(ToolInputBase):
    """Input for getting a dashboard configuration."""

    url_path: Optional[str] = Field(
        default=None,
        description="Dashboard URL path (None for default dashboard)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class CreateDashboardInput(ToolInputBase):
    """Input for creating a new dashboard."""

    url_path: str = Field(
        ...,
        pattern=r"^[a-z0-9-]+$",
        description="URL path for the dashboard (lowercase alphanumeric and hyphens)",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Dashboard title",
    )
    icon: Optional[str] = Field(
        default=None,
        pattern=r"^mdi:[a-z0-9-]+$",
        description="Dashboard icon (e.g., 'mdi:home')",
    )
    show_in_sidebar: bool = Field(
        default=True,
        description="Show in sidebar",
    )
    require_admin: bool = Field(
        default=False,
        description="Require admin access",
    )


class UpdateDashboardInput(ToolInputBase):
    """Input for updating a dashboard."""

    dashboard_id: str = Field(
        ...,
        min_length=1,
        description="Dashboard ID to update",
    )
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        description="New title",
    )
    icon: Optional[str] = Field(
        default=None,
        pattern=r"^mdi:[a-z0-9-]+$",
        description="New icon (e.g., 'mdi:home')",
    )
    show_in_sidebar: Optional[bool] = Field(
        default=None,
        description="Show in sidebar",
    )
    require_admin: Optional[bool] = Field(
        default=None,
        description="Require admin access",
    )


class DeleteDashboardInput(ToolInputBase):
    """Input for deleting a dashboard."""

    dashboard_id: str = Field(
        ...,
        min_length=1,
        description="Dashboard ID to delete",
    )
