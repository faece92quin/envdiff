"""Tests for envdiff.comparator module."""

import pytest
from envdiff.comparator import compare_envs, DiffResult


BASE = {"APP_NAME": "myapp", "DEBUG": "true", "PORT": "8080", "SECRET": "abc123"}
TARGET = {"APP_NAME": "myapp", "DEBUG": "false", "PORT": "8080", "DATABASE_URL": "postgres://"}


def test_missing_in_target():
    result = compare_envs(BASE, TARGET)
    assert "SECRET" in result.missing_in_target
    assert len(result.missing_in_target) == 1


def test_missing_in_base():
    result = compare_envs(BASE, TARGET)
    assert "DATABASE_URL" in result.missing_in_base
    assert len(result.missing_in_base) == 1


def test_mismatched_values():
    result = compare_envs(BASE, TARGET)
    assert "DEBUG" in result.mismatched
    assert result.mismatched["DEBUG"] == {"base": "true", "target": "false"}


def test_no_mismatch_when_values_equal():
    result = compare_envs(BASE, TARGET)
    assert "PORT" not in result.mismatched
    assert "APP_NAME" not in result.mismatched


def test_ignore_values_flag():
    result = compare_envs(BASE, TARGET, ignore_values=True)
    assert result.mismatched == {}
    assert "SECRET" in result.missing_in_target


def test_identical_envs_no_differences():
    env = {"KEY": "value", "OTHER": "123"}
    result = compare_envs(env, env.copy())
    assert not result.has_differences


def test_empty_envs():
    result = compare_envs({}, {})
    assert not result.has_differences


def test_base_empty_all_missing_in_base():
    result = compare_envs({}, {"FOO": "bar"})
    assert "FOO" in result.missing_in_base
    assert result.missing_in_target == []


def test_target_empty_all_missing_in_target():
    result = compare_envs({"FOO": "bar"}, {})
    assert "FOO" in result.missing_in_target
    assert result.missing_in_base == []


def test_has_differences_true():
    result = compare_envs(BASE, TARGET)
    assert result.has_differences


def test_has_differences_false():
    env = {"A": "1"}
    result = compare_envs(env, env.copy())
    assert not result.has_differences


def test_summary_no_differences():
    env = {"A": "1"}
    result = compare_envs(env, env.copy(), base_name="prod", target_name="staging")
    summary = result.summary()
    assert "No differences found" in summary
    assert "prod" in summary
    assert "staging" in summary


def test_summary_with_differences():
    result = compare_envs(BASE, TARGET, base_name="prod", target_name="staging")
    summary = result.summary()
    assert "SECRET" in summary
    assert "DATABASE_URL" in summary
    assert "DEBUG" in summary


def test_none_values_mismatch():
    base = {"KEY": None}
    target = {"KEY": "value"}
    result = compare_envs(base, target)
    assert "KEY" in result.mismatched
    assert result.mismatched["KEY"] == {"base": None, "target": "value"}


def test_custom_names_in_result():
    result = compare_envs({}, {}, base_name="env.prod", target_name="env.dev")
    assert result.base_name == "env.prod"
    assert result.target_name == "env.dev"
