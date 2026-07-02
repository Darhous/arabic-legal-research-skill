from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from legal_research_skill.constants import (
    DECISION_ORDER,
    REPORT_SCHEMA_VERSION,
    STATUS_ORDER,
)
from legal_research_skill.enums import Decision, FindingStatus, Severity


def stable_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_hash(data: Any) -> str:
    return hashlib.sha256(stable_json(data).encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class ResearchState:
    data: dict[str, Any]

    @property
    def task_identifier(self) -> str:
        return str(self.data["task_identifier"])

    def list_records(self, key: str) -> list[dict[str, Any]]:
        value = self.data.get(key, [])
        return value if isinstance(value, list) else []

    def dict_value(self, key: str) -> dict[str, Any]:
        value = self.data.get(key, {})
        return value if isinstance(value, dict) else {}

    def index(self, list_key: str, id_key: str) -> dict[str, dict[str, Any]]:
        return {
            str(item[id_key]): item for item in self.list_records(list_key) if isinstance(item, dict) and id_key in item
        }

    def serialize(self) -> dict[str, Any]:
        return json.loads(stable_json(self.data))


@dataclass(frozen=True, slots=True)
class Finding:
    validator: str
    rule_id: str
    status: FindingStatus
    decision: Decision
    severity: Severity
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    affected_locations: tuple[str, ...] = ()
    required_corrections: tuple[str, ...] = ()
    verification_required: bool = False
    task_memory_updates: tuple[str, ...] = ()
    rerun_required: bool = False
    limitations: tuple[str, ...] = ()
    path: str = ""
    related_ids: tuple[str, ...] = ()
    code: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def finding_id(self) -> str:
        source = {
            "validator": self.validator,
            "rule_id": self.rule_id,
            "status": self.status.value,
            "message": self.message,
            "path": self.path,
            "related_ids": self.related_ids,
            "evidence": self.evidence,
        }
        return f"{self.rule_id}-{stable_hash(source)}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "validator": self.validator,
            "rule_id": self.rule_id,
            "status": self.status.value,
            "decision": self.decision.value,
            "severity": self.severity.value,
            "message": self.message,
            "evidence": self.evidence,
            "affected_locations": list(self.affected_locations),
            "required_corrections": list(self.required_corrections),
            "verification_required": self.verification_required,
            "task_memory_updates": list(self.task_memory_updates),
            "rerun_required": self.rerun_required,
            "limitations": list(self.limitations),
            "path": self.path,
            "related_ids": list(self.related_ids),
            "code": self.code,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class ValidatorResult:
    validator: str
    version: str
    status: FindingStatus
    decision: Decision
    findings: tuple[Finding, ...] = ()
    skipped_reason: str | None = None
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "validator": self.validator,
            "version": self.version,
            "status": self.status.value,
            "decision": self.decision.value,
            "findings": [finding.to_dict() for finding in self.findings],
            "skipped_reason": self.skipped_reason,
            "limitations": list(self.limitations),
        }


@dataclass(frozen=True, slots=True)
class ValidationReport:
    input_identifier: str
    input_hash: str
    validator_results: tuple[ValidatorResult, ...]
    allowed_output_claims: tuple[str, ...] = ()
    prohibited_output_claims: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @property
    def findings(self) -> tuple[Finding, ...]:
        return tuple(f for result in self.validator_results for f in result.findings)

    @property
    def overall_status(self) -> FindingStatus:
        status = FindingStatus.PASS
        for result in self.validator_results:
            if STATUS_ORDER[result.status.value] > STATUS_ORDER[status.value]:
                status = result.status
        return status

    @property
    def overall_decision(self) -> Decision:
        decision = Decision.PROCEED
        for result in self.validator_results:
            if DECISION_ORDER[result.decision.value] > DECISION_ORDER[decision.value]:
                decision = result.decision
        return decision

    def counts_by_severity(self) -> dict[str, int]:
        counts = {severity.value: 0 for severity in Severity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return counts

    def counts_by_status(self) -> dict[str, int]:
        counts = {status.value: 0 for status in FindingStatus}
        for finding in self.findings:
            counts[finding.status.value] += 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        findings = sorted(
            (finding.to_dict() for finding in self.findings),
            key=lambda item: (item["validator"], item["rule_id"], item["finding_id"]),
        )
        return {
            "report_schema_version": REPORT_SCHEMA_VERSION,
            "metadata": {
                "tool": "legal_research_skill",
                "package_version": "0.3.0",
                "deterministic": True,
            },
            "input_identifier": self.input_identifier,
            "input_hash": self.input_hash,
            "overall_status": self.overall_status.value,
            "overall_decision": self.overall_decision.value,
            "validator_results": [result.to_dict() for result in self.validator_results],
            "findings": findings,
            "counts_by_severity": self.counts_by_severity(),
            "counts_by_status": self.counts_by_status(),
            "executed_validators": [
                result.validator for result in self.validator_results if result.status != FindingStatus.SKIPPED
            ],
            "skipped_validators": [
                {"validator": result.validator, "reason": result.skipped_reason or ""}
                for result in self.validator_results
                if result.status == FindingStatus.SKIPPED
            ],
            "allowed_output_claims": sorted(set(self.allowed_output_claims)),
            "prohibited_output_claims": sorted(set(self.prohibited_output_claims)),
            "limitations": sorted(set(self.limitations)),
        }


def aggregate_result(
    validator: str, version: str, findings: list[Finding], limitations: tuple[str, ...] = ()
) -> ValidatorResult:
    if not findings:
        return ValidatorResult(validator, version, FindingStatus.PASS, Decision.PROCEED, (), None, limitations)
    status = FindingStatus.WARNING
    decision = Decision.PROCEED
    for finding in findings:
        if finding.status == FindingStatus.FAIL:
            status = FindingStatus.FAIL
        elif status != FindingStatus.FAIL and finding.status == FindingStatus.WARNING:
            status = FindingStatus.WARNING
        if DECISION_ORDER[finding.decision.value] > DECISION_ORDER[decision.value]:
            decision = finding.decision
    return ValidatorResult(
        validator, version, status, decision, tuple(sorted(findings, key=lambda f: f.finding_id)), None, limitations
    )
