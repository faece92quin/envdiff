"""Tests for envdiff.parser module."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, _parse_value


# ---------------------------------------------------------------------------
# _parse_value unit tests
# ---------------------------------------------------------------------------

def test_parse_value_plain():
    assert _parse_value("hello") == "hello"


def test_parse_value_double_quoted():
    assert _parse_value('"hello world"') == "hello world"


def test_parse_value_single_quoted():
    assert _parse_value("'hello world'") == "hello world"


def test_parse_value_empty():
    assert _parse_value("") == ""


def test_parse_value_inline_comment():
    assert _parse_value("myvalue #comment") == "myvalue"


def test_parse_value_no_strip_quoted_comment():
    # Inline comment inside quotes should be preserved
    assert _parse_value('"value #not a comment"') == "value #not a comment"


# ---------------------------------------------------------------------------
# parse_env_file integration tests
# ---------------------------------------------------------------------------

@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    content = """
# This is a comment
APP_NAME=MyApp
DEBUG=true
DB_PASSWORD="s3cr3t"
EMPTY_VAR=
SPACED_VALUE=hello world # inline comment
SINGLE_QUOTED='single'
"""
    env_path = tmp_path / ".env"
    env_path.write_text(content, encoding="utf-8")
    return env_path


def test_parse_basic_keys(env_file):
    result = parse_env_file(env_file)
    assert "APP_NAME" in result
    assert "DEBUG" in result
    assert "DB_PASSWORD" in result


def test_parse_plain_value(env_file):
    result = parse_env_file(env_file)
    assert result["APP_NAME"] == "MyApp"
    assert result["DEBUG"] == "true"


def test_parse_double_quoted_value(env_file):
    result = parse_env_file(env_file)
    assert result["DB_PASSWORD"] == "s3cr3t"


def test_parse_single_quoted_value(env_file):
    result = parse_env_file(env_file)
    assert result["SINGLE_QUOTED"] == "single"


def test_parse_empty_value(env_file):
    result = parse_env_file(env_file)
    assert result["EMPTY_VAR"] == ""


def test_parse_inline_comment_stripped(env_file):
    result = parse_env_file(env_file)
    assert result["SPACED_VALUE"] == "hello world"


def test_comments_excluded(env_file):
    result = parse_env_file(env_file)
    for key in result:
        assert not key.startswith("#")


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/path/.env")
