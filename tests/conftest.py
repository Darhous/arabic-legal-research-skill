from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
MINIMAL = ROOT / "examples" / "fixtures" / "valid" / "minimal-valid.json"
MANIFEST = ROOT / "examples" / "fixtures" / "manifest.json"


@pytest.fixture
def root() -> Path:
    return ROOT


@pytest.fixture
def minimal_data() -> dict[str, Any]:
    return json.loads(MINIMAL.read_text(encoding="utf-8"))


@pytest.fixture
def manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def cloned(data: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(data)
