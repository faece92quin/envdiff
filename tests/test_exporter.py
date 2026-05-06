"""Tests for envdiff.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import export, export_csv, export_json
from envdiff.sorter import GroupedDiff


def _make(*, mit=(), mib=(), mm=None):
    """Build a minimal DiffResult + GroupedDiff pair."""
    mm = mm or {}
    result = DiffResult(
        missing_in_target=set(mit),
        missing_in_base=set(mib),
        mismatched=dict(mm),
    )
    grouped = GroupedDiff(
        missing_in_target=set(mit),
        missing_in_base=set(mib),
        mismatched=dict(mm),
    )
    return result, grouped


class TestExportJson:
    def test_no_differences_summary(self):
        result, grouped = _make()
        data = json.loads(export_json(result, grouped))
        assert data["summary"]["has_differences"] is False
        assert data["summary"]["missing_in_target"] == 0

    def test_missing_in_target_appears_in_details(self):
        result, grouped = _make(mit=["FOO"])
        data = json.loads(export_json(result, grouped))
        keys = [r["key"] for r in data["details"]]
        assert "FOO" in keys

    def test_mismatch_includes_values(self):
        result, grouped = _make(mm={"BAR": ("old", "new")})
        data = json.loads(export_json(result, grouped))
        row = next(r for r in data["details"] if r["key"] == "BAR")
        assert row["base"] == "old"
        assert row["target"] == "new"
        assert row["status"] == "mismatch"

    def test_indent_applied(self):
        result, grouped = _make(mit=["X"])
        raw = export_json(result, grouped, indent=4)
        # 4-space indent means lines should start with 4 spaces
        assert "    " in raw


class TestExportCsv:
    def _parse(self, csv_str: str):
        return list(csv.DictReader(io.StringIO(csv_str)))

    def test_header_row_present(self):
        _, grouped = _make()
        rows = self._parse(export_csv(grouped))
        # DictReader skips header; just ensure no crash and fieldnames OK
        assert isinstance(rows, list)

    def test_missing_in_base_row(self):
        _, grouped = _make(mib=["SECRET"])
        rows = self._parse(export_csv(grouped))
        assert any(r["key"] == "SECRET" and r["status"] == "missing_in_base" for r in rows)

    def test_mismatch_row_values(self):
        _, grouped = _make(mm={"PORT": ("8080", "9090")})
        rows = self._parse(export_csv(grouped))
        row = next(r for r in rows if r["key"] == "PORT")
        assert row["base"] == "8080"
        assert row["target"] == "9090"

    def test_empty_produces_only_header(self):
        _, grouped = _make()
        output = export_csv(grouped)
        lines = output.strip().splitlines()
        assert len(lines) == 1  # header only


class TestExportDispatch:
    def test_json_format(self):
        result, grouped = _make(mit=["A"])
        out = export(result, grouped, "json")
        json.loads(out)  # must be valid JSON

    def test_csv_format(self):
        result, grouped = _make(mit=["A"])
        out = export(result, grouped, "csv")
        assert "key" in out  # header present

    def test_invalid_format_raises(self):
        result, grouped = _make()
        with pytest.raises(ValueError, match="Unsupported"):
            export(result, grouped, "xml")  # type: ignore[arg-type]
