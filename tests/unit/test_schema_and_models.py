from __future__ import annotations

import json

import pytest

from legal_research_skill.loader import load_state, read_json
from legal_research_skill.models import ResearchState, stable_json
from legal_research_skill.schema_validation import (
    artifact_manifest_errors,
    load_schema,
    report_errors,
    research_state_errors,
)


def test_schemas_load(root):
    research_schema = load_schema(str(root / "schemas" / "research-state.schema.json"))
    report_schema = load_schema(str(root / "schemas" / "validation-report.schema.json"))
    manifest_schema = load_schema(str(root / "schemas" / "artifact-manifest.schema.json"))
    assert research_schema["$schema"].endswith("2020-12/schema")
    assert report_schema["$id"].startswith("urn:arabic-legal-research-skill")
    assert manifest_schema["$schema"].endswith("2020-12/schema")


def test_valid_fixtures_pass_schema(root, manifest):
    for item in manifest["fixtures"]:
        if not item["expected_schema_valid"]:
            continue
        data = json.loads((root / item["path"]).read_text(encoding="utf-8"))
        assert research_state_errors(data) == []


def test_malformed_schema_fixture_fails(root):
    data = json.loads((root / "examples/fixtures/invalid/malformed-schema.json").read_text(encoding="utf-8"))
    errors = research_state_errors(data)
    assert errors
    assert any("0.3.0" in error or "pattern" in error for error in errors)


def test_unknown_field_fails_schema(minimal_data):
    minimal_data["unknown"] = "not allowed"
    assert any("Additional properties" in error for error in research_state_errors(minimal_data))


def test_bad_enum_fails_schema(minimal_data):
    minimal_data["language"]["direction"] = "SIDEWAYS"
    assert any("'SIDEWAYS' is not one of" in error for error in research_state_errors(minimal_data))


def test_arabic_text_survives_model_round_trip(root):
    state = load_state(root / "examples/fixtures/valid/minimal-valid.json")
    serialized = state.serialize()
    assert serialized["research_metadata"]["research_title"]["value"] == "الحماية القانونية للبيانات الشخصية"
    assert json.loads(stable_json(serialized)) == serialized


def test_read_json_rejects_non_object(tmp_path):
    path = tmp_path / "array.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(Exception, match="JSON object"):
        read_json(path)


def test_model_index_preserves_ids(minimal_data):
    state = ResearchState(minimal_data)
    assert state.index("sources", "source_id")["src-law-1"]["title"] == "قانون حماية البيانات الشخصية"


def test_report_schema_rejects_missing_required_field():
    assert report_errors({"report_schema_version": "0.3.0"})


def test_artifact_manifest_schema_rejects_missing_required_field():
    assert artifact_manifest_errors({"manifest_schema_version": "0.4.0"})
