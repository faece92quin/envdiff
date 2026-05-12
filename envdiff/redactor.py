"""Redact sensitive values in env diff output.

Provides utilities to mask values for keys that match known sensitive
patterns (e.g. passwords, tokens, secrets) before display or export.
"""

from __future__ import annotations

import re
from typing import Iterable

from envdiff.comparator import DiffResult

_DEFAULT_PATTERNS: list[str] = [
    r"password",
    r"passwd",
    r"secret",
    r"token",
    r"api[_\-]?key",
    r"private[_\-]?key",
    r"auth",
    r"credential",
    r"access[_\-]?key",
]

REDACTED = "***REDACTED***"


def _compile_patterns(patterns: Iterable[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def is_sensitive(key: str, patterns: list[re.Pattern[str]]) -> bool:
    """Return True if *key* matches any of the compiled *patterns*."""
    return any(p.search(key) for p in patterns)


def redact_value(key: str, value: str, patterns: list[re.Pattern[str]]) -> str:
    """Return REDACTED placeholder when *key* is sensitive, else *value*."""
    return REDACTED if is_sensitive(key, patterns) else value


def redact_result(
    result: DiffResult,
    extra_patterns: Iterable[str] | None = None,
) -> DiffResult:
    """Return a new :class:`DiffResult` with sensitive values redacted.

    Values in *missing_in_target*, *missing_in_base*, and *mismatched*
    are replaced with ``REDACTED`` for any key that matches the default
    sensitive-key patterns or any caller-supplied *extra_patterns*.
    """
    all_patterns = list(_DEFAULT_PATTERNS)
    if extra_patterns:
        all_patterns.extend(extra_patterns)
    compiled = _compile_patterns(all_patterns)

    def _mask(key: str, value: str) -> str:
        return redact_value(key, value, compiled)

    redacted_missing_target = {
        k: _mask(k, v) for k, v in result.missing_in_target.items()
    }
    redacted_missing_base = {
        k: _mask(k, v) for k, v in result.missing_in_base.items()
    }
    redacted_mismatched = {
        k: (_mask(k, base_val), _mask(k, target_val))
        for k, (base_val, target_val) in result.mismatched.items()
    }

    return DiffResult(
        missing_in_target=redacted_missing_target,
        missing_in_base=redacted_missing_base,
        mismatched=redacted_mismatched,
    )
