"""Tests for envdiff.sorter."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter import GroupedDiff, group_diff, sort_keys_by_status


def _make_result(
    missing_in_target=None,
    missing_in_base=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_target=missing_in_target or {},
        missing_in_base=missing_in_base or {},
        mismatched=mismatched or {},
    )


class TestGroupDiff:
    def test_empty_result_produces_empty_groups(self):
        result = _make_result()
        grouped = group_diff(result)
        assert grouped.missing_in_target == {}
        assert grouped.missing_in_base == {}
        assert grouped.mismatched == {}

    def test_missing_in_target_sorted(self):
        result = _make_result(missing_in_target={"ZEBRA": "z", "ALPHA": "a"})
        grouped = group_diff(result)
        assert list(grouped.missing_in_target.keys()) == ["ALPHA", "ZEBRA"]

    def test_missing_in_base_sorted(self):
        result = _make_result(missing_in_base={"PORT": "8080", "HOST": "localhost"})
        grouped = group_diff(result)
        assert list(grouped.missing_in_base.keys()) == ["HOST", "PORT"]

    def test_mismatched_sorted(self):
        result = _make_result(
            mismatched={"Z_KEY": ("a", "b"), "A_KEY": ("x", "y")}
        )
        grouped = group_diff(result)
        assert list(grouped.mismatched.keys()) == ["A_KEY", "Z_KEY"]

    def test_total_counts_all_entries(self):
        result = _make_result(
            missing_in_target={"A": "1"},
            missing_in_base={"B": "2", "C": "3"},
            mismatched={"D": ("old", "new")},
        )
        grouped = group_diff(result)
        assert grouped.total == 4

    def test_all_keys_sorted_merges_categories(self):
        result = _make_result(
            missing_in_target={"CHARLIE": "c"},
            missing_in_base={"ALPHA": "a"},
            mismatched={"BRAVO": ("x", "y")},
        )
        grouped = group_diff(result)
        assert grouped.all_keys_sorted == ["ALPHA", "BRAVO", "CHARLIE"]

    def test_total_zero_for_empty(self):
        assert group_diff(_make_result()).total == 0


class TestSortKeysByStatus:
    def test_ordering_missing_target_first(self):
        result = _make_result(
            missing_in_target={"MT": "1"},
            missing_in_base={"MB": "2"},
            mismatched={"MM": ("a", "b")},
        )
        keys = sort_keys_by_status(result)
        assert keys == ["MT", "MB", "MM"]

    def test_each_group_sorted_alphabetically(self):
        result = _make_result(
            missing_in_target={"Z": "z", "A": "a"},
            missing_in_base={"Y": "y", "B": "b"},
            mismatched={"X": ("1", "2"), "C": ("3", "4")},
        )
        keys = sort_keys_by_status(result)
        assert keys == ["A", "Z", "B", "Y", "C", "X"]

    def test_empty_returns_empty_list(self):
        assert sort_keys_by_status(_make_result()) == []

    def test_only_mismatched(self):
        result = _make_result(mismatched={"KEY": ("v1", "v2")})
        assert sort_keys_by_status(result) == ["KEY"]
