# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides tools to interact with Home Assistant through its REST API. It allows AI assistants to control smart home devices, query states, and call services.

## Available Skills

### mcp-builder

**Location**: `.claude/skills/mcp-builder`

This project includes the official Anthropic mcp-builder skill, which provides comprehensive guidance for developing MCP servers.

**Key References:**

- `reference/python_mcp_server.md` - Complete guide for Python MCP server development (⭐ most relevant for this project)
- `reference/mcp_best_practices.md` - Best practices for MCP server design
- `reference/evaluation.md` - Evaluation methodologies for MCP implementations
- `reference/node_mcp_server.md` - Node.js/TypeScript MCP guide

**Utility Scripts:**

- `scripts/evaluation.py` - Script to evaluate MCP server implementation quality
- `scripts/connections.py` - Utilities for managing MCP connections

**Installation & Updates:**

To install or update the skill:

```bash
./install-mcp-builder-skill.sh
```

To update with latest changes from Anthropic:

```bash
./install-mcp-builder-skill.sh --update
```

To install Python dependencies for evaluation scripts:

```bash
./install-mcp-builder-skill.sh --install-deps
```

**Usage:**

The skill is automatically available to Claude Code. You can reference it when working on MCP server improvements, or explicitly invoke evaluation scripts:

```bash
python .claude/skills/mcp-builder/scripts/evaluation.py
```

---

## Development Guidelines

When working with code in this repository, you MUST follow these principles:

### Architecture and Design Principles

1. **SOLID Principles**: Apply Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion.

2. **DDD and TDD**: Follow Domain-Driven Design and Test-Driven Development approaches.

3. **Clean Code**: Write clean, readable, and maintainable code.

