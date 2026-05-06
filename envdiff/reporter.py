"""Formatting and printing of diff reports."""

from __future__ import annotations

from typing import Any, Dict

from envdiff.comparator import DiffResult
from envdiff.sorter import group_diff


def _to_dict(result: DiffResult) -> Dict[str, Any]:
    """Serialise a DiffResult to a plain dictionary."""
    return {
        "missing_in_target": dict(result.missing_in_target),
        "missing_in_base": dict(result.missing_in_base),
        "mismatched": {
            k: {"base": base, "target": target}
            for k, (base, target) in result.mismatched.items()
        },
    }


def format_report(result: DiffResult, *, show_values: bool = True) -> str:
    """Return a human-readable report string for *result*.

    Args:
        result:      The DiffResult to format.
        show_values: When False, omit actual values (useful for secrets).

    Returns:
        A multi-line string ready for printing.
    """
    grouped = group_diff(result)
    lines: list[str] = []

    if grouped.total == 0:
        return "No differences found."

    if grouped.missing_in_target:
        lines.append("Missing in target:")
        for key, value in grouped.missing_in_target.items():
            entry = f"  - {key}" + (f" = {value!r}" if show_values else "")
            lines.append(entry)

    if grouped.missing_in_base:
        lines.append("Missing in base:")
        for key, value in grouped.missing_in_base.items():
            entry = f"  + {key}" + (f" = {value!r}" if show_values else "")
            lines.append(entry)

    if grouped.mismatched:
        lines.append("Mismatched values:")
        for key, (base_val, target_val) in grouped.mismatched.items():
            if show_values:
                lines.append(f"  ~ {key}")
                lines.append(f"      base:   {base_val!r}")
                lines.append(f"      target: {target_val!r}")
            else:
                lines.append(f"  ~ {key}")

    lines.append(f"\nTotal differences: {grouped.total}")
    return "\n".join(lines)


def print_report(result: DiffResult, *, show_values: bool = True) -> None:
    """Print the formatted report to stdout."""
    print(format_report(result, show_values=show_values))
