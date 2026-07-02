from __future__ import annotations

from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator

CLAIM_REQUIREMENTS = {
    "print-ready": ("docx_generated", "docx_structurally_validated", "word_manually_validated", "all_reviewers_passed"),
    "submission-ready": (
        "docx_generated",
        "docx_structurally_validated",
        "word_manually_validated",
        "all_reviewers_passed",
        "submission_requirements_confirmed",
    ),
    "all citations verified": ("all_sources_verified",),
    "sources verified": ("all_sources_verified",),
    "docx generated": ("docx_generated",),
    "final docx": ("docx_generated", "docx_structurally_validated"),
    "word-compatible": ("docx_generated", "word_manually_validated"),
    "automated legal validation": ("automated_legal_correctness_validated",),
    "legal correctness validated": ("automated_legal_correctness_validated",),
    "legal correctness verified": ("automated_legal_correctness_validated",),
    "rtl validated": ("rtl_rendering_validated",),
    "toc updated": ("toc_updated_in_word",),
    "per-page footnote restart verified": ("word_footnote_restart_validated",),
}

ALWAYS_PROHIBITED_CLAIMS = {
    "court-ready",
    "final legal research accepted",
    "human reviewed",
    "source authenticity verified",
    "submission-ready",
}

HONEST_CLAIMS = {
    "content validation completed",
    "text-level checks completed",
    "text-level validation completed",
    "docx generation not performed",
    "microsoft word validation required",
    "citation review completed with verification gaps",
    "citations include unresolved verification markers",
}

CLAIM_ALIASES = {
    "docx_generated": "docx generated",
    "print ready": "print-ready",
    "submission ready": "submission-ready",
    "word compatible": "word-compatible",
}


class OutputClaimsValidator(BaseValidator):
    name = "output_claims"
    dependencies = ("verification_markers",)
    rule_ids = ("CLAIM-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        claims = state.dict_value("output_claims")
        evidence = claims.get("evidence", {})
        requested = [_canonical_claim(claim) for claim in claims.get("requested", [])]
        prohibited = {_canonical_claim(claim) for claim in claims.get("prohibited", [])}
        open_markers = [marker for marker in state.list_records("verification_markers") if marker["status"] == "open"]

        for claim in requested:
            requirements = CLAIM_REQUIREMENTS.get(claim)
            if claim in prohibited or claim in ALWAYS_PROHIBITED_CLAIMS:
                findings.append(self._unsupported(claim, ["claim listed as prohibited"]))
                continue
            if requirements:
                missing = [requirement for requirement in requirements if not evidence.get(requirement)]
                if claim in {"all citations verified", "sources verified"} and open_markers:
                    missing.append("no open Requires Verification markers")
                if missing:
                    findings.append(self._unsupported(claim, missing))
            elif claim not in HONEST_CLAIMS and ("validated" in claim or "verified" in claim or "updated" in claim):
                findings.append(self._unsupported(claim, ["unsupported validation claim"]))
        return self.result(findings, ("No DOCX generation or Microsoft Word validation is performed in Phase 3.",))

    def _unsupported(self, claim: str, missing: list[str]):
        return self.finding(
            "CLAIM-001",
            f"Unsupported output claim: {claim}",
            evidence={"claim": claim, "missing_evidence": missing},
            path="/output_claims/requested",
            related_ids=(claim,),
            code="unsupported_output_claim",
        )


def _canonical_claim(claim: str) -> str:
    normalized = " ".join(claim.strip().lower().replace("_", " ").split())
    return CLAIM_ALIASES.get(normalized, normalized)
