from __future__ import annotations

from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator

WORD_LIMITATIONS = (
    "Page placement is not verified in Phase 3.",
    "Per-page footnote restart is not verified in Phase 3.",
    "Microsoft Word rendering is not verified in Phase 3.",
)


class FootnoteLinkageValidator(BaseValidator):
    name = "footnote_linkage"
    dependencies = ("cross_reference", "citation_status")
    rule_ids = ("FOOTNOTE-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        footnote_citations = {
            citation_id
            for footnote in state.list_records("footnotes")
            for citation_id in footnote.get("citation_ids", [])
        }
        for footnote in state.list_records("footnotes"):
            footnote_id = footnote["footnote_id"]
            if not footnote["citation_ids"] and not (footnote.get("purpose_reason") or "").strip():
                findings.append(
                    self.finding(
                        "FOOTNOTE-001",
                        f"Footnote {footnote_id} has no citation linkage or documented purpose.",
                        path=f"/footnotes/{footnote_id}",
                        related_ids=(footnote_id,),
                        code="orphan_footnote",
                    )
                )
            if footnote["numbering_intent"] == "per_page_restart":
                findings.append(
                    self.finding(
                        "FOOTNOTE-001",
                        f"Footnote {footnote_id} requests per-page restart, which is not Word-validated here.",
                        status=__import__(
                            "legal_research_skill.enums", fromlist=["FindingStatus"]
                        ).FindingStatus.WARNING,
                        path=f"/footnotes/{footnote_id}",
                        related_ids=(footnote_id,),
                        limitations=WORD_LIMITATIONS,
                        code="word_footnote_restart_unvalidated",
                    )
                )
        for citation in state.list_records("citations"):
            if citation.get("footnote_required") and citation["citation_id"] not in footnote_citations:
                findings.append(
                    self.finding(
                        "FOOTNOTE-001",
                        f"Citation requiring a footnote is not linked from any footnote: {citation['citation_id']}",
                        path=f"/citations/{citation['citation_id']}",
                        related_ids=(citation["citation_id"],),
                        code="citation_missing_required_footnote",
                    )
                )
        return self.result(findings, WORD_LIMITATIONS)
