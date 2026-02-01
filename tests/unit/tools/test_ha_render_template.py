"""Unit tests for ha_render_template tool."""

import pytest
from unittest.mock import AsyncMock

from home_assistant_mcp import core
from home_assistant_mcp.tools.templates import ha_render_template
from home_assistant_mcp.tool_models import RenderTemplateInput


class TestRenderTemplateTool:
    """Tests for ha_render_template tool."""



    @pytest.mark.asyncio
    async def test_execute_simple_template(self):
        """Test rendering a simple template."""
        # Create mock client
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "22.5"
        core.client = mock_client

        # Execute tool
        result = await ha_render_template(
            RenderTemplateInput(template='{{ states("sensor.temperature") }}')
        )

        # Verify
        # Verify
        assert "Template result:" in result
        assert "22.5" in result
        mock_client.render_template.assert_called_once_with(template='{{ states("sensor.temperature") }}')

    @pytest.mark.asyncio
    async def test_execute_areas_template(self):
        """Test rendering template with areas function."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "['living_room', 'kitchen', 'bedroom']"
        core.client = mock_client

        result = await ha_render_template(RenderTemplateInput(template="{{ areas() | list }}"))

        assert "Template result:" in result
        assert "['living_room', 'kitchen', 'bedroom']" in result

    @pytest.mark.asyncio
    async def test_execute_complex_template(self):
        """Test rendering complex template with multiple functions."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = (
            "Living room lights: light.living_room, light.lamp"
        )
        core.client = mock_client

        result = await ha_render_template(
            RenderTemplateInput(
                template="Living room lights: {{ area_entities('living_room') | join(', ') }}"
            )
        )

        assert "Living room lights: light.living_room, light.lamp" in result

    @pytest.mark.asyncio
    async def test_execute_template_with_filters(self):
        """Test rendering template with Jinja2 filters."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "HELLO WORLD"
        core.client = mock_client

        result = await ha_render_template(
            RenderTemplateInput(template="{{ 'hello world' | upper }}")
        )

        assert "HELLO WORLD" in result

    @pytest.mark.asyncio
    async def test_execute_template_with_math(self):
        """Test rendering template with mathematical operations."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = "42"
        core.client = mock_client

        result = await ha_render_template(RenderTemplateInput(template="{{ 40 + 2 }}"))

        assert "42" in result

    @pytest.mark.asyncio
    async def test_execute_empty_template_result(self):
        """Test rendering template that returns empty result."""
        mock_client = AsyncMock()
        mock_client.render_template.return_value = ""
        core.client = mock_client

        result = await ha_render_template(RenderTemplateInput(template="{{ none }}"))

        assert "Template result:" in result
