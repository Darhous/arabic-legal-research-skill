from __future__ import annotations

from legal_research_skill.models import ResearchState, stable_json
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


def _rule_ids(result):
    return {finding.rule_id for finding in result.findings}


def test_validators_do_not_mutate_input(minimal_data):
    before = stable_json(minimal_data)
    state = ResearchState(minimal_data)
    for validator in (
        CrossReferenceValidator(),
        PriorityResolutionValidator(),
        PlanPreservationValidator(),
        HierarchyComplianceValidator(),
        MethodologyCompletenessValidator(),
        CitationStatusValidator(),
        FootnoteLinkageValidator(),
        BibliographyCompletenessValidator(),
        VerificationMarkerValidator(),
        OutputClaimsValidator(),
        GateReadinessValidator(),
    ):
        validator.validate(state, minimal_data)
    assert stable_json(minimal_data) == before


def test_cross_reference_marker_target_missing(minimal_data):
    minimal_data["verification_markers"].append(
        {
            "marker_id": "marker-missing",
            "marker_text": "Requires Verification",
            "target_type": "source",
            "target_id": "src-missing",
            "reason": "Missing target.",
            "created_by": "test",
            "removal_authority": "reviewer",
            "status": "open",
            "resolution_evidence": None,
            "arabic_disclosure": "تتطلب هذه الإحالة تحققًا إضافيًا.",
        }
    )
    result = CrossReferenceValidator().validate(ResearchState(minimal_data), minimal_data)
    assert "XREF-001" in _rule_ids(result)


def test_priority_inversion_detected(minimal_data):
    decision = minimal_data["instruction_context"]["priority_decisions"][0]
    decision["selected_authority_level"] = "generic_profile"
    decision["rejected_authority_level"] = "current_user"
    result = PriorityResolutionValidator().validate(ResearchState(minimal_data), minimal_data)
    assert "PRIORITY-002" in _rule_ids(result)


def test_plan_confirmed_missing_pauses(minimal_data):
    minimal_data["approved_plan"]["status"] = "confirmed_missing"
    result = PlanPreservationValidator().validate(ResearchState(minimal_data), minimal_data)
    assert result.decision == "PAUSE"


def test_plan_allowed_omission_with_reason_passes(minimal_data):
    minimal_data["approved_plan"]["status"] = "incomplete_approved"
    node = minimal_data["approved_plan"]["nodes"][0]
    node["locked"] = True
    node["omitted"] = True
    node["omission_reason"] = "User authorized preserving the gap."
    minimal_data["body_hierarchy"]["nodes"] = []
    result = PlanPreservationValidator().validate(ResearchState(minimal_data), minimal_data)
    assert result.findings == ()


def test_hierarchy_duplicate_sibling_order(minimal_data):
    node = dict(minimal_data["body_hierarchy"]["nodes"][0])
    node["heading_id"] = "heading-part-2"
    node["plan_node_id"] = None
    minimal_data["body_hierarchy"]["nodes"].append(node)
    result = HierarchyComplianceValidator().validate(ResearchState(minimal_data), minimal_data)
    assert "HIERARCHY-001" in _rule_ids(result)


def test_direct_quote_requires_location(minimal_data):
    citation = minimal_data["citations"][0]
    citation["direct_quote"] = True
    citation["quote_marks_present"] = False
    citation["location"] = None
    result = CitationStatusValidator().validate(ResearchState(minimal_data), minimal_data)
    assert "CITATION-001" in _rule_ids(result)


def test_bibliography_incomplete_website_metadata_warns_when_marked(minimal_data):
    source = minimal_data["sources"][0]
    source["source_type"] = "website"
    source["url_or_location"] = None
    source["verification_status"] = "requires_verification"
    result = BibliographyCompletenessValidator().validate(ResearchState(minimal_data), minimal_data)
    assert result.findings[0].status == "warning"


def test_marker_resolved_without_evidence(minimal_data):
    minimal_data["verification_markers"].append(
        {
            "marker_id": "marker-resolved",
            "marker_text": "Requires Verification",
            "target_type": "source",
            "target_id": "src-law-1",
            "reason": "Needs proof.",
            "created_by": "test",
            "removal_authority": "reviewer",
            "status": "resolved",
            "resolution_evidence": None,
            "arabic_disclosure": "تتطلب هذه الإحالة تحققًا إضافيًا.",
        }
    )
    result = VerificationMarkerValidator().validate(ResearchState(minimal_data), minimal_data)
    assert "VERIFY-001" in _rule_ids(result)


def test_output_claim_all_citations_verified_blocked_by_marker(minimal_data):
    minimal_data["output_claims"]["requested"] = ["all citations verified"]
    minimal_data["verification_markers"].append(
        {
            "marker_id": "marker-open",
            "marker_text": "Requires Verification",
            "target_type": "source",
            "target_id": "src-law-1",
            "reason": "Open marker.",
            "created_by": "test",
            "removal_authority": "reviewer",
            "status": "open",
            "resolution_evidence": None,
            "arabic_disclosure": "تتطلب هذه الإحالة تحققًا إضافيًا.",
        }
    )
    result = OutputClaimsValidator().validate(ResearchState(minimal_data), minimal_data)
    assert "CLAIM-001" in _rule_ids(result)


def test_gate_not_run_detected(minimal_data):
    gate = minimal_data["state_machine"]["gates"][0]
    gate["status"] = "not_run"
    result = GateReadinessValidator().validate(ResearchState(minimal_data), minimal_data)
    assert "GATE-001" in _rule_ids(result)
