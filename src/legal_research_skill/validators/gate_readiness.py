from __future__ import annotations

from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator


class GateReadinessValidator(BaseValidator):
    name = "gate_readiness"
    dependencies = ("bibliography_completeness", "footnote_linkage", "methodology_completeness")
    rule_ids = ("GATE-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        machine = state.dict_value("state_machine")
        for gate in machine.get("gates", []):
            if gate["status"] in {"fail", "blocked"}:
                findings.append(
                    self.finding(
                        "GATE-001",
                        f"State-machine gate is not ready: {gate['gate_id']}",
                        evidence={"status": gate["status"], "decision": gate["decision"], "blockers": gate["blockers"]},
                        path=f"/state_machine/gates/{gate['gate_id']}",
                        related_ids=(gate["gate_id"],),
                        code="gate_blocked",
                    )
                )
            if gate["status"] == "not_run" and gate["required_validators"]:
                findings.append(
                    self.finding(
                        "GATE-001",
                        f"Required validators have not run for gate: {gate['gate_id']}",
                        evidence={"required_validators": gate["required_validators"]},
                        path=f"/state_machine/gates/{gate['gate_id']}",
                        related_ids=(gate["gate_id"],),
                        code="gate_not_run",
                    )
                )
        if machine.get("rerun_required"):
            findings.append(
                self.finding(
                    "GATE-001",
                    "State machine records required validator rerun before advancement.",
                    path="/state_machine/rerun_required",
                    code="rerun_required",
                )
            )
        return self.result(findings)
