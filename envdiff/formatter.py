"""Colour-aware text formatter for envdiff diff output."""
from __future__ import annotations

from typing import Optional

# ANSI escape codes
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def _colourise(text: str, code: str, *, colour: bool) -> str:
    if not colour:
        return text
    return f"{code}{text}{_RESET}"


def fmt_missing_in_target(key: str, *, colour: bool = True) -> str:
    """Format a key that is present in base but absent in target."""
    label = _colourise("MISSING IN TARGET", _RED, colour=colour)
    key_str = _colourise(key, _BOLD, colour=colour)
    return f"  {key_str}  [{label}]"


def fmt_missing_in_base(key: str, *, colour: bool = True) -> str:
    """Format a key that is present in target but absent in base."""
    label = _colourise("MISSING IN BASE", _GREEN, colour=colour)
    key_str = _colourise(key, _BOLD, colour=colour)
    return f"  {key_str}  [{label}]"


def fmt_mismatch(key: str, base_val: Optional[str], target_val: Optional[str], *, colour: bool = True) -> str:
    """Format a key whose value differs between base and target."""
    label = _colourise("MISMATCH", _YELLOW, colour=colour)
    key_str = _colourise(key, _BOLD, colour=colour)
    base_display = _colourise(repr(base_val), _CYAN, colour=colour)
    target_display = _colourise(repr(target_val), _CYAN, colour=colour)
    return f"  {key_str}  [{label}]  base={base_display}  target={target_display}"


def fmt_section_header(title: str, *, colour: bool = True) -> str:
    """Format a section header line."""
    header = f"── {title} "
    header = header.ljust(60, "─")
    return _colourise(header, _BOLD, colour=colour)


def fmt_summary(missing_target: int, missing_base: int, mismatched: int, *, colour: bool = True) -> str:
    """Format a one-line summary of diff counts."""
    parts = [
        _colourise(f"{missing_target} missing-in-target", _RED, colour=colour),
        _colourise(f"{missing_base} missing-in-base", _GREEN, colour=colour),
        _colourise(f"{mismatched} mismatched", _YELLOW, colour=colour),
    ]
    return "Summary: " + ", ".join(parts)
