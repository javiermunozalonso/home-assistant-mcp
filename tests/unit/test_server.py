import pytest
from unittest.mock import AsyncMock, patch

from home_assistant_mcp.server import get_client, list_tools, call_tool
from home_assistant_mcp.client import HomeAssistantClient, HomeAssistantError
from home_assistant_mcp.config import HomeAssistantConfig


class TestGetClient:
    """Tests for get_client function."""

    def test_get_client_creates_instance(self):
        """Test that get_client creates a client instance."""
        # Reset global state
        import home_assistant_mcp.server as server_module

        server_module._client = None
        server_module._config = None

        with patch("home_assistant_mcp.server.load_config") as mock_load_config:
            mock_config = HomeAssistantConfig(
                url="http://localhost:8123",
                token="test_token",
                verify_ssl=False,
                timeout=10.0,
            )
            mock_load_config.return_value = mock_config

            client = get_client()

            assert isinstance(client, HomeAssistantClient)
            mock_load_config.assert_called_once()

    def test_get_client_reuses_instance(self):
        """Test that get_client reuses existing instance."""
        import home_assistant_mcp.server as server_module

        # Create initial client
        mock_config = HomeAssistantConfig(
            url="http://localhost:8123",
            token="test_token",
            verify_ssl=False,
            timeout=10.0,
        )
        server_module._config = mock_config
        server_module._client = HomeAssistantClient(mock_config)
        first_client = server_module._client

        # Get client again
        second_client = get_client()

        # Should be the same instance
        assert second_client is first_client


class TestListTools:
    """Tests for list_tools handler."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Test that list_tools returns all available tools."""
        tools = await list_tools()

        # Verify it returns a list
        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check that essential tools are present
        tool_names = [tool.name for tool in tools]
        assert "ha_health_check" in tool_names
        assert "ha_list_entities" in tool_names
        assert "ha_get_entity_state" in tool_names
        assert "ha_call_service" in tool_names
        assert "ha_turn_on" in tool_names
        assert "ha_turn_off" in tool_names
        assert "ha_toggle" in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_includes_area_tools(self):
        """Test that list_tools includes area-related tools."""
        tools = await list_tools()
        tool_names = [tool.name for tool in tools]

        assert "ha_list_areas" in tool_names
        assert "ha_get_area_entities" in tool_names
        assert "ha_get_area_devices" in tool_names
        assert "ha_get_entity_area" in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_includes_dashboard_tools(self):
        """Test that list_tools includes dashboard-related tools."""
        tools = await list_tools()
        tool_names = [tool.name for tool in tools]

        assert "ha_list_dashboards" in tool_names
        assert "ha_get_dashboard" in tool_names
        assert "ha_create_dashboard" in tool_names
        assert "ha_update_dashboard" in tool_names
        assert "ha_delete_dashboard" in tool_names


class TestCallTool:
    """Tests for call_tool handler."""

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool."""
        result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert result[0].type == "text"
        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_handles_key_error(self):
        """Test that call_tool handles missing required arguments."""
        with patch("home_assistant_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            # Mock the tool to raise KeyError
            with patch("home_assistant_mcp.server.TOOLS_MAP") as mock_tools_map:
                async def raise_key_error(client, args):
                    raise KeyError("entity_id")

                mock_tools_map.__contains__.return_value = True
                mock_tools_map.__getitem__.return_value = raise_key_error

                result = await call_tool("test_tool", {})

                assert len(result) == 1
                assert "Missing required argument" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_handles_type_error(self):
        """Test that call_tool handles invalid argument types."""
        with patch("home_assistant_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            with patch("home_assistant_mcp.server.TOOLS_MAP") as mock_tools_map:
                async def raise_type_error(client, args):
                    raise TypeError("Invalid type")

                mock_tools_map.__contains__.return_value = True
                mock_tools_map.__getitem__.return_value = raise_type_error

                result = await call_tool("test_tool", {})

                assert "Invalid argument type" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_handles_timeout(self):
        """Test that call_tool handles timeout exceptions."""
        import httpx

        with patch("home_assistant_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            with patch("home_assistant_mcp.server.TOOLS_MAP") as mock_tools_map:
                async def raise_timeout(client, args):
                    raise httpx.TimeoutException("Request timed out")

                mock_tools_map.__contains__.return_value = True
                mock_tools_map.__getitem__.return_value = raise_timeout

                result = await call_tool("test_tool", {})

                assert "Request timed out" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_handles_ha_error(self):
        """Test that call_tool handles Home Assistant errors."""
        with patch("home_assistant_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            with patch("home_assistant_mcp.server.TOOLS_MAP") as mock_tools_map:
                async def raise_ha_error(client, args):
                    raise HomeAssistantError("HA API error")

                mock_tools_map.__contains__.return_value = True
                mock_tools_map.__getitem__.return_value = raise_ha_error

                result = await call_tool("test_tool", {})

                assert "Home Assistant error" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_handles_generic_exception(self):
        """Test that call_tool handles unexpected exceptions."""
        with patch("home_assistant_mcp.server.get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            with patch("home_assistant_mcp.server.TOOLS_MAP") as mock_tools_map:
                async def raise_generic_error(client, args):
                    raise ValueError("Unexpected error")

                mock_tools_map.__contains__.return_value = True
                mock_tools_map.__getitem__.return_value = raise_generic_error

                result = await call_tool("test_tool", {})

                assert "Internal error" in result[0].text