4. **DRY (Don't Repeat Yourself)**: Avoid code duplication.

5. **KISS (Keep It Simple)**: Keep solutions simple and straightforward.

6. **YAGNI (You Ain't Gonna Need It)**: Don't add functionality until it's needed.

7. **Modularization**: Seek code modularization into reusable components.

### Code Organization

- **One class per file**: Classes must have individual files in `snake_case` format.
- **No multiple classes** in the same file.

### Documentation Standards

- **Google Style docstrings**: All functions and classes must have documentation following Google Style standards.
- When creating a function, generate associated documentation.
- When creating a class, document the class and each method.

### Testing Requirements

- **Tests are mandatory**: Always generate tests associated with developed functionalities.
- **Use pytest**: Always use `pytest` for test execution.
- **Mirror structure**: Tests must respect the original functionality structure, distributed across files following the project organization (see Testing Guidelines below).

### Dependency Management

- **Use uv for execution**: Always use `uv` to run commands.
- **Production dependencies**: Use `uv add <package>` for production dependencies.
- **Development dependencies**: Use `uv add --dev <package>` for development dependencies (testing, linting, etc.).

### Repository Practices

- **Update README**: Always update README.md when adding new functionalities.
- **Commit regularly**: Generate a git commit when completing a significant task.
- **Sync artifacts**: When creating internal artifacts (tasks, implementation plans), use the sync-artifacts workflow to maintain a history in the `planning/` folder.

---

## Commands

### Development Setup

```bash
uv sync              # Install dependencies
uv sync --group dev  # Install with dev dependencies
```

### Running the Server

```bash
uv run home-assistant-mcp                    # Run MCP server
uv run python -m home_assistant_mcp.server   # Alternative
```

### Testing

```bash
uv run pytest                           # Run all tests
uv run pytest tests/unit                # Run unit tests only
uv run pytest tests/integration         # Run integration tests only
uv run pytest tests/unit/test_client.py # Run single test file
uv run pytest -k "test_name"            # Run tests matching pattern
uv run pytest --cov=src/home_assistant_mcp --cov-report=html  # With coverage
```

---

## Testing Guidelines

### Directory Structure (Mandatory)

The project follows a **hybrid structure** that separates by test type and mirrors the `src/` structure:

```
src/
  home_assistant_mcp/
    client.py
    server.py
    config.py
    models.py

tests/
  unit/              # Mirrors src/ structure
    test_client.py
    test_server.py
    test_config.py
    test_models.py
  integration/       # Can mirror or group by functionality
    test_server.py
  e2e/              # Complete business flows
  data/             # Static test data
  conftest.py       # Global fixtures
```

### Naming Conventions

1. **Test files**: Use the `test_*.py` pattern.
2. **Test functions**: Prefix with `test_*`.
3. **Direct relationship**: `src/home_assistant_mcp/client.py` → `tests/unit/test_client.py`.

### Test Classification

#### Unit Tests (`tests/unit/`)

- Test a **small logical unit** (function, method, class).
- **No access to external services**: No real HTTP calls, databases, or queues.
- All external dependencies are **mocked/stubbed**.
- Examples: validation logic, pure calculations, services with mocked repositories.

#### Integration Tests (`tests/integration/`)

- Test **interaction between multiple components**.
- Use real or semi-real resources:
  - Test databases (local or containerized)
  - Test message queues
  - Simulated HTTP services (docker, testcontainers)
- Slower than unit tests but **reasonably fast**.

#### End-to-End Tests (`tests/e2e/`)

- Cover **complete business flows**.
- Traverse nearly the entire stack: API / UI / DB / queues.
- Require heavier environment (docker-compose, loaded data).

### Isolation and Dependencies

**Unit tests**:

- Cannot depend on execution order.
- Cannot depend on shared state.
- Should not perform real I/O.

**Integration and e2e tests**:

- Must leave environment clean (clean DB, reset queues, delete temp files).
- Controlled I/O is allowed.

### Pytest and Markers

1. **Framework**: Use `pytest`.

2. **Required markers**: Mark integration and e2e tests:

```python
import pytest

@pytest.mark.integration
def test_auth_flow_with_db():
    ...

@pytest.mark.e2e
def test_full_checkout_flow():
    ...
```

1. **Configuration**: Declare markers in `pytest.ini` or `pyproject.toml`:

```ini
[pytest]
markers =
    integration: integration tests (require external resources)
    e2e: end-to-end tests (complete flows and heavy environments)
```

1. **Execution commands**:

```bash
# All unit tests
pytest tests/unit

# Integration tests
pytest tests/integration -m integration

# E2E tests
pytest tests/e2e -m e2e

# Full suite
pytest tests
```

### Fixtures and Utilities

1. **Global fixtures**: Define in `tests/conftest.py`.
2. **Specific fixtures**: In `tests/<type>/conftest.py`.
3. **Static data**: In `tests/data/` or `tests/<type>/data/`.

### CI/CD Requirements

1. **Mandatory on every push/PR**: Execute `tests/unit/`.
2. **Integration tests**: On PRs to main branches or nightly pipelines.
3. **E2E tests**: On merges to `main` or nightly pipelines.

```bash
# Fast suite (CI on every push)
pytest tests/unit

# Full backend suite (PR to main)
pytest tests/unit tests/integration -m "not e2e"

# Complete suite (nightly)
pytest tests -m "integration or e2e"
```

### Contribution Requirements

1. **All new code** in `src/` must come with tests in the appropriate folder:
   - Pure logic → `tests/unit/`
   - Integration with DB/services → `tests/integration/`
   - Complete business flows → `tests/e2e/`

2. **Module movements**: If a module moves in `src/`, move its tests maintaining correspondence.

3. **Rejected PRs**:
   - Unit tests outside `tests/unit/`
   - Integration logic in tests under `tests/unit/`

---

## Architecture

### Core Components

- **server.py** - MCP server implementation using `mcp.server.Server`. Defines tools via `@server.list_tools()` decorator and handles tool calls via `@server.call_tool()`. Uses a global `HomeAssistantClient` instance initialized lazily.

- **client.py** - Async HTTP client using `httpx.AsyncClient` to communicate with Home Assistant REST API. All API calls go through `_request()` method. Supports context manager protocol for proper cleanup. Uses Jinja2 templates via `/api/template` endpoint for area queries.

- **config.py** - Pydantic-based configuration loaded from environment variables (`HA_URL`, `HA_TOKEN`, `HA_VERIFY_SSL`, `HA_TIMEOUT`). Uses `python-dotenv` for `.env` file support.

- **models.py** - Pydantic models for API responses: `EntityState`, `ServiceDomain`, `ConfigEntry`, `ServiceCallResponse`, `HistoryEntry`.

### Key Patterns

- The server uses stdio transport (`stdio_server`) for MCP communication
- Entity operations (turn_on, turn_off, toggle) infer the domain from entity_id (e.g., `light.living_room` → domain `light`)
- Area-related queries use Home Assistant's template rendering API with Jinja2 functions (`areas()`, `area_entities()`, `area_devices()`)
- Tests use `pytest-httpx` for mocking HTTP responses and `pytest-asyncio` with `asyncio_mode = "auto"`

## Workflows

Workflows are guided procedures for specific tasks.

### 1. Run Tests

**Description**: Execute project tests using pytest and uv.

**Standard command**:

```bash
uv run pytest
```

**Use cases**:

- Verify code works correctly.
- Before commits or PRs.
- During development to validate changes.

### 2. Manage Dependencies

**Description**: Manage project dependencies correctly using uv.

**Steps**:

1. **Add production dependency**:

```bash
uv add <package_name>
```

Example:

```bash
uv add httpx
```

1. **Add development dependency**:

```bash
uv add --dev <package_name>
```

Example:

```bash
uv add --dev pytest
```

1. **Sync environment** after manual changes to `pyproject.toml`:

```bash
uv sync
```

1. **Update README.md** if necessary with information about the new dependency.

2. **Update documentation** in `docs/` (if using mkdocs) with information about the new component.

### 3. Create Component

**Description**: Create a new component following DDD and SOLID principles.

**Steps**:

1. **Identify the layer** the component belongs to:
   - Domain (entities, value objects)
   - Application (use cases, application services)
   - Infrastructure (repositories, external adapters)
   - UI (controllers, presentation)

2. **Create the file** for the class in `snake_case`:

```bash
touch src/<layer>/<component_name>.py
```

Example:

```bash
touch src/home_assistant_mcp/new_service.py
```

1. **Define the class** ensuring:
   - Single Responsibility Principle (SRP)
   - Documentation (Google-style docstrings) for class and methods
   - Strict type hints

2. **Create the corresponding test file**:

```bash
touch tests/unit/<layer>/test_<component_name>.py
```

Example:

```bash
touch tests/unit/test_new_service.py
```

1. **Implement tests** covering success and error cases.

2. **Run tests** to verify:

```bash
uv run pytest
```

1. **Update README.md** if necessary.

2. **Update documentation** in `docs/` (if using mkdocs).

### 4. Sync Artifacts

**Description**: Sync generated artifacts (tasks, plans) to the `planning/` folder to maintain history.

**Steps**:

1. **Ensure** the `planning` folder exists:

```bash
mkdir -p planning
```

1. **Copy artifacts** to a folder with timestamp:

```bash
UUID="<session-uuid>"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SOURCE_DIR="$HOME/.gemini/antigravity/brain/$UUID"
DEST_DIR="planning/$UUID/$TIMESTAMP"

mkdir -p "$DEST_DIR"
cp "$SOURCE_DIR"/*.md "$DEST_DIR/"
echo "Artifacts copied to $DEST_DIR"
```

**Note**: Replace `<session-uuid>` with the current session UUID.

---

## Configuration

Required environment variables:

- `HA_URL` - Home Assistant URL (e.g., `http://192.168.1.100:8123`)
- `HA_TOKEN` - Long-lived access token from Home Assistant

Optional:

- `HA_VERIFY_SSL` - SSL verification (default: `true`)
- `HA_TIMEOUT` - Request timeout in seconds (default: `30`)

---

## Contribution Checklist

Before making a commit or PR, ensure:

- [ ] Code follows SOLID, DDD, Clean Code principles
- [ ] Each class is in its own file in `snake_case`
- [ ] All functions/classes have Google-style documentation
- [ ] Unit tests created in `tests/unit/`
- [ ] Integration tests created if applicable
- [ ] Tests pass: `uv run pytest`
- [ ] README.md updated if necessary
- [ ] Documentation in `docs/` updated if applicable
- [ ] New dependencies added with `uv add` (or `uv add --dev`)

---

**Last updated**: 2026-01-27
