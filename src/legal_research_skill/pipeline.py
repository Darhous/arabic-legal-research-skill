from __future__ import annotations

from pathlib import Path

from legal_research_skill.enums import Decision, FindingStatus
from legal_research_skill.errors import UnknownValidatorError
from legal_research_skill.loader import read_json
from legal_research_skill.models import ResearchState, ValidationReport, ValidatorResult, stable_hash
from legal_research_skill.schema_validation import report_errors
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
    SchemaIntegrityValidator,
    VerificationMarkerValidator,
)
from legal_research_skill.validators.base import BaseValidator

VALIDATOR_CLASSES: tuple[type[BaseValidator], ...] = (
    SchemaIntegrityValidator,
    CrossReferenceValidator,
    PriorityResolutionValidator,
    PlanPreservationValidator,
    HierarchyComplianceValidator,
    MethodologyCompletenessValidator,
    CitationStatusValidator,
    FootnoteLinkageValidator,
    BibliographyCompletenessValidator,
    VerificationMarkerValidator,
    OutputClaimsValidator,
    GateReadinessValidator,
)


def available_validators() -> list[BaseValidator]:
    return [validator_class() for validator_class in VALIDATOR_CLASSES]


def validator_names() -> list[str]:
    return [validator.name for validator in available_validators()]


def run_pipeline(
    input_path: Path,
    *,
    only: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> ValidationReport:
    validators = available_validators()
    known = {validator.name for validator in validators}
    requested = set(only)
    excluded = set(exclude)
    unknown = (requested | excluded) - known
    if unknown:
        raise UnknownValidatorError(f"Unknown validator(s): {', '.join(sorted(unknown))}")

    raw_data = read_json(input_path)
    state = ResearchState(raw_data)
    results: list[ValidatorResult] = []
    by_name: dict[str, ValidatorResult] = {}
    schema_blocked = False

    for validator in validators:
        if validator.name in excluded:
            result = _skipped(validator, "explicitly excluded")
        elif requested and validator.name != "schema_integrity" and validator.name not in requested:
            result = _skipped(validator, "not selected")
        elif schema_blocked and validator.name != "schema_integrity":
            result = _skipped(validator, "schema_integrity failed")
        elif any(_dependency_failed(by_name.get(dep)) for dep in validator.dependencies):
            result = _skipped(validator, "dependency failed")
        else:
            result = validator.validate(state, raw_data)
            if validator.name == "gate_readiness":
                result = _apply_prior_blockers_to_gate(validator, result, by_name)
        if validator.name == "schema_integrity" and result.status == FindingStatus.FAIL:
            schema_blocked = True
        results.append(result)
        by_name[validator.name] = result

    output_claims = raw_data.get("output_claims", {}) if isinstance(raw_data, dict) else {}
    report = ValidationReport(
        input_identifier=str(input_path),
        input_hash=stable_hash(raw_data),
        validator_results=tuple(results),
        allowed_output_claims=tuple(output_claims.get("allowed", [])),
        prohibited_output_claims=tuple(output_claims.get("prohibited", [])),
        limitations=_collect_limitations(results),
    )
    errors = report_errors(report.to_dict())
    if errors:
        raise RuntimeError(f"Generated validation report does not match schema: {'; '.join(errors)}")
    return report


def _dependency_failed(result: ValidatorResult | None) -> bool:
    if result is None:
        return False
    return result.status == FindingStatus.FAIL


def _skipped(validator: BaseValidator, reason: str) -> ValidatorResult:
    return ValidatorResult(
        validator=validator.name,
        version=validator.version,
        status=FindingStatus.SKIPPED,
        decision=Decision.PROCEED,
        findings=(),
        skipped_reason=reason,
        limitations=(),
    )


def _apply_prior_blockers_to_gate(
    validator: BaseValidator, result: ValidatorResult, prior_results: dict[str, ValidatorResult]
) -> ValidatorResult:
    blockers = tuple(
        name
        for name, prior_result in prior_results.items()
        if name != "schema_integrity" and prior_result.status == FindingStatus.FAIL
    )
    if not blockers:
        return result
    findings = list(result.findings)
    findings.append(
        validator.finding(
            "GATE-001",
            "Prior validator blocker prevents state-machine advancement.",
            evidence={"blocking_validators": list(blockers)},
            path="/state_machine/gates",
            related_ids=blockers,
            code="prior_validator_blocker",
        )
    )
    return validator.result(findings, result.limitations)


def _collect_limitations(results: list[ValidatorResult]) -> tuple[str, ...]:
    limitations: set[str] = set()
    for result in results:
        limitations.update(result.limitations)
        for finding in result.findings:
            limitations.update(finding.limitations)
    return tuple(sorted(limitations))
