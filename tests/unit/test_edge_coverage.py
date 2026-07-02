from __future__ import annotations

import pytest

from legal_research_skill.loader import MAX_INPUT_BYTES, load_state, read_json
from legal_research_skill.models import ResearchState
from legal_research_skill.pipeline import available_validators, run_pipeline, validator_names
from legal_research_skill.report import error_payload, report_to_json, report_to_text
from legal_research_skill.validators import (
    BibliographyCompletenessValidator,
    CitationStatusValidator,
    CrossReferenceValidator,
    FootnoteLinkageValidator,
    GateReadinessValidator,
    HierarchyComplianceValidator,
    MethodologyCompletenessValidator,
    OutputClaimsValidator,
    PlanPreservationValidator,
    PriorityResolutionValidator,
    VerificationMarkerValidator,
)


def test_loader_rejects_directory_and_oversize(root, tmp_path, monkeypatch):
    with pytest.raises(Exception, match="not a file"):
        read_json(root / "examples")
    path = tmp_path / "big.json"
    path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("legal_research_skill.loader.MAX_INPUT_BYTES", 1)
    with pytest.raises(Exception, match="exceeds"):
        read_json(path)
    monkeypatch.setattr("legal_research_skill.loader.MAX_INPUT_BYTES", MAX_INPUT_BYTES)


def test_loader_schema_validation_error(root):
    with pytest.raises(Exception, match=r"0\.3\.0|pattern"):
        load_state(root / "examples/fixtures/invalid/malformed-schema.json")


def test_report_compact_and_findings(root):
    report = run_pipeline(root / "examples/fixtures/invalid/unsupported-output-claim.json")
    assert "\n  " not in report_to_json(report, compact=True)
    text = report_to_text(report, show_passed=True, compact=False)
    assert "Findings:" in text
    compact = report_to_text(report, compact=True)
    assert "Validators:" not in compact
    assert error_payload("x", code="c") == {"error": {"code": "c", "message": "x"}}


def test_registry_helpers():
    names = validator_names()
    assert names[0] == "schema_integrity"
    assert len(available_validators()) == len(names)


def test_cross_reference_all_dangling_types(minimal_data):
    minimal_data["citations"][0]["marker_id"] = "missing-marker"
    minimal_data["footnotes"][0]["citation_ids"] = ["missing-citation"]
    minimal_data["bibliography"][0]["source_ids"] = ["missing-source"]
    minimal_data["body_hierarchy"]["nodes"][0]["plan_node_id"] = "missing-plan"
    minimal_data["body_hierarchy"]["nodes"][0]["parent_heading_id"] = "missing-heading"
    minimal_data["reviewer_results"][0]["affected_entity_type"] = "citation"
    minimal_data["reviewer_results"][0]["affected_entity_id"] = "missing-citation"
    result = CrossReferenceValidator().validate(ResearchState(minimal_data), minimal_data)
    assert len(result.findings) >= 5


def test_citation_missing_source_and_exclusive_cases(minimal_data):
    minimal_data["source_restrictions"]["mandatory_missing_files"] = ["mandatory.pdf"]
    minimal_data["source_restrictions"]["exclusive_source_ids"] = ["src-exclusive"]
    minimal_data["citations"].append(
        dict(minimal_data["citations"][0], citation_id="cite-missing", source_id="missing")
    )
    result = CitationStatusValidator().validate(ResearchState(minimal_data), minimal_data)
    codes = {finding.code for finding in result.findings}
    assert "mandatory_exclusive_file_missing" in codes
    assert "exclusive_source_bypassed" in codes


def test_unverifiable_source_blocks_verified_citation(minimal_data):
    minimal_data["sources"][0]["verification_status"] = "unverifiable"
    minimal_data["citations"][0]["verification_status"] = "verified"
    result = CitationStatusValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "citation_stronger_than_source" for finding in result.findings)


def test_footnote_per_page_warning(minimal_data):
    minimal_data["footnotes"][0]["numbering_intent"] = "per_page_restart"
    result = FootnoteLinkageValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.status == "warning" for finding in result.findings)


def test_bibliography_duplicate_and_stronger_than_source(minimal_data):
    minimal_data["bibliography"].append(dict(minimal_data["bibliography"][0], bibliography_id="bib-2"))
    minimal_data["sources"][0]["verification_status"] = "requires_verification"
    minimal_data["bibliography"][0]["verification_status"] = "verified"
    result = BibliographyCompletenessValidator().validate(ResearchState(minimal_data), minimal_data)
    codes = {finding.code for finding in result.findings}
    assert "duplicate_bibliography_entry" in codes
    assert "bibliography_stronger_than_source" in codes


