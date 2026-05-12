"""Tests for envdiff.redactor."""

from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.redactor import (
    REDACTED,
    _compile_patterns,
    is_sensitive,
    redact_result,
    redact_value,
)


# ---------------------------------------------------------------------------
# is_sensitive
# ---------------------------------------------------------------------------

class TestIsSensitive:
    def _patterns(self, *raw: str):
        return _compile_patterns(raw)

    def test_password_key_is_sensitive(self):
        assert is_sensitive("DB_PASSWORD", self._patterns(r"password"))

    def test_non_sensitive_key_is_not_sensitive(self):
        assert not is_sensitive("APP_ENV", self._patterns(r"password", r"secret"))

    def test_case_insensitive_match(self):
        assert is_sensitive("AWS_Secret_Key", self._patterns(r"secret"))

    def test_token_in_middle_of_key(self):
        assert is_sensitive("GITHUB_TOKEN_VALUE", self._patterns(r"token"))


# ---------------------------------------------------------------------------
# redact_value
# ---------------------------------------------------------------------------

class TestRedactValue:
    def _patterns(self, *raw: str):
        return _compile_patterns(raw)

    def test_sensitive_key_returns_placeholder(self):
        result = redact_value("API_KEY", "supersecret", self._patterns(r"api[_\-]?key"))
        assert result == REDACTED

    def test_non_sensitive_key_returns_original(self):
        result = redact_value("APP_ENV", "production", self._patterns(r"secret"))
        assert result == "production"


# ---------------------------------------------------------------------------
# redact_result
# ---------------------------------------------------------------------------

def _make_result(**kwargs) -> DiffResult:
    defaults = dict(missing_in_target={}, missing_in_base={}, mismatched={})
    defaults.update(kwargs)
    return DiffResult(**defaults)


class TestRedactResult:
    def test_non_sensitive_values_unchanged(self):
        r = _make_result(missing_in_target={"APP_ENV": "production"})
        out = redact_result(r)
        assert out.missing_in_target["APP_ENV"] == "production"

    def test_password_in_missing_target_is_redacted(self):
        r = _make_result(missing_in_target={"DB_PASSWORD": "hunter2"})
        out = redact_result(r)
        assert out.missing_in_target["DB_PASSWORD"] == REDACTED

    def test_secret_in_missing_base_is_redacted(self):
        r = _make_result(missing_in_base={"APP_SECRET": "abc123"})
        out = redact_result(r)
        assert out.missing_in_base["APP_SECRET"] == REDACTED

    def test_mismatched_both_values_redacted_for_sensitive_key(self):
        r = _make_result(mismatched={"AUTH_TOKEN": ("old", "new")})
        out = redact_result(r)
        assert out.mismatched["AUTH_TOKEN"] == (REDACTED, REDACTED)

    def test_mismatched_non_sensitive_values_unchanged(self):
        r = _make_result(mismatched={"LOG_LEVEL": ("debug", "info")})
        out = redact_result(r)
        assert out.mismatched["LOG_LEVEL"] == ("debug", "info")

    def test_extra_patterns_applied(self):
        r = _make_result(missing_in_target={"INTERNAL_CERT": "pem-data"})
        out = redact_result(r, extra_patterns=[r"cert"])
        assert out.missing_in_target["INTERNAL_CERT"] == REDACTED

    def test_original_result_not_mutated(self):
        r = _make_result(missing_in_target={"DB_PASSWORD": "hunter2"})
        redact_result(r)
        assert r.missing_in_target["DB_PASSWORD"] == "hunter2"
