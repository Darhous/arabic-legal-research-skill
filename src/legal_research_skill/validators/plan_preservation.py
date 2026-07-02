from __future__ import annotations

from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator
from legal_research_skill.validators.graph_utils import parent_cycles


class PlanPreservationValidator(BaseValidator):
    name = "plan_preservation"
    dependencies = ("cross_reference", "priority_resolution")
    rule_ids = ("PLAN-001", "PLAN-002")

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        plan = state.dict_value("approved_plan")
        status = plan.get("status")
        plan_nodes = {node["plan_node_id"]: node for node in plan.get("nodes", [])}
        body_nodes = state.dict_value("body_hierarchy").get("nodes", [])
        body_by_id = {heading["heading_id"]: heading for heading in body_nodes}
        headings_by_plan = {
            heading.get("plan_node_id"): heading for heading in body_nodes if heading.get("plan_node_id")
        }

        if status == "confirmed_missing":
            findings.append(
                self.finding(
                    "PLAN-002",
                    "Approved plan is confirmed but missing.",
                    evidence={"approved_plan_status": status},
                    path="/approved_plan/status",
                    code="approved_plan_missing",
                )
            )
            return self.result(findings)

        if status == "incomplete_approved":
            for node in plan_nodes.values():
                if node["omitted"] and not node.get("omission_reason"):
                    findings.append(
                        self.finding(
                            "PLAN-002",
                            f"Incomplete approved plan node lacks omission reason: {node['plan_node_id']}",
                            path=f"/approved_plan/nodes/{node['plan_node_id']}",
                            related_ids=(node["plan_node_id"],),
                            code="missing_omission_reason",
                        )
                    )

        if status == "proposed":
            for node in plan_nodes.values():
                if node.get("locked"):
                    findings.append(
                        self.finding(
                            "PLAN-001",
                            "Proposed plan must not be treated as a locked approved plan.",
                            evidence={"plan_node_id": node["plan_node_id"]},
                            path=f"/approved_plan/nodes/{node['plan_node_id']}",
                            related_ids=(node["plan_node_id"],),
                            code="proposed_plan_locked",
                        )
                    )

        if status in {"approved", "locked_approved", "incomplete_approved"}:
            for cycle in parent_cycles(list(plan_nodes.values()), "plan_node_id", "parent_plan_node_id"):
                findings.append(
                    self.finding(
                        "PLAN-001",
                        "Approved plan contains a parent-reference cycle.",
                        evidence={"cycle": list(cycle)},
                        path="/approved_plan/nodes",
                        related_ids=cycle,
                        code="approved_plan_parent_cycle",
                    )
                )
            expected_order = [
                node["plan_node_id"]
                for node in sorted(plan_nodes.values(), key=lambda item: item["order"])
                if not node["omitted"]
            ]
            actual_order = [
                heading["plan_node_id"]
                for heading in sorted(body_nodes, key=lambda item: item["order"])
                if heading.get("plan_node_id") in plan_nodes
            ]
            if expected_order != actual_order:
                findings.append(
                    self.finding(
                        "PLAN-001",
                        "Body heading order does not preserve the approved plan order.",
                        evidence={"expected_order": expected_order, "actual_order": actual_order},
                        path="/body_hierarchy/nodes",
                        code="approved_plan_reordered",
                    )
                )
            for node_id, node in plan_nodes.items():
                if node["omitted"]:
                    if not node.get("omission_reason"):
                        findings.append(
                            self.finding(
                                "PLAN-002",
                                f"Omitted node has no reason: {node_id}",
                                path=f"/approved_plan/nodes/{node_id}",
                            )
                        )
                    continue
                heading = headings_by_plan.get(node_id)
                if not heading:
                    findings.append(
                        self.finding(
                            "PLAN-001",
                            f"Approved plan node is missing from body hierarchy: {node_id}",
                            path=f"/approved_plan/nodes/{node_id}",
                            related_ids=(node_id,),
                            code="approved_plan_node_missing",
                        )
                    )
                    continue
                if heading["title"] != node["title"]:
                    findings.append(
                        self.finding(
                            "PLAN-001",
                            f"Approved plan title changed for node {node_id}.",
                            evidence={"approved_title": node["title"], "body_title": heading["title"]},
                            path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                            related_ids=(node_id, heading["heading_id"]),
                            code="approved_plan_title_changed",
                        )
                    )
                if heading["level_type"] != node["node_type"]:
                    findings.append(
                        self.finding(
                            "PLAN-001",
                            f"Approved plan level changed for node {node_id}.",
                            evidence={"approved_level": node["node_type"], "body_level": heading["level_type"]},
                            path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                            related_ids=(node_id, heading["heading_id"]),
                            code="approved_plan_level_changed",
                        )
                    )
                parent_heading_id = heading.get("parent_heading_id")
                parent_heading = body_by_id.get(parent_heading_id) if parent_heading_id else None
                body_parent_plan_id = parent_heading.get("plan_node_id") if parent_heading else None
                if body_parent_plan_id != node.get("parent_plan_node_id"):
                    related_ids = tuple(
                        item for item in (node_id, heading["heading_id"], body_parent_plan_id) if item is not None
                    )
                    findings.append(
                        self.finding(
                            "PLAN-001",
                            f"Approved plan parent changed for node {node_id}.",
                            evidence={
                                "approved_parent_plan_node_id": node.get("parent_plan_node_id"),
                                "body_parent_plan_node_id": body_parent_plan_id,
                            },
                            path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                            related_ids=related_ids,
                            code="approved_plan_parent_changed",
                        )
                    )
            extra = [heading for heading in body_nodes if not heading.get("plan_node_id")]
            for heading in extra:
                findings.append(
                    self.finding(
                        "PLAN-001",
                        f"Unauthorized extra body heading is not mapped to approved plan: {heading['heading_id']}",
                        path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                        related_ids=(heading["heading_id"],),
                        code="unauthorized_extra_heading",
                    )
                )
        return self.result(findings)
