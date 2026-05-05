"""Format and output DiffResult reports."""

import json
import sys
from typing import IO, Literal

from envdiff.comparator import DiffResult

OutputFormat = Literal["text", "json"]


def _to_dict(result: DiffResult) -> dict:
    return {
        "base": result.base_name,
        "target": result.target_name,
        "missing_in_target": sorted(result.missing_in_target),
        "missing_in_base": sorted(result.missing_in_base),
        "mismatched": {
            k: result.mismatched[k] for k in sorted(result.mismatched)
        },
        "has_differences": result.has_differences,
    }


def format_report(result: DiffResult, fmt: OutputFormat = "text") -> str:
    """Render a DiffResult as a string in the requested format.

    Args:
        result: The diff result to render.
        fmt: Output format — 'text' (human-readable) or 'json'.

    Returns:
        Formatted string representation of the diff.
    """
    if fmt == "json":
        return json.dumps(_to_dict(result), indent=2)
    return result.summary()


def print_report(
    result: DiffResult,
    fmt: OutputFormat = "text",
    stream: IO[str] = None,
) -> int:
    """Print a DiffResult report and return an exit code.

    Args:
        result: The diff result to print.
        fmt: Output format — 'text' or 'json'.
        stream: Output stream (defaults to stdout).

    Returns:
        1 if there are differences, 0 otherwise.
    """
    if stream is None:
        stream = sys.stdout
    print(format_report(result, fmt=fmt), file=stream)
    return 1 if result.has_differences else 0
