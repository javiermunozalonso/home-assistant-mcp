
import json
from typing import Any

def format_response(data: Any) -> str:
    """Format response data as JSON string."""
    if hasattr(data, "model_dump"):
        return json.dumps(data.model_dump(), indent=2, default=str)
    if isinstance(data, list):
        return json.dumps(
            [item.model_dump() if hasattr(item, "model_dump") else item for item in data],
            indent=2,
            default=str,
        )
    return json.dumps(data, indent=2, default=str)
