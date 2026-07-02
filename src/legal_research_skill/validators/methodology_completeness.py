from __future__ import annotations

import re
from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator

REQUIRED_COMPONENTS = (
    "preface",
    "problem",
    "importance",
    "previous_studies",
    "objectives",
    "methodology",
    "scope",
    "hypotheses",
    "questions",
    "tools",
    "concepts",
    "difficulties",
    "plan_presentation",
)

PLACEHOLDER_RE = re.compile(r"^\s*(tbd|todo|placeholder|\.\.\.|لاحقًا|يضاف لاحقا)\s*$", re.IGNORECASE)


class MethodologyCompletenessValidator(BaseValidator):
    name = "methodology_completeness"
    dependencies = ("plan_preservation",)
    rule_ids = ("METHOD-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        title = state.dict_value("research_metadata").get("research_title", {})
        if title.get("status") not in {"Known", "Derived", "Assumed"} or not (title.get("value") or "").strip():
            findings.append(
                self.finding(
                    "METHOD-001",
                    "Research title is missing or not actionable.",
                    path="/research_metadata/research_title",
                    code="missing_research_title",
                )
            )

        methodology = state.dict_value("methodology")
        components = methodology.get("components", {})
        for key in REQUIRED_COMPONENTS:
            component = components.get(key)
            if not component:
                findings.append(self._component_finding(key, "missing", f"/methodology/components/{key}"))
                continue
            status = component.get("status")
            content = component.get("content") or ""
            if status in {"missing", "empty", "placeholder"} or not self._meaningful(content):
                findings.append(self._component_finding(key, status, f"/methodology/components/{key}"))

        conclusion = methodology.get("conclusion", {})
        for key in ("summary", "findings", "recommendations"):
            component = conclusion.get(key, {})
            if component.get("status") != "present" or not self._meaningful(component.get("content") or ""):
                findings.append(
                    self._component_finding(key, component.get("status", "missing"), f"/methodology/conclusion/{key}")
                )
        return self.result(findings, ("Minimum content checks do not certify deep scholarly quality.",))

    def _component_finding(self, key: str, status: str, path: str):
        return self.finding(
            "METHOD-001",
            f"Methodology component is not substantively complete: {key}",
            evidence={"component": key, "status": status},
            path=path,
            related_ids=(key,),
            code="methodology_component_incomplete",
        )

    @staticmethod
    def _meaningful(content: str) -> bool:
        stripped = content.strip()
        if PLACEHOLDER_RE.match(stripped):
            return False
        letters = [char for char in stripped if char.isalpha()]
        return len(letters) >= 8 and len(set(letters)) >= 4
