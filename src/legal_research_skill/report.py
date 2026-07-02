from __future__ import annotations

import json
from typing import Any

from legal_research_skill.models import ValidationReport


def report_to_json(report: ValidationReport, *, compact: bool = False) -> str:
    indent = None if compact else 2
    return json.dumps(report.to_dict(), ensure_ascii=False, sort_keys=True, indent=indent)


def report_to_text(report: ValidationReport, *, show_passed: bool = False, compact: bool = False) -> str:
    data = report.to_dict()
    lines = [
        "Legal research validation summary",
        f"Input: {data['input_identifier']}",
        f"Overall status: {data['overall_status']}",
        f"Overall decision: {data['overall_decision']}",
        f"Findings: {len(data['findings'])}",
    ]
    if not compact:
        lines.append("Validators:")
        for result in data["validator_results"]:
            if result["status"] == "pass" and not show_passed:
                continue
            suffix = f" ({result['skipped_reason']})" if result["skipped_reason"] else ""
            lines.append(f"- {result['validator']}: {result['status']} / {result['decision']}{suffix}")
        if data["findings"]:
            lines.append("Findings:")
            for finding in data["findings"]:
                lines.append(
                    f"- {finding['rule_id']} [{finding['severity']}/{finding['decision']}]: {finding['message']}"
                )
    if data["prohibited_output_claims"]:
        lines.append("Prohibited claims: " + ", ".join(data["prohibited_output_claims"]))
    if data["limitations"]:
        lines.append("Limitations: " + "; ".join(data["limitations"]))
    return "\n".join(lines) + "\n"


def error_payload(message: str, *, code: str = "input_error") -> dict[str, Any]:
    return {"error": {"code": code, "message": message}}
