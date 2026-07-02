from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from legal_research_skill.constants import RESEARCH_STATE_SCHEMA, VALIDATION_REPORT_SCHEMA


def load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=4)
def load_schema(path: str) -> dict[str, Any]:
    return load_json_file(Path(path))


@lru_cache(maxsize=4)
def compiled_validator(path: str) -> Draft202012Validator:
    schema = load_schema(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def research_state_errors(data: Any) -> list[str]:
    validator = compiled_validator(str(RESEARCH_STATE_SCHEMA))
    return sorted(error.message for error in validator.iter_errors(data))


def report_errors(data: Any) -> list[str]:
    validator = compiled_validator(str(VALIDATION_REPORT_SCHEMA))
    return sorted(error.message for error in validator.iter_errors(data))
