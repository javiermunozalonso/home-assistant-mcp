# Home Assistant MCP Server

A Model Context Protocol (MCP) server that provides tools to interact with Home Assistant through its REST API.

## Features

- **Health Check**: Verify Home Assistant API connectivity
- **Entity Management**: List and query entity states
- **Service Calls**: Execute any Home Assistant service
- **Device Control**: Turn on/off, toggle devices with convenience methods
- **History**: Retrieve historical state data
- **Events**: Fire custom events

## Requirements

- Python 3.12+
- Home Assistant instance with REST API enabled
- Long-lived access token from Home Assistant

## Installation

### Using uv (recommended)

```bash
# Clone the repository
cd ha_connection

# Install dependencies (creates virtual environment automatically)
uv sync

# Install with dev dependencies for testing
uv sync --group dev
```

### Manual installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Home Assistant details:
   ```env
   HA_URL=http://your-home-assistant:8123
   HA_TOKEN=your_long_lived_access_token
   HA_VERIFY_SSL=true
   HA_TIMEOUT=30
   ```

3. Generate a long-lived access token in Home Assistant:
   - Go to your Profile (click your name in the sidebar)
   - Scroll to "Long-Lived Access Tokens"
   - Click "Create Token"
   - Copy the token to your `.env` file

## Usage

### Running the MCP Server

```bash
# Using uv
uv run ha-mcp-server

# Or directly
uv run python -m ha_mcp_server.server
```

### Configuring with Claude Desktop

Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json` on Linux/Mac or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "home-assistant": {
      "command": "uv",
      "args": ["--directory", "/path/to/ha_connection", "run", "ha-mcp-server"],
      "env": {
        "HA_URL": "http://your-home-assistant:8123",
        "HA_TOKEN": "your_long_lived_access_token"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `ha_health_check` | Check if Home Assistant API is accessible |
| `ha_get_config` | Get Home Assistant configuration |
| `ha_list_entities` | List all entities (optionally filter by domain) |
| `ha_get_entity_state` | Get state of a specific entity |
| `ha_list_services` | List available services |
| `ha_call_service` | Call any Home Assistant service |
| `ha_turn_on` | Turn on an entity with optional parameters |
| `ha_turn_off` | Turn off an entity |
| `ha_toggle` | Toggle an entity's state |
| `ha_get_history` | Get historical state changes |
| `ha_fire_event` | Fire a custom event |

## Examples

Once configured with Claude, you can ask:

- "Check if my Home Assistant is online"
- "List all my lights"
- "Turn on the living room light at 50% brightness"
- "What's the temperature in the bedroom?"
- "Toggle the kitchen switch"
- "Show me the history of the front door sensor"

## Testing

### Run all tests

```bash
uv run pytest
```

### Run with coverage

```bash
uv run pytest --cov=src/ha_mcp_server --cov-report=html
```

### Run only unit tests

```bash
uv run pytest tests/unit
```

### Run only integration tests

```bash
uv run pytest tests/integration
```

## Project Structure

```
ha_connection/
├── src/
│   └── ha_mcp_server/
│       ├── __init__.py
│       ├── client.py      # Home Assistant REST API client
│       ├── config.py      # Configuration management
│       ├── models.py      # Pydantic data models
│       └── server.py      # MCP server implementation
├── tests/
│   ├── conftest.py        # Pytest fixtures
│   ├── unit/              # Unit tests
│   │   ├── test_client.py
│   │   ├── test_config.py
│   │   └── test_models.py
│   └── integration/       # Integration tests
│       └── test_server.py
├── .env.example           # Example environment configuration
├── pyproject.toml         # Project configuration
└── README.md
```

## Security Notes

- Never commit your `.env` file or expose your access token
- Use tokens with minimal required permissions
- Consider using HTTPS for remote Home Assistant instances
- The token grants full API access - treat it like a password

## License

MIT
