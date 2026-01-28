"""Unit tests for tools utility functions."""

import json
import pytest
from pydantic import BaseModel

from home_assistant_mcp.tools.utils import format_response


class MockModel(BaseModel):
    """Mock Pydantic model for testing."""

    name: str
    value: int


class TestFormatResponse:
    """Tests for format_response function."""

    def test_format_response_with_pydantic_model(self):
        """Test formatting a Pydantic model."""
        model = MockModel(name="test", value=42)
        result = format_response(model)

        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["value"] == 42
        assert "\n" in result  # Check for indentation

    def test_format_response_with_list_of_models(self):
        """Test formatting a list of Pydantic models."""
        models = [
            MockModel(name="first", value=1),
            MockModel(name="second", value=2),
        ]
        result = format_response(models)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "first"
        assert parsed[1]["value"] == 2

    def test_format_response_with_list_of_dicts(self):
        """Test formatting a list of dictionaries."""
        data = [
            {"name": "first", "value": 1},
            {"name": "second", "value": 2},
        ]
        result = format_response(data)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "first"

    def test_format_response_with_mixed_list(self):
        """Test formatting a list with mixed types."""
        data = [
            MockModel(name="model", value=1),
            {"name": "dict", "value": 2},
        ]
        result = format_response(data)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "model"
        assert parsed[1]["name"] == "dict"

    def test_format_response_with_plain_dict(self):
        """Test formatting a plain dictionary."""
        data = {"name": "test", "value": 42}
        result = format_response(data)

        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["value"] == 42

    def test_format_response_with_string(self):
        """Test formatting a string."""
        result = format_response("test string")
        parsed = json.loads(result)
        assert parsed == "test string"

    def test_format_response_with_number(self):
        """Test formatting a number."""
        result = format_response(42)
        parsed = json.loads(result)
        assert parsed == 42

    def test_format_response_with_none(self):
        """Test formatting None."""
        result = format_response(None)
        parsed = json.loads(result)
        assert parsed is None