def test_hierarchy_parent_child_level_invalid(minimal_data):
    minimal_data["body_hierarchy"]["nodes"].append(
        {
            "heading_id": "heading-demand-1",
            "parent_heading_id": "heading-part-1",
            "plan_node_id": None,
            "level_type": "demand",
            "display_label": "مطلب",
            "title": "قفزة مستوى",
            "order": 2,
        }
    )
    result = HierarchyComplianceValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "invalid_parent_child_level" for finding in result.findings)


def test_methodology_missing_title_component_and_bad_conclusion(minimal_data):
    minimal_data["research_metadata"]["research_title"] = {"status": "Missing", "value": None}
    minimal_data["methodology"]["components"].pop("tools")
    minimal_data["methodology"]["conclusion"]["summary"]["content"] = "..."
    result = MethodologyCompletenessValidator().validate(ResearchState(minimal_data), minimal_data)
    codes = {finding.code for finding in result.findings}
    assert "missing_research_title" in codes
    assert "methodology_component_incomplete" in codes


def test_plan_edge_cases(minimal_data):
    minimal_data["approved_plan"]["status"] = "locked_approved"
    minimal_data["approved_plan"]["nodes"][0]["omitted"] = True
    minimal_data["approved_plan"]["nodes"][0]["omission_reason"] = None
    minimal_data["body_hierarchy"]["nodes"][0]["plan_node_id"] = None
    result = PlanPreservationValidator().validate(ResearchState(minimal_data), minimal_data)
    codes = {finding.code for finding in result.findings}
    assert "missing_omission_reason" in codes or "unauthorized_extra_heading" in codes


def test_proposed_plan_locked_and_level_changed(minimal_data):
    minimal_data["approved_plan"]["nodes"][0]["locked"] = True
    proposed = PlanPreservationValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "proposed_plan_locked" for finding in proposed.findings)
    minimal_data["approved_plan"]["status"] = "locked_approved"
    minimal_data["approved_plan"]["nodes"][0]["locked"] = True
    minimal_data["body_hierarchy"]["nodes"][0]["level_type"] = "chapter"
    changed = PlanPreservationValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "approved_plan_level_changed" for finding in changed.findings)


def test_priority_missing_data_and_unknown_level(minimal_data):
    decision = minimal_data["instruction_context"]["priority_decisions"][0]
    decision["specificity_recorded"] = False
    decision["selected_authority_level"] = "unknown-custom"
    result = PriorityResolutionValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "incomplete_priority_record" for finding in result.findings)


def test_marker_missing_lifecycle_field(minimal_data):
    minimal_data["verification_markers"].append(
        {
            "marker_id": "marker-missing-field",
            "marker_text": "Requires Verification",
            "target_type": "source",
            "target_id": "src-law-1",
            "reason": "",
            "created_by": "",
            "removal_authority": "",
            "status": "open",
            "resolution_evidence": None,
            "arabic_disclosure": "تتطلب هذه الإحالة تحققًا إضافيًا.",
        }
    )
    result = VerificationMarkerValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "marker_lifecycle_field_missing" for finding in result.findings)


def test_output_claim_unknown_validated_phrase(minimal_data):
    minimal_data["output_claims"]["requested"] = ["fully validated"]
    result = OutputClaimsValidator().validate(ResearchState(minimal_data), minimal_data)
    assert any(finding.code == "unsupported_output_claim" for finding in result.findings)


def test_gate_blocked_and_rerun(minimal_data):
    minimal_data["state_machine"]["gates"][0]["status"] = "blocked"
    minimal_data["state_machine"]["gates"][0]["blockers"] = ["Need user decision"]
    minimal_data["state_machine"]["rerun_required"] = True
    result = GateReadinessValidator().validate(ResearchState(minimal_data), minimal_data)
    codes = {finding.code for finding in result.findings}
    assert {"gate_blocked", "rerun_required"}.issubset(codes)


def test_pipeline_unknown_validator(root):
    with pytest.raises(Exception, match="Unknown validator"):
        run_pipeline(root / "examples/fixtures/valid/minimal-valid.json", only=("missing-validator",))


def test_pipeline_report_schema_guard(root, monkeypatch):
    monkeypatch.setattr("legal_research_skill.pipeline.report_errors", lambda data: ["bad report"])
    with pytest.raises(RuntimeError, match="Generated validation report"):
        run_pipeline(root / "examples/fixtures/valid/minimal-valid.json")
