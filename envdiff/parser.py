"""Parser for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_PATTERN = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)


def parse_env_file(filepath: str | Path) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dict of key-value pairs.

    - Ignores blank lines and comments (lines starting with '#').
    - Strips inline comments after values.
    - Handles quoted values (single or double quotes).

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary mapping variable names to their values.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f".env file not found: {filepath}")

    env_vars: Dict[str, Optional[str]] = {}

    with filepath.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            match = ENV_LINE_PATTERN.match(line)
            if not match:
                continue

            key = match.group("key")
            raw_value = match.group("value").strip()

            value = _parse_value(raw_value)
            env_vars[key] = value

    return env_vars


def _parse_value(raw: str) -> Optional[str]:
    """Strip quotes and inline comments from a raw env value."""
    if not raw:
        return ""

    # Handle double-quoted values
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1]

    # Handle single-quoted values
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        return raw[1:-1]

    # Strip inline comments (unquoted values)
    comment_index = raw.find(" #")
    if comment_index != -1:
        raw = raw[:comment_index].strip()

    return raw


def get_keys(filepath: str | Path) -> list[str]:
    """Return a sorted list of variable names defined in a .env file.

    This is a convenience wrapper around :func:`parse_env_file` useful for
    quickly inspecting which keys are present without caring about values.

    Args:
        filepath: Path to the .env file.

    Returns:
        Sorted list of variable name strings.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return sorted(parse_env_file(filepath).keys())
