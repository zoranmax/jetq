"""Bump project version (patch) across versioned files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PYPROJECT = ROOT / "pyproject.toml"
SETUP_PY = ROOT / "setup.py"
INIT_PY = ROOT / "jetq" / "__init__.py"

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _bump_patch(version: str) -> str:
    match = VERSION_RE.match(version)
    if not match:
        raise ValueError(f"Unsupported version format: {version}")
    major, minor, patch = (int(part) for part in match.groups())
    return f"{major}.{minor}.{patch + 1}"


def _update_pyproject(version: str) -> str:
    content = _read_text(PYPROJECT)
    updated, count = re.subn(
        r"^version\s*=\s*\"[^\"]+\"$",
        f'version = "{version}"',
        content,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("Failed to update pyproject.toml version")
    _write_text(PYPROJECT, updated)
    return version


def _update_setup_py(version: str) -> None:
    content = _read_text(SETUP_PY)
    updated, count = re.subn(
        r"^\s*version=\"[^\"]+\"",
        f'    version="{version}"',
        content,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("Failed to update setup.py version")
    _write_text(SETUP_PY, updated)


def _update_init_py(version: str) -> None:
    content = _read_text(INIT_PY)
    updated, count = re.subn(
        r"^__version__\s*=\s*\"[^\"]+\"$",
        f'__version__ = "{version}"',
        content,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError("Failed to update jetq/__init__.py version")
    _write_text(INIT_PY, updated)


def main() -> None:
    pyproject = _read_text(PYPROJECT)
    version_match = re.search(
        r"^version\s*=\s*\"([^\"]+)\"$", pyproject, flags=re.MULTILINE
    )
    if not version_match:
        raise ValueError("Version not found in pyproject.toml")

    current = version_match.group(1)
    next_version = _bump_patch(current)

    _update_pyproject(next_version)
    _update_setup_py(next_version)
    _update_init_py(next_version)

    print(f"Bumped version: {current} -> {next_version}")


if __name__ == "__main__":
    main()
