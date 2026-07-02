from __future__ import annotations

from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.validators.base import BaseValidator


class CrossReferenceValidator(BaseValidator):
    name = "cross_reference"
    dependencies = ("schema_integrity",)
    rule_ids = ("XREF-001",)

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        findings = []
        sources = state.index("sources", "source_id")
        citations = state.index("citations", "citation_id")
        footnotes = state.index("footnotes", "footnote_id")
        bibliography = state.index("bibliography", "bibliography_id")
        markers = state.index("verification_markers", "marker_id")
        headings = {str(item["heading_id"]): item for item in state.dict_value("body_hierarchy").get("nodes", [])}
        plan_nodes = {str(item["plan_node_id"]): item for item in state.dict_value("approved_plan").get("nodes", [])}
        entity_indexes = {
            "source": sources,
            "citation": citations,
            "footnote": footnotes,
            "bibliography": bibliography,
            "heading": headings,
            "plan_node": plan_nodes,
            "marker": markers,
        }

        for citation in state.list_records("citations"):
            source_id = citation["source_id"]
            if source_id not in sources:
                findings.append(self._dangling("citation source", source_id, f"/citations/{citation['citation_id']}"))
            marker_id = citation.get("marker_id")
            if marker_id and marker_id not in markers:
                findings.append(self._dangling("citation marker", marker_id, f"/citations/{citation['citation_id']}"))

        for footnote in state.list_records("footnotes"):
            for citation_id in footnote["citation_ids"]:
                if citation_id not in citations:
                    findings.append(
                        self._dangling("footnote citation", citation_id, f"/footnotes/{footnote['footnote_id']}")
                    )

        for entry in state.list_records("bibliography"):
            for source_id in entry["source_ids"]:
                if source_id not in sources:
                    findings.append(
                        self._dangling("bibliography source", source_id, f"/bibliography/{entry['bibliography_id']}")
                    )

        for heading in state.dict_value("body_hierarchy").get("nodes", []):
            plan_node_id = heading.get("plan_node_id")
            if plan_node_id and plan_node_id not in plan_nodes:
                findings.append(
                    self._dangling("heading plan node", plan_node_id, f"/body_hierarchy/{heading['heading_id']}")
                )
            parent_id = heading.get("parent_heading_id")
            if parent_id and parent_id not in headings:
                findings.append(self._dangling("heading parent", parent_id, f"/body_hierarchy/{heading['heading_id']}"))

        for marker in state.list_records("verification_markers"):
            target_type = marker["target_type"]
            target_id = marker["target_id"]
            if target_id not in entity_indexes[target_type]:
                findings.append(
                    self._dangling(f"marker {target_type}", target_id, f"/verification_markers/{marker['marker_id']}")
                )

        for review in state.list_records("reviewer_results"):
            entity_type = review["affected_entity_type"]
            entity_id = review.get("affected_entity_id")
            if entity_type != "none" and entity_id not in entity_indexes[entity_type]:
                findings.append(
                    self._dangling(
                        f"reviewer {entity_type}", entity_id or "", f"/reviewer_results/{review['review_result_id']}"
                    )
                )

        return self.result(findings)

    def _dangling(self, label: str, entity_id: str, path: str):
        return self.finding(
            "XREF-001",
            f"Dangling {label} reference: {entity_id}",
            evidence={"missing_id": entity_id, "reference_type": label},
            path=path,
            related_ids=(entity_id,),
            code="dangling_reference",
        )
