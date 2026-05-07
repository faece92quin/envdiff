"""Tests for envdiff.merger."""
from __future__ import annotations

import pytest

from envdiff.loader import EnvFile
from envdiff.merger import MergeResult, merge_env_files


def _make(label: str, data: dict) -> EnvFile:
    env = EnvFile.__new__(EnvFile)
    env.label = label
    env.path = f"/fake/{label}.env"
    env.data = data
    return env


# ---------------------------------------------------------------------------
# merge_env_files
# ---------------------------------------------------------------------------

def test_empty_list_returns_empty_result():
    result = merge_env_files([])
    assert result.merged == {}
    assert result.provenance == {}


def test_single_file_all_keys_present():
    env = _make("base", {"A": "1", "B": "2"})
    result = merge_env_files([env])
    assert result.merged == {"A": "1", "B": "2"}


def test_last_file_wins_on_conflict():
    base = _make("base", {"KEY": "old"})
    override = _make("prod", {"KEY": "new"})
    result = merge_env_files([base, override])
    assert result.merged["KEY"] == "new"


def test_keys_from_all_files_are_included():
    a = _make("a", {"X": "1"})
    b = _make("b", {"Y": "2"})
    result = merge_env_files([a, b])
    assert "X" in result.merged
    assert "Y" in result.merged


def test_provenance_records_all_sources():
    base = _make("base", {"KEY": "v1"})
    prod = _make("prod", {"KEY": "v2"})
    result = merge_env_files([base, prod])
    entries = result.provenance["KEY"]
    assert ("base", "v1") in entries
    assert ("prod", "v2") in entries


def test_origin_returns_last_file_label():
    base = _make("base", {"KEY": "v1"})
    prod = _make("prod", {"KEY": "v2"})
    result = merge_env_files([base, prod])
    assert result.origin("KEY") == "prod"


def test_origin_returns_none_for_unknown_key():
    result = merge_env_files([_make("base", {"A": "1"})])
    assert result.origin("MISSING") is None


def test_conflicts_returns_only_differing_keys():
    base = _make("base", {"SAME": "x", "DIFF": "old"})
    prod = _make("prod", {"SAME": "x", "DIFF": "new"})
    result = merge_env_files([base, prod])
    conflicts = result.conflicts()
    assert "DIFF" in conflicts
    assert "SAME" not in conflicts


def test_no_conflicts_when_all_values_equal():
    a = _make("a", {"K": "v"})
    b = _make("b", {"K": "v"})
    result = merge_env_files([a, b])
    assert result.conflicts() == {}


def test_keys_property_is_sorted():
    env = _make("e", {"Z": "1", "A": "2", "M": "3"})
    result = merge_env_files([env])
    assert result.keys == ["A", "M", "Z"]


# ---------------------------------------------------------------------------
# MergeResult.conflicts – three-way scenario
# ---------------------------------------------------------------------------

def test_three_way_conflict_captured():
    a = _make("a", {"PORT": "3000"})
    b = _make("b", {"PORT": "4000"})
    c = _make("c", {"PORT": "5000"})
    result = merge_env_files([a, b, c])
    assert result.merged["PORT"] == "5000"
    assert len(result.provenance["PORT"]) == 3
