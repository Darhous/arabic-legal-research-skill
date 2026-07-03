from __future__ import annotations

import json

import pytest

from legal_research_skill.cli import main
from legal_research_skill.errors import SchemaValidationError
from legal_research_skill.loader import load_state
from legal_research_skill.pipeline import run_pipeline


def run_cli(root, monkeypatch, capsys, *args):
    monkeypatch.chdir(root)
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


@pytest.mark.parametrize("bad_version", ["0.2.0", "0.4.0", "9.9.9", "", "abc"])
def test_load_state_rejects_every_unsupported_version(root, tmp_path, minimal_data, bad_version):
    data = dict(minimal_data)
    data["schema_version"] = bad_version
    scratch = tmp_path / "input.json"
    scratch.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SchemaValidationError):
        load_state(scratch)


def test_load_state_rejects_missing_version_field(root, tmp_path, minimal_data):
    data = dict(minimal_data)
    del data["schema_version"]
    scratch = tmp_path / "input.json"
    scratch.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SchemaValidationError):
        load_state(scratch)


def test_load_state_accepts_the_supported_version(root, tmp_path, minimal_data):
    assert minimal_data["schema_version"] == "0.3.0"
    scratch = tmp_path / "input.json"
    scratch.write_text(json.dumps(minimal_data, ensure_ascii=False), encoding="utf-8")
    state = load_state(scratch)
    assert state.data["schema_version"] == "0.3.0"


@pytest.mark.parametrize("bad_version", ["0.2.0", "9.9.9"])
def test_pipeline_reports_unsupported_version_as_schema_finding_not_a_raised_exception(
    root, tmp_path, minimal_data, bad_version
):
    # run_pipeline (the CLI's real, active validation path) surfaces an
    # unsupported schema_version as a structured SCHEMA-001 finding in the
    # ValidationReport, rather than raising -- this is the single active
    # version-validation mechanism (the JSON Schema's const constraint on
    # schema_version), exercised the same way load_state exercises it.
    data = dict(minimal_data)
    data["schema_version"] = bad_version
    scratch = tmp_path / "input.json"
    scratch.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    report = run_pipeline(scratch)
    schema_result = next(result for result in report.validator_results if result.validator == "schema_integrity")
    assert schema_result.status.value == "fail"
    assert any(finding.rule_id == "SCHEMA-001" for finding in schema_result.findings)


def test_cli_schema_check_rejects_unsupported_version(root, monkeypatch, capsys, tmp_path, minimal_data):
    data = dict(minimal_data)
    data["schema_version"] = "9.9.9"
    scratch = tmp_path / "input.json"
    scratch.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    code, out, _err = run_cli(tmp_path, monkeypatch, capsys, "schema-check", str(scratch), "--format", "json")
    assert code == 1
    payload = json.loads(out)
    assert payload["schema_valid"] is False
    assert any("0.3.0" in error or "9.9.9" in error for error in payload["errors"])
