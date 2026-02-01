"""Core infrastructure for Home Assistant MCP server.

This module contains the core components that are shared across the server:
- FastMCP server instance
- Home Assistant client lifecycle management
- Client accessor function

Separating these into a core module prevents circular import issues between
server.py and the tools/ package.
"""

import logging
import sys
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from .client import HomeAssistantClient
from .config import load_config

# Configure logging to stderr (stdio transport uses stdout for MCP protocol)
logger = logging.getLogger("home_assistant_mcp")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(handler)

# Global client instance (initialized in lifespan)
client: HomeAssistantClient | None = None


@asynccontextmanager
async def app_lifespan(mcp_server):
    """Manage Home Assistant client lifecycle.

    Args:
        mcp_server: The FastMCP server instance

    Yields:
        dict: Empty context (client is stored in global variable)
    """
    global client
    logger.info("Initializing Home Assistant MCP server...")

    try:
        config = load_config()
        client = HomeAssistantClient(config)
        logger.info(f"Connected to Home Assistant at {config.url}")

        # Yield to keep server running
        yield {}

    except Exception as e:
        logger.error(f"Failed to initialize Home Assistant client: {e}")
        raise
    finally:
        # Cleanup on shutdown
        if client:
            logger.info("Closing Home Assistant client...")
            try:
                await client.close()
                logger.info("Client closed successfully")
            except Exception as e:
                logger.error(f"Error closing client: {e}")
            finally:
                client = None


# Create FastMCP server instance with lifespan
mcp = FastMCP("home_assistant_mcp", lifespan=app_lifespan)


def get_client() -> HomeAssistantClient:
    """Get the Home Assistant client instance.

    Returns:
        HomeAssistantClient: The initialized client

    Raises:
        RuntimeError: If client is not initialized
    """
    if client is None:
        raise RuntimeError(
            "Home Assistant client not initialized. "
            "Server may not have started properly."
        )
    return client
