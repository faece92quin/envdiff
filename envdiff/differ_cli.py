"""Optional thin CLI wrapper that exposes the high-level differ.

Usage
-----
    python -m envdiff.differ_cli base.env target.env [--prefix DB] [--ignore-values]

This complements the main ``envdiff.cli`` entry-point with a focused
command that streams results to stdout via the existing reporter.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.differ import DiffOptions, run_diff
from envdiff.loader import load_env_file, EnvLoadError
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="differ",
        description="High-level diff driver with built-in filtering.",
    )
    p.add_argument("base", help="Path to the base .env file")
    p.add_argument("target", help="Path to the target .env file")
    p.add_argument("--prefix", default=None, help="Only compare keys with this prefix")
    p.add_argument(
        "--only-keys",
        nargs="+",
        metavar="KEY",
        default=[],
        help="Restrict diff to these specific keys",
    )
    p.add_argument(
        "--statuses",
        nargs="+",
        metavar="STATUS",
        default=[],
        choices=["missing_in_target", "missing_in_base", "mismatched"],
        help="Show only these diff statuses",
    )
    p.add_argument(
        "--ignore-values",
        action="store_true",
        default=False,
        help="Ignore value mismatches; report only missing keys",
    )
    p.add_argument(
        "--no-colour",
        action="store_true",
        default=False,
        help="Disable ANSI colour output",
    )
    return p


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        base_file = load_env_file(args.base)
        target_file = load_env_file(args.target)
    except EnvLoadError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    options = DiffOptions(
        ignore_values=args.ignore_values,
        prefix=args.prefix,
        only_keys=args.only_keys or [],
        statuses=args.statuses or [],
    )

    result = run_diff(base_file, target_file, options)
    print_report(result, colour=not args.no_colour)
    return 1 if result.missing_in_target or result.missing_in_base or result.mismatched else 0


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
