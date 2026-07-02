from __future__ import annotations

import json

from legal_research_skill.pipeline import run_pipeline
from legal_research_skill.report import report_to_json
from legal_research_skill.schema_validation import report_errors, research_state_errors


def test_all_manifest_fixtures_match_expectations(root, manifest):
    for item in manifest["fixtures"]:
        path = root / item["path"]
        data = json.loads(path.read_text(encoding="utf-8"))
        assert (research_state_errors(data) == []) is item["expected_schema_valid"]
        report = run_pipeline(path)
        report_data = report.to_dict()
        assert report_errors(report_data) == []
        assert report_data["overall_decision"] == item["expected_overall_decision"]
        failing = {result["validator"] for result in report_data["validator_results"] if result["status"] == "fail"}
        assert set(item["expected_failing_validators"]).issubset(failing)
        rule_ids = {finding["rule_id"] for finding in report_data["findings"]}
        assert set(item["expected_rule_ids"]).issubset(rule_ids)
        assert len(report_data["findings"]) >= item["expected_minimum_finding_count"]
        assert not (set(item["forbidden_findings"]) & rule_ids)


def test_reports_are_deterministic(root):
    path = root / "examples/fixtures/invalid/unsupported-output-claim.json"
    first = report_to_json(run_pipeline(path), compact=True)
    second = report_to_json(run_pipeline(path), compact=True)
    assert first == second


def test_validator_selection_and_exclusion(root):
    path = root / "examples/fixtures/invalid/unsupported-output-claim.json"
    selected = run_pipeline(path, only=("output_claims",)).to_dict()
    assert "output_claims" in selected["executed_validators"]
    assert any(item["validator"] == "cross_reference" for item in selected["skipped_validators"])

    excluded = run_pipeline(path, exclude=("output_claims",)).to_dict()
    assert "CLAIM-001" not in {finding["rule_id"] for finding in excluded["findings"]}
