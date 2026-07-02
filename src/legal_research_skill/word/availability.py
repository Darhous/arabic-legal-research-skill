from __future__ import annotations

import importlib
import platform
from contextlib import suppress
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class WordAvailability:
    is_windows: bool
    com_available: bool
    word_available: bool
    version: str | None = None
    error: str | None = None

    @property
    def status(self) -> str:
        return "AVAILABLE" if self.word_available else "NOT_AVAILABLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "is_windows": self.is_windows,
            "com_available": self.com_available,
            "word_available": self.word_available,
            "version": self.version,
            "error": self.error,
        }


def detect_word_availability() -> WordAvailability:
    is_windows = platform.system().lower() == "windows"
    if not is_windows:
        return WordAvailability(False, False, False, error="Microsoft Word COM automation requires Windows.")
    try:
        client = importlib.import_module("win32com.client")
    except ImportError as exc:
        return WordAvailability(True, False, False, error=f"win32com.client is not importable: {exc}")
    app = None
    try:
        app = client.DispatchEx("Word.Application")
        version = str(getattr(app, "Version", "") or "")
        return WordAvailability(True, True, True, version=version or None)
    except Exception as exc:  # pragma: no cover - depends on host COM state
        return WordAvailability(True, True, False, error=str(exc))
    finally:
        if app is not None:
            with suppress(Exception):
                app.Quit()
