"""Filter utilities for envdiff.

Provides helpers to narrow down DiffResult entries by key prefix,
exact key list, or status type before reporting or exporting.
"""

from __future__ import annotations

from typing import Iterable, Optional

from envdiff.comparator import DiffResult


def filter_by_prefix(
    result: DiffResult,
    prefix: str,
) -> DiffResult:
    """Return a new DiffResult containing only keys that start with *prefix*."""
    prefix_upper = prefix.upper()
    return DiffResult(
        missing_in_target={
            k: v for k, v in result.missing_in_target.items()
            if k.upper().startswith(prefix_upper)
        },
        missing_in_base={
            k: v for k, v in result.missing_in_base.items()
            if k.upper().startswith(prefix_upper)
        },
        mismatched={
            k: v for k, v in result.mismatched.items()
            if k.upper().startswith(prefix_upper)
        },
    )


def filter_by_keys(
    result: DiffResult,
    keys: Iterable[str],
) -> DiffResult:
    """Return a new DiffResult restricted to the supplied *keys* (case-insensitive)."""
    key_set = {k.upper() for k in keys}
    return DiffResult(
        missing_in_target={
            k: v for k, v in result.missing_in_target.items()
            if k.upper() in key_set
        },
        missing_in_base={
            k: v for k, v in result.missing_in_base.items()
            if k.upper() in key_set
        },
        mismatched={
            k: v for k, v in result.mismatched.items()
            if k.upper() in key_set
        },
    )


def filter_by_status(
    result: DiffResult,
    *,
    include_missing_in_target: bool = True,
    include_missing_in_base: bool = True,
    include_mismatched: bool = True,
) -> DiffResult:
    """Return a new DiffResult with unwanted status buckets cleared."""
    return DiffResult(
        missing_in_target=result.missing_in_target if include_missing_in_target else {},
        missing_in_base=result.missing_in_base if include_missing_in_base else {},
        mismatched=result.mismatched if include_mismatched else {},
    )
