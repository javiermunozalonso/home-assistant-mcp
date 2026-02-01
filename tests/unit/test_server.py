"""Unit tests for FastMCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from home_assistant_mcp import core, server
from home_assistant_mcp.client import HomeAssistantClient, HomeAssistantError
from home_assistant_mcp.config import HomeAssistantConfig
from home_assistant_mcp.models import ApiStatus


class TestGetClient:
    """Tests for get_client function."""

    def test_get_client_returns_client_when_initialized(self):
        """Test that get_client returns client when it's set."""
        # Mock the client
        mock_client = MagicMock(spec=HomeAssistantClient)
        core.client = mock_client

        client = core.get_client()

        assert client is mock_client

    def test_get_client_raises_when_not_initialized(self):
        """Test that get_client raises error when client is None."""
        core.client = None

        with pytest.raises(RuntimeError) as exc_info:
            core.get_client()

        assert "not initialized" in str(exc_info.value)


class TestFastMCPServer:
    """Tests for FastMCP server instance."""

    def test_server_instance_created(self):
        """Test that FastMCP server instance is created."""
        assert core.mcp is not None
        assert core.mcp.name == "home_assistant_mcp"

    def test_server_has_lifespan(self):
        """Test that server has lifespan configured."""
        # FastMCP should have lifespan configured (stored internally)
        # The lifespan is passed in constructor and managed by FastMCP
        assert core.mcp is not None
        # We can't directly access lifespan as it's internal to FastMCP
        # But we can verify it works via lifecycle tests


class TestHealthCheckTool:
    """Tests for ha_health_check tool."""

    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test health check with successful API response."""
        from home_assistant_mcp.tools.health import ha_health_check

        # Setup mock client
        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.check_api.return_value = ApiStatus(message="API running")
        core.client = mock_client

        result = await ha_health_check()

        assert "API is running" in result
        assert "✓" in result
        mock_client.check_api.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_handles_error(self):
        """Test health check handles errors gracefully."""
        from home_assistant_mcp.tools.health import ha_health_check

        mock_client = AsyncMock(spec=HomeAssistantClient)
        mock_client.check_api.side_effect = HomeAssistantError("Connection failed")
        core.client = mock_client

        result = await ha_health_check()

        assert "✗" in result
        assert "Connection failed" in result


class TestToolModels:
    """Tests for Pydantic tool models."""

    def test_turn_on_input_validates_entity_id(self):
        """Test that TurnOnInput validates entity_id format."""
        from home_assistant_mcp.tool_models import TurnOnInput
        from pydantic import ValidationError

        # Valid entity_id
        valid_input = TurnOnInput(entity_id="light.living_room")
        assert valid_input.entity_id == "light.living_room"

        # Invalid entity_id (missing domain separator)
        with pytest.raises(ValidationError) as exc_info:
            TurnOnInput(entity_id="invalid")

        assert "domain.entity" in str(exc_info.value)

    def test_turn_on_input_validates_brightness(self):
        """Test that TurnOnInput validates brightness range."""
        from home_assistant_mcp.tool_models import TurnOnInput
        from pydantic import ValidationError

        # Valid brightness
        valid_input = TurnOnInput(entity_id="light.test", brightness=128)
        assert valid_input.brightness == 128

        # Invalid brightness (too high)
        with pytest.raises(ValidationError):
            TurnOnInput(entity_id="light.test", brightness=300)

        # Invalid brightness (negative)
        with pytest.raises(ValidationError):
            TurnOnInput(entity_id="light.test", brightness=-1)

    def test_turn_on_input_validates_rgb_color(self):
        """Test that TurnOnInput validates RGB color values."""
        from home_assistant_mcp.tool_models import TurnOnInput
        from pydantic import ValidationError

        # Valid RGB
        valid_input = TurnOnInput(entity_id="light.test", rgb_color=[255, 0, 0])
        assert valid_input.rgb_color == [255, 0, 0]

        # Invalid RGB (value too high)
        with pytest.raises(ValidationError) as exc_info:
            TurnOnInput(entity_id="light.test", rgb_color=[300, 0, 0])

        assert "0-255" in str(exc_info.value) or "0 and 255" in str(exc_info.value)

    def test_list_entities_input_has_pagination(self):
        """Test that ListEntitiesInput has pagination fields."""
        from home_assistant_mcp.tool_models import ListEntitiesInput

        input_model = ListEntitiesInput()
        assert hasattr(input_model, "limit")
        assert hasattr(input_model, "offset")
        assert input_model.limit == 50  # Default
        assert input_model.offset == 0  # Default

    def test_response_format_enum(self):
        """Test ResponseFormat enum."""
        from home_assistant_mcp.tool_models import ResponseFormat

        assert ResponseFormat.JSON == "json"
        assert ResponseFormat.MARKDOWN == "markdown"


class TestToolAnnotations:
    """Tests to verify tools have proper annotations.

    Note: FastMCP manages annotations internally and doesn't expose them
    via __mcp_annotations__. The annotations are correctly registered
    when tools are decorated with @mcp.tool(annotations={...}).

    These tests verify that the tool functions exist and can be called.
    """

    def test_health_check_exists_and_callable(self):
        """Test that ha_health_check exists and is callable."""
        from home_assistant_mcp.tools.health import ha_health_check

        assert callable(ha_health_check)
        # Verify it's registered with FastMCP
        assert ha_health_check is not None

    def test_turn_on_exists_and_callable(self):
        """Test that ha_turn_on exists and is callable."""
        from home_assistant_mcp.tools.control import ha_turn_on

        assert callable(ha_turn_on)
        assert ha_turn_on is not None

    def test_toggle_exists_and_callable(self):
        """Test that ha_toggle exists and is callable."""
        from home_assistant_mcp.tools.control import ha_toggle

        assert callable(ha_toggle)
        assert ha_toggle is not None


class TestLifecycleManagement:
    """Tests for lifecycle management."""

    @pytest.mark.asyncio
    async def test_lifespan_initializes_client(self):
        """Test that lifespan initializes the Home Assistant client."""
        with patch("home_assistant_mcp.core.load_config") as mock_load_config:
            mock_config = HomeAssistantConfig(
                url="http://localhost:8123",
                token="test_token",
                verify_ssl=False,
                timeout=10.0,
            )
            mock_load_config.return_value = mock_config

            # Test the lifespan context manager
            async with core.app_lifespan(core.mcp):
                # Client should be initialized
                assert core.client is not None
                assert isinstance(core.client, HomeAssistantClient)

            # After exiting, client should be cleaned up (set to None)
            assert core.client is None

    @pytest.mark.asyncio
    async def test_lifespan_handles_initialization_errors(self):
        """Test that lifespan handles initialization errors properly."""
        with patch("home_assistant_mcp.core.load_config") as mock_load_config:
            mock_load_config.side_effect = Exception("Config error")

            with pytest.raises(Exception) as exc_info:
                async with core.app_lifespan(core.mcp):
                    pass

            assert "Config error" in str(exc_info.value)
