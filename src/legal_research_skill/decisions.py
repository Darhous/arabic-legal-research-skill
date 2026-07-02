from __future__ import annotations

from legal_research_skill.constants import SEVERITY_ORDER
from legal_research_skill.enums import Severity


def threshold_reached(severity: Severity, threshold: str) -> bool:
    return SEVERITY_ORDER[severity.value] >= SEVERITY_ORDER[threshold]
