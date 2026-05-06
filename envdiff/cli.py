"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare_envs
from envdiff.exporter import ExportFormat, export
from envdiff.loader import EnvLoadError, load_env_file
from envdiff.reporter import print_report
from envdiff.sorter import group_diff


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    parser.add_argument("base", type=Path, help="Base .env file")
    parser.add_argument("target", type=Path, help="Target .env file to compare against base")
    parser.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Report only missing keys; ignore value mismatches",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    parser.add_argument(
        "--export",
        metavar="FORMAT",
        choices=("json", "csv"),
        default=None,
        help="Export diff to stdout in the given format (json or csv) instead of human-readable output",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        type=Path,
        default=None,
        help="Write export output to FILE instead of stdout (requires --export)",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    try:
        base_env = load_env_file(args.base)
        target_env = load_env_file(args.target)
    except EnvLoadError as exc:
        print(f"envdiff: error: {exc}", file=sys.stderr)
        return 2

    result = compare_envs(base_env, target_env, ignore_values=args.ignore_values)
    grouped = group_diff(result)

    if args.export:
        fmt: ExportFormat = args.export  # type: ignore[assignment]
        output_text = export(result, grouped, fmt)
        if args.output:
            args.output.write_text(output_text, encoding="utf-8")
        else:
            print(output_text, end="")
    else:
        colour = not args.no_colour
        print_report(result, grouped, colour=colour)

    return 1 if result.has_differences else 0


def main() -> None:  # pragma: no cover
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))
