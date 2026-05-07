"""Merge multiple .env files into a single unified key-value mapping.

Later files take precedence over earlier ones (last-write-wins).
Optionally collect provenance so callers know which file contributed each key.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envdiff.loader import EnvFile


@dataclass
class MergeResult:
    """Result of merging two or more EnvFile objects."""

    merged: Dict[str, str] = field(default_factory=dict)
    # key -> list of (label, value) pairs in the order they were seen
    provenance: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)

    @property
    def keys(self) -> List[str]:
        return sorted(self.merged.keys())

    def origin(self, key: str) -> Optional[str]:
        """Return the label of the file that provided the winning value."""
        entries = self.provenance.get(key)
        if not entries:
            return None
        return entries[-1][0]

    def conflicts(self) -> Dict[str, List[Tuple[str, str]]]:
        """Return keys whose value differed across source files."""
        return {
            k: v
            for k, v in self.provenance.items()
            if len({val for _, val in v}) > 1
        }


def merge_env_files(env_files: List[EnvFile]) -> MergeResult:
    """Merge a sequence of EnvFile objects, last file wins on conflicts."""
    if not env_files:
        return MergeResult()

    result = MergeResult()
    for env_file in env_files:
        for key, value in env_file.data.items():
            result.merged[key] = value
            result.provenance.setdefault(key, []).append((env_file.label, value))

    return result
