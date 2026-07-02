from __future__ import annotations

import json

from legal_research_skill.cli import main


def run_cli(root, monkeypatch, capsys, *args):
    monkeypatch.chdir(root)
    try:
        code = main(list(args))
    except SystemExit as exc:
        code = int(exc.code)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_help(root, monkeypatch, capsys):
    code, out, _err = run_cli(root, monkeypatch, capsys, "--help")
    assert code == 0
    assert "validate" in out


def test_valid_input_text(root, monkeypatch, capsys):
    code, out, _err = run_cli(
        root, monkeypatch, capsys, "validate", "examples/fixtures/valid/minimal-valid.json", "--format", "text"
    )
    assert code == 0
    assert "Overall decision: PROCEED" in out


def test_invalid_input_json(root, monkeypatch, capsys):
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "validate",
        "examples/fixtures/invalid/unsupported-output-claim.json",
        "--format",
        "json",
    )
    assert code == 1
    data = json.loads(out)
    assert data["overall_decision"] == "FAIL"
    assert any(finding["rule_id"] == "CLAIM-001" for finding in data["findings"])


def test_output_file_and_compact(root, monkeypatch, capsys):
    output = root / "tests_tmp" / "report.json"
    output.unlink(missing_ok=True)
    code, out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "validate",
        "examples/fixtures/valid/minimal-valid.json",
        "--format",
        "json",
        "--compact",
        "--output",
        str(output),
    )
    assert code == 0
    assert out == ""
    assert json.loads(output.read_text(encoding="utf-8"))["overall_status"] == "pass"
    output.unlink(missing_ok=True)


def test_validator_selection_exclusion_and_threshold(root, monkeypatch, capsys):
    selected_code, _out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "validate",
        "examples/fixtures/invalid/unsupported-output-claim.json",
        "--validator",
        "output_claims",
        "--format",
        "json",
        "--fail-on",
        "critical",
    )
    assert selected_code == 1
    excluded_code, _out, _err = run_cli(
        root,
        monkeypatch,
        capsys,
        "validate",
        "examples/fixtures/invalid/unsupported-output-claim.json",
        "--exclude-validator",
        "output_claims",
        "--fail-on",
        "critical",
    )
    assert excluded_code == 0


def test_list_validators_and_explain(root, monkeypatch, capsys):
    code, out, _err = run_cli(root, monkeypatch, capsys, "list-validators")
    assert code == 0
    assert "schema_integrity" in out
    code, out, _err = run_cli(root, monkeypatch, capsys, "explain", "PLAN-001")
    assert code == 0
    assert "Approved plan headings" in out


def test_schema_check(root, monkeypatch, capsys):
    code, _out, _err = run_cli(root, monkeypatch, capsys, "schema-check", "examples/fixtures/valid/minimal-valid.json")
    assert code == 0
    code, out, _err = run_cli(
        root, monkeypatch, capsys, "schema-check", "examples/fixtures/invalid/malformed-schema.json", "--format", "json"
    )
    assert code == 1
    assert json.loads(out)["schema_valid"] is False


def test_unknown_validator_missing_file_and_malformed_json(root, tmp_path, monkeypatch, capsys):
    code, _out, _err = run_cli(
        root, monkeypatch, capsys, "validate", "examples/fixtures/valid/minimal-valid.json", "--validator", "nope"
    )
    assert code == 2
    code, _out, _err = run_cli(root, monkeypatch, capsys, "validate", "missing.json")
    assert code == 2
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{", encoding="utf-8")
    code, out, _err = run_cli(root, monkeypatch, capsys, "validate", str(bad_json), "--format", "json")
    assert code == 2
    assert json.loads(out)["error"]["code"] == "input_error"


def test_explain_unknown_rule(root, monkeypatch, capsys):
    code, out, _err = run_cli(root, monkeypatch, capsys, "explain", "NOPE-001")
    assert code == 2
    assert "Unknown rule ID" in out
