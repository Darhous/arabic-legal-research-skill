from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from legal_research_skill.cli import main
from legal_research_skill.loader import read_json
from legal_research_skill.models import ResearchState, stable_json
from legal_research_skill.pipeline import run_pipeline, validator_names
from legal_research_skill.report import report_to_json
from legal_research_skill.rules import RULES
from legal_research_skill.schema_validation import load_schema, report_errors
from legal_research_skill.validators import (
    HierarchyComplianceValidator,
    OutputClaimsValidator,
    PlanPreservationValidator,
    PriorityResolutionValidator,
    SchemaIntegrityValidator,
)


def _write_state(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _run_cli(root: Path, monkeypatch, capsys, *args: str):
    monkeypatch.chdir(root)
    code = main(list(args))
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _two_level_locked_plan(data: dict) -> dict:
    data["approved_plan"]["status"] = "locked_approved"
    data["approved_plan"]["nodes"] = [
        {
            **data["approved_plan"]["nodes"][0],
            "plan_node_id": "plan-parent",
            "parent_plan_node_id": None,
            "node_type": "part",
            "title": "الأصل",
            "order": 1,
            "locked": True,
        },
        {
            **data["approved_plan"]["nodes"][0],
            "plan_node_id": "plan-child",
            "parent_plan_node_id": "plan-parent",
            "node_type": "chapter",
            "title": "الفرع",
            "order": 2,
            "locked": True,
        },
    ]
    data["body_hierarchy"]["nodes"] = [
        {
            **data["body_hierarchy"]["nodes"][0],
            "heading_id": "heading-parent",
            "parent_heading_id": None,
            "plan_node_id": "plan-parent",
            "level_type": "part",
            "title": "الأصل",
            "order": 1,
        },
        {
            **data["body_hierarchy"]["nodes"][0],
            "heading_id": "heading-child",
            "parent_heading_id": "heading-parent",
            "plan_node_id": "plan-child",
            "level_type": "chapter",
            "title": "الفرع",
            "order": 2,
        },
    ]
    return data


def test_schemas_are_valid_draft_2020_12(root):
    for schema_path in ("schemas/research-state.schema.json", "schemas/validation-report.schema.json"):
        schema = load_schema(str(root / schema_path))
        Draft202012Validator.check_schema(schema)


def test_manifest_is_complete_and_uses_known_rules_and_validators(root, manifest):
    fixture_root = root / "examples" / "fixtures"
    actual = {
        path.relative_to(root).as_posix() for path in fixture_root.rglob("*.json") if path.name != "manifest.json"
    }
    listed = {item["path"] for item in manifest["fixtures"]}
    assert actual == listed
    known_validators = set(validator_names())
    for item in manifest["fixtures"]:
        assert (root / item["path"]).is_file()
        assert set(item["expected_rule_ids"]).issubset(RULES)
        assert set(item["expected_failing_validators"]).issubset(known_validators)
        assert item["expected_overall_decision"] in {"PROCEED", "REVISE", "PAUSE", "FAIL"}


def test_report_schema_rejects_finding_without_rule_id(root):
    report = run_pipeline(root / "examples/fixtures/invalid/unsupported-output-claim.json").to_dict()
    report["findings"][0].pop("rule_id")
    assert report_errors(report)


def test_pipeline_does_not_mutate_original_input(minimal_data, tmp_path):
    before = stable_json(minimal_data)
    run_pipeline(_write_state(tmp_path, minimal_data))
    assert stable_json(minimal_data) == before


def test_json_output_is_byte_deterministic_for_ten_runs(root):
    path = root / "examples/fixtures/invalid/unsupported-output-claim.json"
    outputs = [report_to_json(run_pipeline(path), compact=True) for _ in range(10)]
    assert len(set(outputs)) == 1


def test_duplicate_plan_and_heading_identifiers_are_schema_findings(minimal_data):
    minimal_data["approved_plan"]["nodes"].append(copy.deepcopy(minimal_data["approved_plan"]["nodes"][0]))
    minimal_data["body_hierarchy"]["nodes"].append(copy.deepcopy(minimal_data["body_hierarchy"]["nodes"][0]))
    result = SchemaIntegrityValidator().validate(ResearchState(minimal_data), minimal_data)
    assert sum(finding.code == "duplicate_identifier" for finding in result.findings) == 2


def test_unsupported_schema_version_is_rejected_by_schema_validator(minimal_data):
    minimal_data["schema_version"] = "9.9.9"
    result = SchemaIntegrityValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.rule_id == "SCHEMA-001" for finding in result.findings)


