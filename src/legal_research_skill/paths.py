from __future__ import annotations

import os
from pathlib import Path

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def resolve_confined_path(path: Path, *, root: Path | None = None) -> Path:
    """Resolve ``path`` and confirm it stays within ``root`` (default: cwd).

    Raises ValueError if the resolved path escapes the confinement root or
    uses a reserved Windows device name. Callers should translate ValueError
    into their own domain-specific exception type.
    """
    confinement_root = (root or Path.cwd()).resolve()
    resolved = path.resolve()
    if resolved != confinement_root and confinement_root not in resolved.parents:
        raise ValueError("Path must stay within the current working directory.")
    if resolved.stem.upper() in WINDOWS_RESERVED_NAMES:
        raise ValueError("Path uses a reserved Windows device name.")
    return resolved


def has_extension(path: Path, extension: str) -> bool:
    """Case-insensitive suffix check (".DOCX" matches ".docx")."""
    return path.suffix.lower() == extension.lower()


def is_same_file_target(first: Path, second: Path) -> bool:
    """Return True if ``first`` and ``second`` would refer to the same file.

    Two independent checks are combined:

    - Resolved-path equality catches exact matches, symlink aliases, and
      case-only aliases (``pathlib.WindowsPath`` equality is already
      case-insensitive on Windows -- e.g. ``Path("A.json") ==
      Path("a.json")`` -- regardless of whether either path exists yet, so
      no separate casefold comparison is needed on this platform).
    - ``os.path.samefile`` catches hardlink aliases (two distinct paths
      pointing at the same inode) once both paths exist on disk.
    """
    resolved_first = first.resolve()
    resolved_second = second.resolve()
    if resolved_first == resolved_second:
        return True
    if resolved_first.exists() and resolved_second.exists():
        try:
            if os.path.samefile(resolved_first, resolved_second):
                return True
        except OSError:
            pass
    return False


__all__ = ["WINDOWS_RESERVED_NAMES", "is_same_file_target", "resolve_confined_path"]
