from __future__ import annotations

from typing import Any

from legal_research_skill.enums import FindingStatus
from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator


class CitationStatusValidator(BaseValidator):
    name = "citation_status"
    dependencies = ("cross_reference",)
    rule_ids = ("CITATION-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        sources = state.index("sources", "source_id")
        restrictions = state.dict_value("source_restrictions")
        exclusive_ids = set(restrictions.get("exclusive_source_ids", []))
        source_has_exclusive = {sid for sid, source in sources.items() if source.get("exclusive_use")}
        exclusive_ids |= source_has_exclusive

        if restrictions.get("mandatory_missing_files"):
            findings.append(
                self.finding(
                    "CITATION-001",
                    "Mandatory exclusive source file is missing.",
                    evidence={"missing_files": restrictions["mandatory_missing_files"]},
                    path="/source_restrictions/mandatory_missing_files",
                    code="mandatory_exclusive_file_missing",
                )
            )

        for citation in state.list_records("citations"):
            citation_id = citation["citation_id"]
            source = sources.get(citation["source_id"])
            if not source:
                continue
            if citation["direct_quote"] and (not citation["quote_marks_present"] or not citation.get("location")):
                findings.append(
                    self.finding(
                        "CITATION-001",
                        f"Direct quotation citation lacks quotation marks or location: {citation_id}",
                        path=f"/citations/{citation_id}",
                        related_ids=(citation_id, citation["source_id"]),
                        code="direct_quote_location_missing",
                    )
                )
            if source["verification_status"] == "unverifiable" and citation["verification_status"] == "verified":
                findings.append(
                    self.finding(
                        "CITATION-001",
                        f"Citation {citation_id} cannot be verified when its source is unverifiable.",
                        path=f"/citations/{citation_id}",
                        related_ids=(citation_id, citation["source_id"]),
                        code="citation_stronger_than_source",
                    )
                )
            if source["verification_status"] == "requires_verification":
                findings.append(
                    self.finding(
                        "CITATION-001",
                        f"Citation {citation_id} depends on a source requiring verification.",
                        status=FindingStatus.WARNING,
                        path=f"/citations/{citation_id}",
                        related_ids=(citation_id, citation["source_id"]),
                        verification_required=True,
                        code="citation_requires_verification",
                    )
                )
            if exclusive_ids and citation["source_id"] not in exclusive_ids:
                findings.append(
                    self.finding(
                        "CITATION-001",
                        f"Citation {citation_id} uses a non-exclusive source while exclusive-use sources are active.",
                        path=f"/citations/{citation_id}",
                        related_ids=(citation_id, citation["source_id"]),
                        code="exclusive_source_bypassed",
                    )
                )
        return self.result(findings, ("No external source authenticity verification is performed.",))
