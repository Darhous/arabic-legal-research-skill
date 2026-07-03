from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from legal_research_skill.errors import InputError, SchemaValidationError
from legal_research_skill.models import ResearchState
from legal_research_skill.schema_validation import research_state_errors

MAX_INPUT_BYTES = 5_000_000


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise InputError(f"Input file does not exist: {path}")
    if not path.is_file():
        raise InputError(f"Input path is not a file: {path}")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise InputError(f"Input file exceeds {MAX_INPUT_BYTES} bytes.")
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError("Input file must be valid UTF-8 JSON.") from exc
    except OSError as exc:
        raise InputError(f"Cannot read input file: {path}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"Malformed JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise InputError("Research state input must be a JSON object.")
    return data


def load_state(path: Path) -> ResearchState:
    """Read, schema-validate (including schema_version), and wrap a research state file.

    Schema compliance -- including the supported ``schema_version`` -- is
    enforced exclusively by the JSON Schema's ``const`` constraint on that
    field, checked here via research_state_errors(). This is the single,
    authoritative version-validation path in the codebase (also used by
    SchemaIntegrityValidator/run_pipeline for the CLI's structured-report
    flow); do not reintroduce a second, hand-rolled version comparison here.
    """
    data = read_json(path)
    errors = research_state_errors(data)
    if errors:
        raise SchemaValidationError("; ".join(errors))
    return ResearchState(data)
