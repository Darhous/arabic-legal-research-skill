from __future__ import annotations

from collections import Counter
from typing import Any

from legal_research_skill.models import ResearchState, ValidatorResult
from legal_research_skill.schema_validation import research_state_errors
from legal_research_skill.validators.base import BaseValidator


class SchemaIntegrityValidator(BaseValidator):
    name = "schema_integrity"
    scope = "JSON Schema and identifier integrity"
    rule_ids = ("SCHEMA-001", "SCHEMA-002")

    ID_FIELDS = {
        "sources": "source_id",
        "citations": "citation_id",
        "footnotes": "footnote_id",
        "bibliography": "bibliography_id",
        "verification_markers": "marker_id",
        "reviewer_results": "review_result_id",
    }

    def validate(self, state: ResearchState, raw_data: dict[str, Any] | None = None) -> ValidatorResult:
        data = raw_data if raw_data is not None else state.data
        findings = []
        for index, error in enumerate(research_state_errors(data)):
            findings.append(
                self.finding(
                    "SCHEMA-001",
                    f"Research state schema violation: {error}",
                    path=f"/schema/{index}",
                    code="schema_violation",
                )
            )
        if findings:
            return self.result(findings)

        for list_key, id_key in self.ID_FIELDS.items():
            ids = [str(item.get(id_key, "")) for item in data.get(list_key, [])]
            for entity_id, count in sorted(Counter(ids).items()):
                if count > 1:
                    findings.append(
                        self.finding(
                            "SCHEMA-002",
                            f"Duplicate {id_key} detected: {entity_id}",
                            path=f"/{list_key}",
                            related_ids=(entity_id,),
                            code="duplicate_identifier",
                        )
                    )
        return self.result(findings)
