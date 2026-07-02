from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from legal_research_skill.enums import FindingStatus
from legal_research_skill.models import Finding, ResearchState, ValidatorResult, aggregate_result
from legal_research_skill.rules import get_rule


class BaseValidator(ABC):
    name: str = ""
    version: str = "0.3.0"
    scope: str = ""
    required_inputs: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    rule_ids: tuple[str, ...] = ()

    @abstractmethod
    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        """Validate state without mutating it."""

    def result(self, findings: list[Finding], limitations: tuple[str, ...] = ()) -> ValidatorResult:
        return aggregate_result(self.name, self.version, findings, limitations)

    def finding(
        self,
        rule_id: str,
        message: str,
        *,
        status: FindingStatus = FindingStatus.FAIL,
        evidence: dict[str, Any] | None = None,
        path: str = "",
        related_ids: tuple[str, ...] = (),
        corrections: tuple[str, ...] = (),
        verification_required: bool = False,
        limitations: tuple[str, ...] = (),
        code: str = "",
    ) -> Finding:
        rule = get_rule(rule_id)
        return Finding(
            validator=self.name,
            rule_id=rule_id,
            status=status,
            decision=rule.decision,
            severity=rule.severity,
            message=message,
            evidence=evidence or {},
            affected_locations=(path,) if path else (),
            required_corrections=corrections or (rule.correction,),
            verification_required=verification_required,
            task_memory_updates=(rule.source,),
            rerun_required=True,
            limitations=limitations or (rule.limitation,),
            path=path,
            related_ids=related_ids,
            code=code or rule_id,
        )
