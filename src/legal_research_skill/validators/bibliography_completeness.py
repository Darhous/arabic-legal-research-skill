from __future__ import annotations

from collections import Counter
from typing import Any

from legal_research_skill.enums import FindingStatus
from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator


class BibliographyCompletenessValidator(BaseValidator):
    name = "bibliography_completeness"
    dependencies = ("cross_reference", "citation_status")
    rule_ids = ("BIBLIO-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        sources = state.index("sources", "source_id")
        entries = state.list_records("bibliography")
        entry_sources = [source_id for entry in entries for source_id in entry["source_ids"]]
        entry_source_set = set(entry_sources)

        for source_id, source in sources.items():
            if source["used_in_research"] and source["include_in_bibliography"] and source_id not in entry_source_set:
                findings.append(
                    self.finding(
                        "BIBLIO-001",
                        f"Used source is missing from bibliography: {source_id}",
                        path=f"/sources/{source_id}",
                        related_ids=(source_id,),
                        code="used_source_missing_bibliography",
                    )
                )
            if source["used_in_research"] and self._metadata_missing(source):
                status = (
                    FindingStatus.WARNING
                    if source["verification_status"] == "requires_verification"
                    else FindingStatus.FAIL
                )
                findings.append(
                    self.finding(
                        "BIBLIO-001",
                        f"Source metadata is incomplete for bibliography review: {source_id}",
                        status=status,
                        path=f"/sources/{source_id}",
                        related_ids=(source_id,),
                        verification_required=source["verification_status"] == "requires_verification",
                        code="bibliographic_metadata_incomplete",
                    )
                )

        for source_id, count in sorted(Counter(entry_sources).items()):
            if count > 1:
                findings.append(
                    self.finding(
                        "BIBLIO-001",
                        f"Duplicate bibliography linkage for source: {source_id}",
                        path="/bibliography",
                        related_ids=(source_id,),
                        code="duplicate_bibliography_entry",
                    )
                )
        for entry in entries:
            for source_id in entry["source_ids"]:
                source = sources.get(source_id)
                if source and not source["used_in_research"] and not entry["authorized_unused"]:
                    findings.append(
                        self.finding(
                            "BIBLIO-001",
                            f"Unused source appears in bibliography without authorization: {source_id}",
                            path=f"/bibliography/{entry['bibliography_id']}",
                            related_ids=(entry["bibliography_id"], source_id),
                            code="unauthorized_unused_bibliography_entry",
                        )
                    )
                if (
                    source
                    and source["verification_status"] == "requires_verification"
                    and entry["verification_status"] == "verified"
                ):
                    findings.append(
                        self.finding(
                            "BIBLIO-001",
                            "Bibliography entry is stronger than source verification status: "
                            f"{entry['bibliography_id']}",
                            path=f"/bibliography/{entry['bibliography_id']}",
                            related_ids=(entry["bibliography_id"], source_id),
                            code="bibliography_stronger_than_source",
                        )
                    )
        return self.result(findings)

    @staticmethod
    def _metadata_missing(source: dict[str, Any]) -> bool:
        data = source.get("bibliographic_data", {})
        if not data.get("title"):
            return True
        if source["source_type"] == "website":
            return not (source.get("url_or_location") and data.get("accessed_at"))
        if source["source_type"] in {"book", "journal_article", "thesis"}:
            return not (data.get("author") or source.get("authors"))
        return False
