"""ID generation utilities."""

import uuid
from typing import Literal


def generate_id(prefix: Literal["proj", "doc", "q", "sec", "ans", "req", "eval", "chunk"]) -> str:
    """Generate a unique ID with a prefix."""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}"
