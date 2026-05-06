"""Tests for envdiff.formatter."""
import pytest

from envdiff.formatter import (
    fmt_missing_in_target,
    fmt_missing_in_base,
    fmt_mismatch,
    fmt_section_header,
    fmt_summary,
)


# ---------------------------------------------------------------------------
# Colour disabled — easier to assert on plain text
# ---------------------------------------------------------------------------

class TestFmtMissingInTarget:
    def test_contains_key(self):
        result = fmt_missing_in_target("DB_HOST", colour=False)
        assert "DB_HOST" in result

    def test_contains_label(self):
        result = fmt_missing_in_target("DB_HOST", colour=False)
        assert "MISSING IN TARGET" in result

    def test_no_ansi_when_colour_off(self):
        result = fmt_missing_in_target("KEY", colour=False)
        assert "\033[" not in result

    def test_ansi_present_when_colour_on(self):
        result = fmt_missing_in_target("KEY", colour=True)
        assert "\033[" in result


class TestFmtMissingInBase:
    def test_contains_key(self):
        result = fmt_missing_in_base("SECRET", colour=False)
        assert "SECRET" in result

    def test_contains_label(self):
        result = fmt_missing_in_base("SECRET", colour=False)
        assert "MISSING IN BASE" in result


class TestFmtMismatch:
    def test_contains_key(self):
        result = fmt_mismatch("PORT", "5432", "3306", colour=False)
        assert "PORT" in result

    def test_contains_both_values(self):
        result = fmt_mismatch("PORT", "5432", "3306", colour=False)
        assert "5432" in result
        assert "3306" in result

    def test_contains_mismatch_label(self):
        result = fmt_mismatch("PORT", "5432", "3306", colour=False)
        assert "MISMATCH" in result

    def test_none_values_represented(self):
        result = fmt_mismatch("KEY", None, "val", colour=False)
        assert "None" in result


class TestFmtSectionHeader:
    def test_contains_title(self):
        result = fmt_section_header("Missing Keys", colour=False)
        assert "Missing Keys" in result

    def test_padded_to_60_chars(self):
        result = fmt_section_header("X", colour=False)
        assert len(result) >= 60


class TestFmtSummary:
    def test_contains_all_counts(self):
        result = fmt_summary(3, 1, 2, colour=False)
        assert "3" in result
        assert "1" in result
        assert "2" in result

    def test_contains_labels(self):
        result = fmt_summary(0, 0, 0, colour=False)
        assert "missing-in-target" in result
        assert "missing-in-base" in result
        assert "mismatched" in result

    def test_starts_with_summary(self):
        result = fmt_summary(0, 0, 0, colour=False)
        assert result.startswith("Summary:")
