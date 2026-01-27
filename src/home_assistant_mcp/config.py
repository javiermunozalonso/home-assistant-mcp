"""Configuration management for Home Assistant MCP Server."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


class HomeAssistantConfig(BaseModel):
    """Configuration for Home Assistant connection."""

    url: str = Field(..., description="Home Assistant URL (e.g., http://192.168.1.100:8123)")
    token: str = Field(..., description="Long-lived access token")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Ensure URL doesn't have trailing slash."""
        return v.rstrip("/")

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Ensure token is not empty."""
        if not v or not v.strip():
            raise ValueError("Token cannot be empty")
        return v.strip()


def load_config(env_file: Path | None = None) -> HomeAssistantConfig:
    """Load configuration from environment variables.

    Args:
        env_file: Optional path to .env file

    Returns:
        HomeAssistantConfig instance

    Raises:
        ValueError: If required environment variables are missing
    """
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    url = os.getenv("HA_URL")
    token = os.getenv("HA_TOKEN")

    if not url:
        raise ValueError("HA_URL environment variable is required")
    if not token:
        raise ValueError("HA_TOKEN environment variable is required")

    return HomeAssistantConfig(
        url=url,
        token=token,
        verify_ssl=os.getenv("HA_VERIFY_SSL", "true").lower() == "true",
        timeout=float(os.getenv("HA_TIMEOUT", "30.0")),
    )
