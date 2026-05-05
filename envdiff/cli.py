"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.comparator import compare_envs
from envdiff.loader import EnvLoadError, load_env_file
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and surface missing or mismatched keys.",
    )
    parser.add_argument(
        "base",
        metavar="BASE",
        help="Path to the base .env file (e.g. .env or .env.example).",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target .env file to compare against BASE.",
    )
    parser.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Only compare keys; ignore value differences.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color codes in text output.",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    """Entry point for the CLI.

    Returns:
        Exit code: 0 if no differences found, 1 if differences exist, 2 on error.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        base_env = load_env_file(args.base)
        target_env = load_env_file(args.target)
    except EnvLoadError as exc:
        print(f"envdiff error: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(
        base_env.data,
        target_env.data,
        ignore_values=args.ignore_values,
    )

    print_report(
        result,
        base_label=base_env.name,
        target_label=target_env.name,
        output_format=args.output_format,
        color=not args.no_color,
    )

    return 1 if result.has_differences() else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
