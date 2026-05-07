"""Human-readable report for a MergeResult.

Provides text formatting for merged env output and conflict warnings.
"""
from __future__ import annotations

from typing import List

from envdiff.merger import MergeResult

_RESET = "\033[0m"
_YELLOW = "\033[33m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_BOLD = "\033[1m"


def _c(text: str, code: str, colour: bool) -> str:
    return f"{code}{text}{_RESET}" if colour else text


def format_merge_report(result: MergeResult, *, colour: bool = True) -> str:
    """Return a multi-line string summarising the merge."""
    lines: List[str] = []

    conflicts = result.conflicts()
    total = len(result.merged)
    n_conflicts = len(conflicts)

    header = f"Merged {total} key(s) from multiple files"
    lines.append(_c(header, _BOLD, colour))

    if n_conflicts:
        warn = f"  {n_conflicts} conflict(s) detected (last-file wins):"
        lines.append(_c(warn, _YELLOW, colour))
        for key, entries in sorted(conflicts.items()):
            lines.append(f"    {_c(key, _BOLD, colour)}")
            for label, value in entries:
                marker = "->" if (label, value) == entries[-1] else "  "
                lines.append(f"      {marker} [{label}] {value}")
    else:
        lines.append(_c("  No conflicts.", _GREEN, colour))

    lines.append("")
    lines.append(_c("Merged values:", _BOLD, colour))
    for key in result.keys:
        origin = result.origin(key) or "?"
        lines.append(f"  {key}={result.merged[key]}  (from: {origin})")

    return "\n".join(lines)


def print_merge_report(result: MergeResult, *, colour: bool = True) -> None:
    """Print the merge report to stdout."""
    print(format_merge_report(result, colour=colour))
