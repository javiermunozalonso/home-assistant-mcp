"""MCP Server for Home Assistant integration."""

from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import HomeAssistantClient, HomeAssistantError
from .config import HomeAssistantConfig, load_config
from .tools import TOOLS_LIST, TOOLS_MAP

# Create the MCP server instance
server = Server("home-assistant-mcp")

# Global client instance (initialized when server starts)
_client: HomeAssistantClient | None = None
_config: HomeAssistantConfig | None = None


def get_client() -> HomeAssistantClient:
    """Get the Home Assistant client instance."""
    global _client, _config
    if _client is None:
        if _config is None:
            _config = load_config()
        _client = HomeAssistantClient(_config)
    return _client


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for Home Assistant control."""
    return TOOLS_LIST


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls for Home Assistant operations."""
    client = get_client()

    if name not in TOOLS_MAP:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    try:
        return await TOOLS_MAP[name](client, arguments)
    except HomeAssistantError as e:
        return [TextContent(type="text", text=f"Home Assistant error: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def run_server() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Main entry point."""
    import asyncio

    asyncio.run(run_server())


if __name__ == "__main__":
    main()
