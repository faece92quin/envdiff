"""Tests for envdiff.validator."""

from __future__ import annotations

import pytest

from envdiff.validator import ValidationResult, validate_env


# ---------------------------------------------------------------------------
# ValidationResult helpers
# ---------------------------------------------------------------------------

class TestValidationResult:
    def test_is_valid_when_empty(self):
        result = ValidationResult()
        assert result.is_valid is True

    def test_is_invalid_when_missing_required(self):
        result = ValidationResult(missing_required={"FOO"})
        assert result.is_valid is False

    def test_is_invalid_when_unknown_keys(self):
        result = ValidationResult(unknown_keys={"BAR"})
        assert result.is_valid is False

    def test_is_invalid_when_empty_required(self):
        result = ValidationResult(empty_required={"BAZ"})
        assert result.is_valid is False

    def test_summary_ok(self):
        assert ValidationResult().summary() == "OK"

    def test_summary_missing_required(self):
        result = ValidationResult(missing_required={"KEY"})
        assert "Missing required keys" in result.summary()
        assert "KEY" in result.summary()

    def test_summary_empty_required(self):
        result = ValidationResult(empty_required={"KEY"})
        assert "empty values" in result.summary()

    def test_summary_unknown_keys(self):
        result = ValidationResult(unknown_keys={"EXTRA"})
        assert "Unknown keys" in result.summary()


# ---------------------------------------------------------------------------
# validate_env
# ---------------------------------------------------------------------------

def test_all_required_present_and_non_empty():
    env = {"A": "1", "B": "2"}
    result = validate_env(env, required=["A", "B"])
    assert result.is_valid


def test_missing_required_key_flagged():
    env = {"A": "1"}
    result = validate_env(env, required=["A", "B"])
    assert "B" in result.missing_required
    assert result.is_valid is False


def test_empty_required_value_flagged():
    env = {"A": "", "B": "ok"}
    result = validate_env(env, required=["A", "B"])
    assert "A" in result.empty_required
    assert result.is_valid is False


def test_unknown_keys_ignored_by_default():
    env = {"A": "1", "EXTRA": "x"}
    result = validate_env(env, required=["A"])
    assert result.unknown_keys == set()
    assert result.is_valid


def test_unknown_keys_flagged_when_not_allowed():
    env = {"A": "1", "EXTRA": "x"}
    result = validate_env(env, required=["A"], allow_unknown=False)
    assert "EXTRA" in result.unknown_keys
    assert result.is_valid is False


def test_optional_keys_not_flagged_as_unknown():
    env = {"A": "1", "OPT": "maybe"}
    result = validate_env(env, required=["A"], optional=["OPT"], allow_unknown=False)
    assert result.unknown_keys == set()
    assert result.is_valid


def test_empty_env_with_required_keys():
    result = validate_env({}, required=["X", "Y"])
    assert result.missing_required == {"X", "Y"}


def test_no_schema_all_valid():
    env = {"ANYTHING": "goes"}
    result = validate_env(env)
    assert result.is_valid
