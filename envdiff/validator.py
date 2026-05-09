"""Validate .env files against a schema of required and optional keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Set


@dataclass
class ValidationResult:
    """Outcome of validating an env mapping against a schema."""

    missing_required: Set[str] = field(default_factory=set)
    unknown_keys: Set[str] = field(default_factory=set)
    empty_required: Set[str] = field(default_factory=set)

    @property
    def is_valid(self) -> bool:
        """Return True only when no violations were found."""
        return not (self.missing_required or self.unknown_keys or self.empty_required)

    def summary(self) -> str:
        parts: list[str] = []
        if self.missing_required:
            keys = ", ".join(sorted(self.missing_required))
            parts.append(f"Missing required keys: {keys}")
        if self.empty_required:
            keys = ", ".join(sorted(self.empty_required))
            parts.append(f"Required keys with empty values: {keys}")
        if self.unknown_keys:
            keys = ", ".join(sorted(self.unknown_keys))
            parts.append(f"Unknown keys not in schema: {keys}")
        return "\n".join(parts) if parts else "OK"


def validate_env(
    env: Dict[str, str],
    required: Iterable[str] = (),
    optional: Optional[Iterable[str]] = None,
    allow_unknown: bool = True,
) -> ValidationResult:
    """Validate *env* against sets of required and optional keys.

    Parameters
    ----------
    env:
        Parsed key/value mapping (e.g. from ``load_env_file``).
    required:
        Keys that must be present and non-empty.
    optional:
        Keys that may be present.  When *allow_unknown* is ``False`` any key
        not in *required* ∪ *optional* is flagged as unknown.
    allow_unknown:
        If ``False``, keys absent from the schema are reported.
    """
    required_set: Set[str] = set(required)
    optional_set: Set[str] = set(optional) if optional is not None else set()
    known: Set[str] = required_set | optional_set

    missing_required: Set[str] = set()
    empty_required: Set[str] = set()
    unknown_keys: Set[str] = set()

    for key in required_set:
        if key not in env:
            missing_required.add(key)
        elif env[key] == "":
            empty_required.add(key)

    if not allow_unknown:
        for key in env:
            if key not in known:
                unknown_keys.add(key)

    return ValidationResult(
        missing_required=missing_required,
        unknown_keys=unknown_keys,
        empty_required=empty_required,
    )
