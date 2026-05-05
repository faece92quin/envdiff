"""Tests for envdiff.loader module."""

from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.loader import (
    EnvFile,
    EnvLoadError,
    discover_env_files,
    load_env_file,
    load_env_files,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# load_env_file
# ---------------------------------------------------------------------------

def test_load_env_file_basic(tmp_path: Path) -> None:
    p = _write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    env = load_env_file(p)
    assert isinstance(env, EnvFile)
    assert env.data == {"FOO": "bar", "BAZ": "qux"}
    assert env.name == ".env"


def test_load_env_file_quoted_values(tmp_path: Path) -> None:
    p = _write(tmp_path, ".env.prod", 'SECRET="hello world"\n')
    env = load_env_file(p)
    assert env.data["SECRET"] == "hello world"


def test_load_env_file_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(EnvLoadError, match="File not found"):
        load_env_file(tmp_path / "nonexistent.env")


def test_load_env_file_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(EnvLoadError, match="not a file"):
        load_env_file(tmp_path)


def test_load_env_file_accepts_string_path(tmp_path: Path) -> None:
    p = _write(tmp_path, ".env", "KEY=value\n")
    env = load_env_file(str(p))
    assert env.data == {"KEY": "value"}


# ---------------------------------------------------------------------------
# load_env_files
# ---------------------------------------------------------------------------

def test_load_env_files_returns_ordered_list(tmp_path: Path) -> None:
    p1 = _write(tmp_path, ".env", "A=1\n")
    p2 = _write(tmp_path, ".env.staging", "B=2\n")
    envs = load_env_files([p1, p2])
    assert len(envs) == 2
    assert envs[0].data == {"A": "1"}
    assert envs[1].data == {"B": "2"}


def test_load_env_files_propagates_error(tmp_path: Path) -> None:
    p1 = _write(tmp_path, ".env", "A=1\n")
    with pytest.raises(EnvLoadError):
        load_env_files([p1, tmp_path / "missing.env"])


# ---------------------------------------------------------------------------
# discover_env_files
# ---------------------------------------------------------------------------

def test_discover_env_files_finds_all(tmp_path: Path) -> None:
    _write(tmp_path, ".env", "A=1\n")
    _write(tmp_path, ".env.production", "A=2\n")
    _write(tmp_path, ".env.staging", "A=3\n")
    envs = discover_env_files(tmp_path)
    names = [e.name for e in envs]
    assert ".env" in names
    assert ".env.production" in names
    assert ".env.staging" in names


def test_discover_env_files_excludes(tmp_path: Path) -> None:
    _write(tmp_path, ".env", "A=1\n")
    _write(tmp_path, ".env.example", "A=changeme\n")
    envs = discover_env_files(tmp_path, exclude=[".env.example"])
    names = [e.name for e in envs]
    assert ".env.example" not in names
    assert ".env" in names


def test_discover_env_files_ignores_directories(tmp_path: Path) -> None:
    (tmp_path / ".env.d").mkdir()
    _write(tmp_path, ".env", "X=1\n")
    envs = discover_env_files(tmp_path)
    assert all(e.path.is_file() for e in envs)


def test_discover_env_files_empty_directory(tmp_path: Path) -> None:
    envs = discover_env_files(tmp_path)
    assert envs == []
