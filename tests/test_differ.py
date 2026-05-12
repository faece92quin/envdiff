"""Tests for envdiff.differ — the high-level diff driver."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.differ import DiffOptions, run_diff, sorted_diff
from envdiff.loader import EnvFile


def _make_file(name: str, data: dict) -> EnvFile:
    ef = EnvFile.__new__(EnvFile)
    ef.path = name
    ef.data = data
    ef.name = name
    return ef


# ---------------------------------------------------------------------------
# run_diff — basic comparison
# ---------------------------------------------------------------------------

def test_run_diff_no_differences():
    base = _make_file("base", {"A": "1", "B": "2"})
    target = _make_file("target", {"A": "1", "B": "2"})
    result = run_diff(base, target)
    assert isinstance(result, DiffResult)
    assert not result.missing_in_target
    assert not result.missing_in_base
    assert not result.mismatched


def test_run_diff_missing_in_target():
    base = _make_file("base", {"A": "1", "B": "2"})
    target = _make_file("target", {"A": "1"})
    result = run_diff(base, target)
    assert "B" in result.missing_in_target


def test_run_diff_missing_in_base():
    base = _make_file("base", {"A": "1"})
    target = _make_file("target", {"A": "1", "Z": "9"})
    result = run_diff(base, target)
    assert "Z" in result.missing_in_base


def test_run_diff_mismatched_values():
    base = _make_file("base", {"A": "1"})
    target = _make_file("target", {"A": "99"})
    result = run_diff(base, target)
    assert "A" in result.mismatched


# ---------------------------------------------------------------------------
# run_diff — ignore_values flag
# ---------------------------------------------------------------------------

def test_run_diff_ignore_values_suppresses_mismatch():
    base = _make_file("base", {"A": "1"})
    target = _make_file("target", {"A": "99"})
    opts = DiffOptions(ignore_values=True)
    result = run_diff(base, target, opts)
    assert not result.mismatched


# ---------------------------------------------------------------------------
# run_diff — prefix filter
# ---------------------------------------------------------------------------

def test_run_diff_prefix_filters_results():
    base = _make_file("base", {"DB_HOST": "a", "APP_KEY": "x"})
    target = _make_file("target", {"APP_KEY": "x"})
    opts = DiffOptions(prefix="APP")
    result = run_diff(base, target, opts)
    # DB_HOST missing in target, but prefix=APP should exclude it
    assert "DB_HOST" not in result.missing_in_target


# ---------------------------------------------------------------------------
# run_diff — only_keys filter
# ---------------------------------------------------------------------------

def test_run_diff_only_keys_restricts_output():
    base = _make_file("base", {"A": "1", "B": "2", "C": "3"})
    target = _make_file("target", {"A": "1"})
    opts = DiffOptions(only_keys=["A"])
    result = run_diff(base, target, opts)
    assert "B" not in result.missing_in_target
    assert "C" not in result.missing_in_target


# ---------------------------------------------------------------------------
# run_diff — statuses filter
# ---------------------------------------------------------------------------

def test_run_diff_statuses_filter_keeps_only_requested():
    base = _make_file("base", {"A": "1", "B": "old"})
    target = _make_file("target", {"B": "new", "C": "3"})
    opts = DiffOptions(statuses=["missing_in_target"])
    result = run_diff(base, target, opts)
    assert "A" in result.missing_in_target
    assert not result.mismatched
    assert not result.missing_in_base


# ---------------------------------------------------------------------------
# sorted_diff
# ---------------------------------------------------------------------------

def test_sorted_diff_returns_dict():
    base = _make_file("base", {"A": "1"})
    target = _make_file("target", {})
    grouped = sorted_diff(base, target)
    assert isinstance(grouped, dict)


def test_sorted_diff_contains_missing_key():
    base = _make_file("base", {"FOO": "bar"})
    target = _make_file("target", {})
    grouped = sorted_diff(base, target)
    all_keys = [k for keys in grouped.values() for k in keys]
    assert "FOO" in all_keys