def test_body_hierarchy_parent_cycle_is_detected(minimal_data):
    first = minimal_data["body_hierarchy"]["nodes"][0]
    minimal_data["body_hierarchy"]["nodes"] = [
        {**first, "heading_id": "heading-a", "parent_heading_id": "heading-b", "order": 1},
        {**first, "heading_id": "heading-b", "parent_heading_id": "heading-a", "order": 2},
    ]
    result = HierarchyComplianceValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "hierarchy_parent_cycle" for finding in result.findings)


def test_approved_plan_cycle_and_parent_drift_are_detected(minimal_data):
    data = _two_level_locked_plan(minimal_data)
    data["approved_plan"]["nodes"][0]["parent_plan_node_id"] = "plan-child"
    cycle_result = PlanPreservationValidator().validate(ResearchState(data), data)
    assert any(finding.code == "approved_plan_parent_cycle" for finding in cycle_result.findings)

    drift_data = _two_level_locked_plan(copy.deepcopy(data))
    drift_data["approved_plan"]["nodes"][0]["parent_plan_node_id"] = None
    drift_data["body_hierarchy"]["nodes"][1]["parent_heading_id"] = None
    drift_result = PlanPreservationValidator().validate(ResearchState(drift_data), drift_data)
    assert any(finding.code == "approved_plan_parent_changed" for finding in drift_result.findings)


def test_locked_title_strictness_covers_whitespace_and_arabic_normalization(minimal_data):
    whitespace_data = _two_level_locked_plan(minimal_data)
    whitespace_data["body_hierarchy"]["nodes"][0]["title"] = " الأصل "
    whitespace_result = PlanPreservationValidator().validate(ResearchState(whitespace_data), whitespace_data)
    assert any(finding.code == "approved_plan_title_changed" for finding in whitespace_result.findings)

    normalization_data = _two_level_locked_plan(copy.deepcopy(whitespace_data))
    normalization_data["approved_plan"]["nodes"][0]["title"] = "مسؤولية"
    normalization_data["body_hierarchy"]["nodes"][0]["title"] = "مسؤولية"
    normalization_result = PlanPreservationValidator().validate(ResearchState(normalization_data), normalization_data)
    assert any(finding.code == "approved_plan_title_changed" for finding in normalization_result.findings)


def test_unknown_priority_authority_is_not_silently_accepted(minimal_data):
    minimal_data["instruction_context"]["priority_decisions"][0]["selected_authority_level"] = "future_policy"
    result = PriorityResolutionValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "unknown_priority_authority" for finding in result.findings)


def test_dangerous_output_claim_variants_are_blocked(minimal_data):
    claims = [
        "print ready",
        "DOCX_GENERATED",
        "legal correctness verified",
        "RTL validated",
        "TOC updated",
        "per-page footnote restart verified",
    ]
    minimal_data["output_claims"]["requested"] = claims
    result = OutputClaimsValidator().validate(ResearchState(minimal_data), minimal_data)
    blocked = {finding.evidence["claim"] for finding in result.findings}
    assert {
        "print-ready",
        "docx generated",
        "legal correctness verified",
        "rtl validated",
        "toc updated",
        "per-page footnote restart verified",
    }.issubset(blocked)


def test_gate_readiness_blocks_prior_validator_failures(root):
    report = run_pipeline(root / "examples/fixtures/invalid/unsupported-output-claim.json").to_dict()
    gate = next(result for result in report["validator_results"] if result["validator"] == "gate_readiness")
    assert gate["status"] == "fail"
    assert any(finding["code"] == "prior_validator_blocker" for finding in gate["findings"])


def test_utf8_bom_input_is_supported(minimal_data, tmp_path):
    path = tmp_path / "bom.json"
    path.write_text(json.dumps(minimal_data, ensure_ascii=False), encoding="utf-8-sig")
    assert read_json(path)["task_identifier"] == minimal_data["task_identifier"]


def test_non_utf8_input_is_cli_input_error(root, tmp_path, monkeypatch, capsys):
    path = tmp_path / "latin1.json"
    path.write_bytes('{"schema_version":"0.3.0","task_identifier":"é"}'.encode("latin-1"))
    code, out, _err = _run_cli(root, monkeypatch, capsys, "validate", str(path), "--format", "json")
    assert code == 2
    assert json.loads(out)["error"]["code"] == "input_error"


def test_cli_output_path_traversal_is_rejected(root, monkeypatch, capsys):
    code, _out, err = _run_cli(
        root,
        monkeypatch,
        capsys,
        "validate",
        "examples/fixtures/valid/minimal-valid.json",
        "--output",
        "../phase3-outside.json",
    )
    assert code == 2
    assert "current working directory" in err
