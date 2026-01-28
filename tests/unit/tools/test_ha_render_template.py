"""Unit tests for ha_render_template tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp.tools.ha_render_template import TOOL_DEF, execute


class TestRenderTemplateTool:
    """Tests for ha_render_template tool."""

    def test_tool_definition(self):
        """Test tool definition is correctly structured."""
        assert TOOL_DEF.name == "ha_render_template"
        assert "Render a Home Assistant Jinja2 template" in TOOL_DEF.description
        assert TOOL_DEF.inputSchema["type"] == "object"
        assert "template" in TOOL_DEF.inputSchema["required"]

    @pytest.mark.asyncio
    async def test_execute_simple_template(self):
        """Test rendering a simple template."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "22.5"

        # Execute tool
        result = await execute(
            mock_client, {"template": '{{ states("sensor.temperature") }}'}
        )

        # Verify
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Template result:" in result[0].text
        assert "22.5" in result[0].text
        mock_client.render_template.assert_called_once_with('{{ states("sensor.temperature") }}')

    @pytest.mark.asyncio
    async def test_execute_areas_template(self):
        """Test rendering template with areas function."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "['living_room', 'kitchen', 'bedroom']"

        result = await execute(mock_client, {"template": "{{ areas() | list }}"})

        assert "Template result:" in result[0].text
        assert "['living_room', 'kitchen', 'bedroom']" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_complex_template(self):
        """Test rendering complex template with multiple functions."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = (
            "Living room lights: light.living_room, light.lamp"
        )

        result = await execute(
            mock_client,
            {"template": "Living room lights: {{ area_entities('living_room') | join(', ') }}"},
        )

        assert "Living room lights: light.living_room, light.lamp" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_template_with_filters(self):
        """Test rendering template with Jinja2 filters."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "HELLO WORLD"

        result = await execute(
            mock_client, {"template": "{{ 'hello world' | upper }}"}
        )

        assert "HELLO WORLD" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_template_with_math(self):
        """Test rendering template with mathematical operations."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "42"

        result = await execute(mock_client, {"template": "{{ 40 + 2 }}"})

        assert "42" in result[0].text

    @pytest.mark.asyncio
    async def test_execute_empty_template_result(self):
        """Test rendering template that returns empty result."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = ""

        result = await execute(mock_client, {"template": "{{ none }}"})

        assert "Template result:" in result[0].text
