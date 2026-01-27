"""Unit tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from ha_mcp_server.config import HomeAssistantConfig, load_config


class TestHomeAssistantConfig:
    """Tests for HomeAssistantConfig model."""

    def test_valid_config(self):
        """Test creating a valid configuration."""
        config = HomeAssistantConfig(
            url="http://localhost:8123",
            token="test_token",
        )
        assert config.url == "http://localhost:8123"
        assert config.token == "test_token"
        assert config.verify_ssl is True
        assert config.timeout == 30.0

    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from URL."""
        config = HomeAssistantConfig(
            url="http://localhost:8123/",
            token="test_token",
        )
        assert config.url == "http://localhost:8123"

    def test_token_whitespace_stripped(self):
        """Test that token whitespace is stripped."""
        config = HomeAssistantConfig(
            url="http://localhost:8123",
            token="  test_token  ",
        )
        assert config.token == "test_token"

    def test_empty_token_raises_error(self):
        """Test that empty token raises validation error."""
        with pytest.raises(ValueError, match="Token cannot be empty"):
            HomeAssistantConfig(
                url="http://localhost:8123",
                token="   ",
            )

    def test_custom_timeout(self):
        """Test setting custom timeout."""
        config = HomeAssistantConfig(
            url="http://localhost:8123",
            token="test_token",
            timeout=60.0,
        )
        assert config.timeout == 60.0

    def test_ssl_verification_disabled(self):
        """Test disabling SSL verification."""
        config = HomeAssistantConfig(
            url="https://localhost:8123",
            token="test_token",
            verify_ssl=False,
        )
        assert config.verify_ssl is False


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_from_env(self):
        """Test loading configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "HA_URL": "http://192.168.1.100:8123",
                "HA_TOKEN": "my_secret_token",
            },
            clear=False,
        ):
            config = load_config()
            assert config.url == "http://192.168.1.100:8123"
            assert config.token == "my_secret_token"

    def test_load_config_with_optional_env(self):
        """Test loading configuration with optional environment variables."""
        with patch.dict(
            os.environ,
            {
                "HA_URL": "http://192.168.1.100:8123",
                "HA_TOKEN": "my_secret_token",
                "HA_VERIFY_SSL": "false",
                "HA_TIMEOUT": "60",
            },
            clear=False,
        ):
            config = load_config()
            assert config.verify_ssl is False
            assert config.timeout == 60.0

    def test_load_config_missing_url(self, tmp_path):
        """Test that missing URL raises error."""
        # Use a non-existent env file to prevent loading from .env
        fake_env = tmp_path / ".env.nonexistent"
        with patch.dict(
            os.environ,
            {"HA_TOKEN": "my_secret_token"},
            clear=True,
        ):
            with pytest.raises(ValueError, match="HA_URL environment variable is required"):
                load_config(env_file=fake_env)

    def test_load_config_missing_token(self, tmp_path):
        """Test that missing token raises error."""
        # Use a non-existent env file to prevent loading from .env
        fake_env = tmp_path / ".env.nonexistent"
        with patch.dict(
            os.environ,
            {"HA_URL": "http://localhost:8123"},
            clear=True,
        ):
            with pytest.raises(ValueError, match="HA_TOKEN environment variable is required"):
                load_config(env_file=fake_env)
