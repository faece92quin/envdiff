"""Tests for envdiff.cli module."""

from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.cli import build_parser, run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------

def test_build_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args([".env", ".env.prod"])
    assert args.base == ".env"
    assert args.target == ".env.prod"
    assert args.ignore_values is False
    assert args.output_format == "text"
    assert args.no_color is False


def test_build_parser_flags() -> None:
    parser = build_parser()
    args = parser.parse_args([".env", ".env.prod", "--ignore-values", "--format", "json", "--no-color"])
    assert args.ignore_values is True
    assert args.output_format == "json"
    assert args.no_color is True


# ---------------------------------------------------------------------------
# run — exit codes
# ---------------------------------------------------------------------------

def test_run_returns_0_when_no_differences(tmp_path: Path) -> None:
    base = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    target = _write(tmp_path, ".env.prod", "FOO=bar\nBAZ=qux\n")
    code = run([str(base), str(target)])
    assert code == 0


def test_run_returns_1_when_keys_missing(tmp_path: Path) -> None:
    base = _write(tmp_path, ".env", "FOO=bar\nMISSING=yes\n")
    target = _write(tmp_path, ".env.prod", "FOO=bar\n")
    code = run([str(base), str(target)])
    assert code == 1


def test_run_returns_1_when_values_differ(tmp_path: Path) -> None:
    base = _write(tmp_path, ".env", "FOO=bar\n")
    target = _write(tmp_path, ".env.prod", "FOO=different\n")
    code = run([str(base), str(target)])
    assert code == 1


def test_run_returns_0_with_ignore_values_flag(tmp_path: Path) -> None:
    base = _write(tmp_path, ".env", "FOO=bar\n")
    target = _write(tmp_path, ".env.prod", "FOO=different\n")
    code = run([str(base), str(target), "--ignore-values"])
    assert code == 0


def test_run_returns_2_on_missing_base_file(tmp_path: Path) -> None:
    target = _write(tmp_path, ".env.prod", "FOO=bar\n")
    code = run([str(tmp_path / "nonexistent.env"), str(target)])
    assert code == 2


def test_run_returns_2_on_missing_target_file(tmp_path: Path) -> None:
    base = _write(tmp_path, ".env", "FOO=bar\n")
    code = run([str(base), str(tmp_path / "nonexistent.env")])
    assert code == 2


def test_run_json_format_no_error(tmp_path: Path, capsys) -> None:
    base = _write(tmp_path, ".env", "FOO=bar\n")
    target = _write(tmp_path, ".env.prod", "FOO=bar\n")
    code = run([str(base), str(target), "--format", "json"])
    assert code == 0
    captured = capsys.readouterr()
    assert captured.out  # some output was produced


def test_run_no_color_flag(tmp_path: Path) -> None:
    base = _write(tmp_path, ".env", "FOO=bar\n")
    target = _write(tmp_path, ".env.prod", "FOO=baz\n")
    code = run([str(base), str(target), "--no-color"])
    assert code == 1
