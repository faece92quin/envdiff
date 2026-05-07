"""Tests for envdiff.merge_reporter."""
from __future__ import annotations

from envdiff.loader import EnvFile
from envdiff.merger import merge_env_files
from envdiff.merge_reporter import format_merge_report, print_merge_report


def _make(label: str, data: dict) -> EnvFile:
    env = EnvFile.__new__(EnvFile)
    env.label = label
    env.path = f"/fake/{label}.env"
    env.data = data
    return env


def test_report_contains_key_count():
    result = merge_env_files([_make("a", {"X": "1", "Y": "2"})])
    report = format_merge_report(result, colour=False)
    assert "2 key(s)" in report


def test_report_no_conflicts_message():
    result = merge_env_files([_make("a", {"K": "v"})])
    report = format_merge_report(result, colour=False)
    assert "No conflicts" in report


def test_report_shows_conflict_key():
    a = _make("base", {"PORT": "3000"})
    b = _make("prod", {"PORT": "4000"})
    result = merge_env_files([a, b])
    report = format_merge_report(result, colour=False)
    assert "PORT" in report
    assert "conflict" in report.lower()


def test_report_shows_winning_value():
    a = _make("base", {"PORT": "3000"})
    b = _make("prod", {"PORT": "4000"})
    result = merge_env_files([a, b])
    report = format_merge_report(result, colour=False)
    assert "4000" in report


def test_report_lists_all_merged_keys():
    a = _make("a", {"ALPHA": "1"})
    b = _make("b", {"BETA": "2"})
    result = merge_env_files([a, b])
    report = format_merge_report(result, colour=False)
    assert "ALPHA" in report
    assert "BETA" in report


def test_report_shows_origin_label():
    a = _make("staging", {"DB": "sqlite"})
    result = merge_env_files([a])
    report = format_merge_report(result, colour=False)
    assert "staging" in report


def test_colour_off_has_no_ansi():
    result = merge_env_files([_make("a", {"K": "v"})])
    report = format_merge_report(result, colour=False)
    assert "\033[" not in report


def test_colour_on_contains_ansi():
    result = merge_env_files([_make("a", {"K": "v"})])
    report = format_merge_report(result, colour=True)
    assert "\033[" in report


def test_print_merge_report_outputs_text(capsys):
    result = merge_env_files([_make("env", {"A": "1"})])
    print_merge_report(result, colour=False)
    captured = capsys.readouterr()
    assert "A=1" in captured.out


def test_conflict_count_in_header():
    a = _make("a", {"X": "old", "Y": "same"})
    b = _make("b", {"X": "new", "Y": "same"})
    result = merge_env_files([a, b])
    report = format_merge_report(result, colour=False)
    assert "1 conflict(s)" in report
