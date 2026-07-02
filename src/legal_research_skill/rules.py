from __future__ import annotations

from dataclasses import dataclass

from legal_research_skill.enums import Decision, Severity


@dataclass(frozen=True, slots=True)
class Rule:
    rule_id: str
    title: str
    description: str
    severity: Severity
    decision: Decision
    source: str
    validator: str
    correction: str
    limitation: str


RULES: dict[str, Rule] = {
    "SCHEMA-001": Rule(
        "SCHEMA-001",
        "Research state schema compliance",
        "The input must conform to the structured research-state schema and supported version.",
        Severity.CRITICAL,
        Decision.FAIL,
        "rules/task-memory.md",
        "schema_integrity",
        "Correct the JSON shape, required fields, enum values, and unsupported fields.",
        "Schema checks prove structure only, not legal correctness.",
    ),
    "SCHEMA-002": Rule(
        "SCHEMA-002",
        "Stable unique identifiers",
        "Entity identifiers must be non-empty, canonical, and unique within their entity type.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/task-memory.md",
        "schema_integrity",
        "Rename duplicate or malformed identifiers and update references.",
        "Identifier checks do not prove source authenticity.",
    ),
    "XREF-001": Rule(
        "XREF-001",
        "References resolve to existing entities",
        "Citations, footnotes, bibliography entries, headings, markers, and reviewer findings must not dangle.",
        Severity.HIGH,
        Decision.REVISE,
        "validators/README.md",
        "cross_reference",
        "Create the referenced entity, correct the reference, or remove the unsupported record.",
        "Cross-reference checks do not verify external legal sources.",
    ),
    "PRIORITY-001": Rule(
        "PRIORITY-001",
        "Priority decision record is complete",
        "Recorded priority resolutions must include authority, specificity, recency, and a reason.",
        Severity.HIGH,
        Decision.PAUSE,
        "rules/priority-hierarchy.md",
        "priority_resolution",
        "Record the selected authority, rejected alternative, specificity, recency, and resolution reason.",
        "The validator checks recorded priority safety, not substantive legal correctness.",
    ),
    "PRIORITY-002": Rule(
        "PRIORITY-002",
        "Canonical priority hierarchy is preserved",
        "A lower-priority source must not override a higher-priority source without an explicit permissible reason.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/priority-hierarchy.md",
        "priority_resolution",
        "Apply the canonical hierarchy or document a non-conflicting coexistence reason.",
        "Same-authority conflicts may still require user clarification.",
    ),
    "PLAN-001": Rule(
        "PLAN-001",
        "Approved plan headings are preserved",
        "Locked approved plan headings, order, and nesting must match the body hierarchy.",
        Severity.HIGH,
        Decision.REVISE,
        "validators/plan-reviewer.md",
        "plan_preservation",
        "Restore exact headings/order/nesting or record explicit user authorization.",
        "The validator does not judge the academic quality of an approved plan.",
    ),
    "PLAN-002": Rule(
        "PLAN-002",
        "Approved plan status is actionable",
        "Confirmed missing or incomplete approved plans must be paused or explicitly authorized.",
        Severity.CRITICAL,
        Decision.PAUSE,
        "rules/error-recovery.md",
        "plan_preservation",
        "Provide the approved plan, authorize a proposed plan, or preserve gaps with recorded reasons.",
        "The validator cannot infer missing professor-approved content.",
    ),
    "HIERARCHY-001": Rule(
        "HIERARCHY-001",
        "Body hierarchy uses allowed levels",
        "Body headings must use the structured hierarchy قسم, باب, فصل, مبحث, مطلب.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/structure.md",
        "hierarchy_compliance",
        "Replace unsupported levels and repair parent-child relationships.",
        "Structured hierarchy checks do not validate DOCX visual heading styles.",
    ),
    "METHOD-001": Rule(
        "METHOD-001",
        "Methodological components are complete",
        "Required methodology components must be present with meaningful non-placeholder content.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/police-academy-methodology.md",
        "methodology_completeness",
        "Add or substantively complete the missing methodology component.",
        "The validator checks minimum completeness, not deep scholarly quality.",
    ),
    "CITATION-001": Rule(
        "CITATION-001",
        "Citation status is consistent with sources",
        "Citations must link to sources and cannot claim stronger verification than their evidence supports.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/citations.md",
        "citation_status",
        "Link the citation to a real source, add location/evidence, or mark Requires Verification.",
        "No internet or external authenticity verification is performed.",
    ),
    "FOOTNOTE-001": Rule(
        "FOOTNOTE-001",
        "Footnotes are linked and honest",
        "Footnotes must link to citations or a documented non-citation purpose and cannot assert Word placement.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/footnotes.md",
        "footnote_linkage",
        "Link the footnote to citations or record a legitimate purpose and limitation.",
        "Word bottom placement and per-page restart are not validated in Phase 3.",
    ),
    "BIBLIO-001": Rule(
        "BIBLIO-001",
        "Bibliography covers used sources",
        "Every used source requiring bibliography must have an entry and entries must map to known sources.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/bibliography.md",
        "bibliography_completeness",
        "Add missing entries, remove unsupported entries, or provide authorization and metadata.",
        "No bibliography style certification is performed unless encoded in the state.",
    ),
    "VERIFY-001": Rule(
        "VERIFY-001",
        "Verification markers follow lifecycle",
        "The only internal marker is Requires Verification and it must have a target, reason, owner, and authority.",
        Severity.MEDIUM,
        Decision.REVISE,
        "rules/terminology.md",
        "verification_markers",
        "Use the canonical marker and record lifecycle fields and resolution evidence.",
        "Markers do not prove the source is authentic; they disclose verification state.",
    ),
    "CLAIM-001": Rule(
        "CLAIM-001",
        "Output claims match evidence",
        "Restricted final-output claims require the matching artifact and validation evidence.",
        Severity.CRITICAL,
        Decision.FAIL,
        "rules/output-contract.md",
        "output_claims",
        "Remove unsupported claims or provide the required artifact and validation evidence.",
        "Phase 3 validates text-level claims only and performs no DOCX or Word validation.",
    ),
    "GATE-001": Rule(
        "GATE-001",
        "State-machine gates are ready",
        "A state may advance only when required inputs and gate statuses permit it.",
        Severity.HIGH,
        Decision.REVISE,
        "rules/decision-engine.md",
        "gate_readiness",
        "Resolve blockers, rerun required validators, or keep the state at the current gate.",
        "The validator reports readiness and does not mutate state.",
    ),
}


def get_rule(rule_id: str) -> Rule:
    return RULES[rule_id]
