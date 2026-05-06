"""Utilities for sorting and grouping diff results by category."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class GroupedDiff:
    """DiffResult entries grouped by category for structured reporting."""

    missing_in_target: Dict[str, str] = field(default_factory=dict)
    missing_in_base: Dict[str, str] = field(default_factory=dict)
    mismatched: Dict[str, tuple] = field(default_factory=dict)

    @property
    def all_keys_sorted(self) -> List[str]:
        """Return all affected keys in alphabetical order."""
        keys = (
            set(self.missing_in_target)
            | set(self.missing_in_base)
            | set(self.mismatched)
        )
        return sorted(keys)

    @property
    def total(self) -> int:
        """Total number of differing entries."""
        return (
            len(self.missing_in_target)
            + len(self.missing_in_base)
            + len(self.mismatched)
        )


def group_diff(result: DiffResult) -> GroupedDiff:
    """Group a DiffResult into a structured GroupedDiff.

    Args:
        result: The DiffResult produced by compare_envs.

    Returns:
        A GroupedDiff with entries sorted alphabetically within each category.
    """
    return GroupedDiff(
        missing_in_target=dict(sorted(result.missing_in_target.items())),
        missing_in_base=dict(sorted(result.missing_in_base.items())),
        mismatched=dict(sorted(result.mismatched.items())),
    )


def sort_keys_by_status(result: DiffResult) -> List[str]:
    """Return all differing keys sorted: missing-in-target first, then
    missing-in-base, then mismatched — each group sorted alphabetically.

    Args:
        result: The DiffResult to inspect.

    Returns:
        Ordered list of key names.
    """
    return (
        sorted(result.missing_in_target)
        + sorted(result.missing_in_base)
        + sorted(result.mismatched)
    )
