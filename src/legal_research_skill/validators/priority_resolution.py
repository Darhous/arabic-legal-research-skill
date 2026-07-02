from __future__ import annotations

from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator

PRIORITY_RANK = {
    "system_developer": 1,
    "current_user": 2,
    "university_course_professor": 3,
    "approved_plan": 4,
    "word_template": 5,
    "police_academy_methodology": 6,
    "generic_profile": 7,
    "internal_default": 8,
    "primary_legal_source": 3,
    "secondary_source": 7,
}


class PriorityResolutionValidator(BaseValidator):
    name = "priority_resolution"
    dependencies = ("cross_reference",)
    rule_ids = ("PRIORITY-001", "PRIORITY-002")

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        context = state.dict_value("instruction_context")
        for conflict in context.get("unresolved_conflicts", []):
            findings.append(
                self.finding(
                    "PRIORITY-001",
                    f"Unresolved priority conflict requires clarification: {conflict}",
                    evidence={"conflict": conflict},
                    path="/instruction_context/unresolved_conflicts",
                    code="unresolved_conflict",
                )
            )

        for decision in context.get("priority_decisions", []):
            missing = [
                field
                for field in ("specificity_recorded", "recency_recorded", "task_memory_update")
                if not decision.get(field)
            ]
            if missing or not decision.get("resolution_reason", "").strip():
                findings.append(
                    self.finding(
                        "PRIORITY-001",
                        f"Priority decision {decision['conflict_id']} lacks required resolution data.",
                        evidence={"missing": missing, "decision": decision},
                        path=f"/instruction_context/priority_decisions/{decision['conflict_id']}",
                        related_ids=(decision["conflict_id"],),
                        code="incomplete_priority_record",
                    )
                )
            selected = PRIORITY_RANK.get(decision["selected_authority_level"])
            rejected = PRIORITY_RANK.get(decision["rejected_authority_level"])
            if selected is None or rejected is None:
                findings.append(
                    self.finding(
                        "PRIORITY-001",
                        f"Priority conflict uses an unknown authority level: {decision['conflict_id']}",
                        evidence={
                            "selected": decision["selected_authority_level"],
                            "rejected": decision["rejected_authority_level"],
                        },
                        path=f"/instruction_context/priority_decisions/{decision['conflict_id']}",
                        related_ids=(decision["conflict_id"],),
                        code="unknown_priority_authority",
                    )
                )
                continue
            if selected > rejected and not decision.get("explicit_user_authorization", False):
                findings.append(
                    self.finding(
                        "PRIORITY-002",
                        "Lower-priority authority selected over higher-priority authority "
                        f"in {decision['conflict_id']}.",
                        evidence={
                            "selected": decision["selected_authority_level"],
                            "rejected": decision["rejected_authority_level"],
                        },
                        path=f"/instruction_context/priority_decisions/{decision['conflict_id']}",
                        related_ids=(decision["conflict_id"],),
                        code="priority_inversion",
                    )
                )
        return self.result(findings)
