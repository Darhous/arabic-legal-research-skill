from __future__ import annotations

from typing import Any

from legal_research_skill.constants import ALLOWED_HIERARCHY
from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator
from legal_research_skill.validators.graph_utils import parent_cycles


class HierarchyComplianceValidator(BaseValidator):
    name = "hierarchy_compliance"
    dependencies = ("cross_reference",)
    rule_ids = ("HIERARCHY-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        headings = state.dict_value("body_hierarchy").get("nodes", [])
        by_id = {heading["heading_id"]: heading for heading in headings}
        sibling_orders: set[tuple[str | None, int]] = set()
        for cycle in parent_cycles(headings, "heading_id", "parent_heading_id"):
            findings.append(
                self.finding(
                    "HIERARCHY-001",
                    "Body hierarchy contains a parent-reference cycle.",
                    evidence={"cycle": list(cycle)},
                    path="/body_hierarchy/nodes",
                    related_ids=cycle,
                    code="hierarchy_parent_cycle",
                )
            )
        for heading in headings:
            level = heading["level_type"]
            if level not in ALLOWED_HIERARCHY:
                findings.append(
                    self.finding(
                        "HIERARCHY-001",
                        f"Unsupported body hierarchy level: {heading['display_label']}",
                        path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                        related_ids=(heading["heading_id"],),
                        code="unsupported_hierarchy_level",
                    )
                )
                continue
            parent_id = heading.get("parent_heading_id")
            level_index = ALLOWED_HIERARCHY.index(level)
            if parent_id is None and level_index != 0:
                findings.append(
                    self.finding(
                        "HIERARCHY-001",
                        f"Heading {heading['heading_id']} starts below root level without a parent.",
                        path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                        related_ids=(heading["heading_id"],),
                        code="level_jump_without_parent",
                    )
                )
            if parent_id:
                parent = by_id.get(parent_id)
                if parent and parent["level_type"] in ALLOWED_HIERARCHY:
                    parent_index = ALLOWED_HIERARCHY.index(parent["level_type"])
                    if level_index != parent_index + 1:
                        findings.append(
                            self.finding(
                                "HIERARCHY-001",
                                f"Heading {heading['heading_id']} skips or repeats hierarchy levels.",
                                evidence={"parent_level": parent["level_type"], "child_level": level},
                                path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                                related_ids=(parent_id, heading["heading_id"]),
                                code="invalid_parent_child_level",
                            )
                        )
            order_key = (parent_id, heading["order"])
            if order_key in sibling_orders:
                findings.append(
                    self.finding(
                        "HIERARCHY-001",
                        f"Duplicate sibling order detected for heading {heading['heading_id']}.",
                        path=f"/body_hierarchy/nodes/{heading['heading_id']}",
                        related_ids=(heading["heading_id"],),
                        code="duplicate_heading_order",
                    )
                )
            sibling_orders.add(order_key)
        return self.result(findings)
