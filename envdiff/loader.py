"""Loader module for reading and resolving .env files from the filesystem."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


class EnvFile:
    """Represents a loaded .env file with its path and parsed key-value pairs."""

    def __init__(self, path: Path, data: Dict[str, str]) -> None:
        self.path = path
        self.data = data
        self.name = path.name

    def __repr__(self) -> str:  # pragma: no cover
        return f"EnvFile(path={self.path!r}, keys={list(self.data.keys())})"


class EnvLoadError(Exception):
    """Raised when an .env file cannot be loaded."""


def load_env_file(path: str | Path) -> EnvFile:
    """Load and parse a single .env file.

    Args:
        path: Filesystem path to the .env file.

    Returns:
        An :class:`EnvFile` instance with parsed key-value data.

    Raises:
        EnvLoadError: If the file does not exist or cannot be read.
    """
    resolved = Path(path).resolve()
    if not resolved.exists():
        raise EnvLoadError(f"File not found: {resolved}")
    if not resolved.is_file():
        raise EnvLoadError(f"Path is not a file: {resolved}")
    try:
        data = parse_env_file(str(resolved))
    except OSError as exc:
        raise EnvLoadError(f"Could not read file {resolved}: {exc}") from exc
    return EnvFile(path=resolved, data=data)


def load_env_files(paths: List[str | Path]) -> List[EnvFile]:
    """Load multiple .env files in order.

    Args:
        paths: List of filesystem paths to .env files.

    Returns:
        List of :class:`EnvFile` instances in the same order as *paths*.

    Raises:
        EnvLoadError: If any file cannot be loaded.
    """
    return [load_env_file(p) for p in paths]


def discover_env_files(
    directory: str | Path,
    pattern: str = ".env*",
    exclude: Optional[List[str]] = None,
) -> List[EnvFile]:
    """Discover and load .env files matching *pattern* inside *directory*.

    Args:
        directory: Root directory to search.
        pattern: Glob pattern used to match filenames.
        exclude: Optional list of filenames to skip (e.g. [".env.example"]).

    Returns:
        Sorted list of loaded :class:`EnvFile` instances.
    """
    root = Path(directory).resolve()
    exclude_set: set[str] = set(exclude or [])
    matched = sorted(root.glob(pattern))
    files: List[EnvFile] = []
    for candidate in matched:
        if candidate.is_file() and candidate.name not in exclude_set:
            files.append(load_env_file(candidate))
    return files
