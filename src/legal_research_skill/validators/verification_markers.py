from __future__ import annotations

from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator


class VerificationMarkerValidator(BaseValidator):
    name = "verification_markers"
    dependencies = ("cross_reference",)
    rule_ids = ("VERIFY-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        for marker in state.list_records("verification_markers"):
            marker_id = marker["marker_id"]
            if marker["marker_text"] != "Requires Verification":
                findings.append(
                    self.finding(
                        "VERIFY-001",
                        f"Invalid internal verification marker text: {marker['marker_text']}",
                        evidence={"allowed": "Requires Verification"},
                        path=f"/verification_markers/{marker_id}",
                        related_ids=(marker_id,),
                        code="invalid_marker_text",
                    )
                )
            for field_name in ("reason", "created_by", "removal_authority"):
                if not marker.get(field_name, "").strip():
                    findings.append(
                        self.finding(
                            "VERIFY-001",
                            f"Verification marker {marker_id} lacks {field_name}.",
                            path=f"/verification_markers/{marker_id}",
                            related_ids=(marker_id,),
                            code="marker_lifecycle_field_missing",
                        )
                    )
            if marker["status"] == "resolved" and not (marker.get("resolution_evidence") or "").strip():
                findings.append(
                    self.finding(
                        "VERIFY-001",
                        f"Verification marker {marker_id} is resolved without evidence.",
                        path=f"/verification_markers/{marker_id}",
                        related_ids=(marker_id,),
                        code="marker_resolved_without_evidence",
                    )
                )
            if marker.get("arabic_disclosure") == marker["marker_text"]:
                findings.append(
                    self.finding(
                        "VERIFY-001",
                        f"Verification marker {marker_id} uses internal marker as Arabic disclosure.",
                        path=f"/verification_markers/{marker_id}",
                        related_ids=(marker_id,),
                        code="marker_disclosure_not_translated",
                    )
                )
        return self.result(findings)
