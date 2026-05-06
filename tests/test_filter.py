"""Tests for envdiff.filter."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.filter import filter_by_keys, filter_by_prefix, filter_by_status


def _make() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST": "localhost", "APP_PORT": "8080"},
        missing_in_base={"CACHE_URL": "redis://"},
        mismatched={"DB_PASS": ("secret", "hunter2"), "APP_ENV": ("prod", "staging")},
    )


# --- filter_by_prefix ---

def test_prefix_keeps_matching_keys():
    result = filter_by_prefix(_make(), "DB_")
    assert "DB_HOST" in result.missing_in_target
    assert "DB_PASS" in result.mismatched


def test_prefix_removes_non_matching_keys():
    result = filter_by_prefix(_make(), "DB_")
    assert "APP_PORT" not in result.missing_in_target
    assert "CACHE_URL" not in result.missing_in_base
    assert "APP_ENV" not in result.mismatched


def test_prefix_is_case_insensitive():
    result = filter_by_prefix(_make(), "db_")
    assert "DB_HOST" in result.missing_in_target
    assert "DB_PASS" in result.mismatched


def test_prefix_no_match_returns_empty_buckets():
    result = filter_by_prefix(_make(), "UNKNOWN_")
    assert result.missing_in_target == {}
    assert result.missing_in_base == {}
    assert result.mismatched == {}


# --- filter_by_keys ---

def test_filter_by_keys_exact_match():
    result = filter_by_keys(_make(), ["DB_HOST", "CACHE_URL"])
    assert list(result.missing_in_target.keys()) == ["DB_HOST"]
    assert list(result.missing_in_base.keys()) == ["CACHE_URL"]
    assert result.mismatched == {}


def test_filter_by_keys_case_insensitive():
    result = filter_by_keys(_make(), ["db_host"])
    assert "DB_HOST" in result.missing_in_target


def test_filter_by_keys_empty_list_returns_empty():
    result = filter_by_keys(_make(), [])
    assert result.missing_in_target == {}
    assert result.missing_in_base == {}
    assert result.mismatched == {}


def test_filter_by_keys_unknown_key_ignored():
    result = filter_by_keys(_make(), ["DOES_NOT_EXIST"])
    assert result.missing_in_target == {}


# --- filter_by_status ---

def test_filter_by_status_exclude_mismatched():
    result = filter_by_status(_make(), include_mismatched=False)
    assert result.mismatched == {}
    assert result.missing_in_target == _make().missing_in_target
    assert result.missing_in_base == _make().missing_in_base


def test_filter_by_status_exclude_missing_in_target():
    result = filter_by_status(_make(), include_missing_in_target=False)
    assert result.missing_in_target == {}
    assert result.mismatched == _make().mismatched


def test_filter_by_status_exclude_missing_in_base():
    result = filter_by_status(_make(), include_missing_in_base=False)
    assert result.missing_in_base == {}


def test_filter_by_status_all_excluded_returns_empty():
    result = filter_by_status(
        _make(),
        include_missing_in_target=False,
        include_missing_in_base=False,
        include_mismatched=False,
    )
    assert result.missing_in_target == {}
    assert result.missing_in_base == {}
    assert result.mismatched == {}


def test_filter_by_status_all_included_unchanged():
    original = _make()
    result = filter_by_status(original)
    assert result.missing_in_target == original.missing_in_target
    assert result.missing_in_base == original.missing_in_base
    assert result.mismatched == original.mismatched
