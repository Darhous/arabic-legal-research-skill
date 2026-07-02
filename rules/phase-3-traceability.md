# Phase 3 Traceability

This file maps executable Phase 3 components to Phase 2 rule sources and reviewer contracts. It avoids duplicating the full rule text.

| Executable component | Rule source | Reviewer contract | Tests | Fixture coverage |
|---|---|---|---|---|
| `schemas/research-state.schema.json` top-level fields | `rules/task-memory.md` | `validators/README.md` | `tests/unit/test_schema_and_models.py` | All fixtures |
| `schemas/validation-report.schema.json` | `validators/README.md`, `rules/output-contract.md` | `validators/final-qa-reviewer.md` | `tests/integration/test_manifest_pipeline.py` | All fixtures |
| `schema_integrity` / `SCHEMA-001`, `SCHEMA-002` | `rules/task-memory.md` | Base reviewer contract | `tests/unit/test_schema_and_models.py`, `tests/integration/test_manifest_pipeline.py` | `malformed-schema.json`, `duplicate-identifiers.json` |
| `cross_reference` / `XREF-001` | `rules/task-memory.md` | `validators/citation-reviewer.md`, `validators/footnote-reviewer.md`, `validators/bibliography-reviewer.md` | `tests/unit/test_edge_coverage.py`, `tests/integration/test_manifest_pipeline.py` | `dangling-citation-source.json` |
| `priority_resolution` / `PRIORITY-001`, `PRIORITY-002` | `rules/priority-hierarchy.md` | Base reviewer contract | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `unresolved-priority-conflict.json` |
| `plan_preservation` / `PLAN-001`, `PLAN-002` | `rules/structure.md`, `rules/error-recovery.md` | `validators/plan-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `approved-plan-locked.json`, `approved-plan-reordered.json`, `approved-plan-heading-changed.json` |
| `hierarchy_compliance` / `HIERARCHY-001` | `rules/structure.md` | `validators/plan-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `hierarchy-level-jump.json` |
| `methodology_completeness` / `METHOD-001` | `rules/police-academy-methodology.md`, `rules/structure.md` | `validators/methodology-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `missing-methodology-elements.json` |
| `citation_status` / `CITATION-001` | `rules/citations.md`, `rules/error-recovery.md` | `validators/citation-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `requires-verification-valid.json`, `dangling-citation-source.json` |
| `footnote_linkage` / `FOOTNOTE-001` | `rules/footnotes.md` | `validators/footnote-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `orphan-footnote.json` |
| `bibliography_completeness` / `BIBLIO-001` | `rules/bibliography.md` | `validators/bibliography-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `bibliography-missing-used-source.json`, `bibliography-orphan-entry.json` |
| `verification_markers` / `VERIFY-001` | `rules/terminology.md`, `rules/task-memory.md` | `validators/citation-reviewer.md`, `validators/footnote-reviewer.md`, `validators/bibliography-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `requires-verification-valid.json`, `invalid-verification-marker.json` |
| `output_claims` / `CLAIM-001` | `rules/output-contract.md` | `validators/docx-readiness-reviewer.md`, `validators/final-qa-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py`, `tests/unit/test_cli.py` | `unsupported-output-claim.json`, `requires-verification-valid.json` |
| `gate_readiness` / `GATE-001` | `rules/decision-engine.md` | `validators/final-qa-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | All fixtures through state-machine records |
| CLI `validate` | `rules/decision-engine.md`, `rules/output-contract.md` | Final QA contract | `tests/unit/test_cli.py` | All fixtures |
| CLI `schema-check` | `rules/task-memory.md` | Base reviewer contract | `tests/unit/test_cli.py` | `minimal-valid.json`, `malformed-schema.json` |
| CLI `list-validators` | `rules/terminology.md` | Base reviewer contract | `tests/unit/test_cli.py` | Not fixture-specific |
| CLI `explain RULE_ID` | Rule registry | Base reviewer contract | `tests/unit/test_cli.py` | Not fixture-specific |
| Deterministic report sorting and IDs | `rules/output-contract.md` | `validators/final-qa-reviewer.md` | `tests/integration/test_manifest_pipeline.py` | `unsupported-output-claim.json` |
| Output claim boundaries | `rules/output-contract.md` | `validators/docx-readiness-reviewer.md`, `validators/final-qa-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | `unsupported-output-claim.json` |
| State gates | `rules/decision-engine.md` | `validators/final-qa-reviewer.md` | `tests/unit/test_validators.py`, `tests/unit/test_edge_coverage.py` | All fixtures |

## Schema Field Coverage

| Task-memory field | Schema path |
|---|---|
| `task_identifier` | `/task_identifier` |
| `user_request` | `/user_request` |
| `jurisdiction` | `/jurisdiction` |
| `institution_profile` | `/institution_profile` |
| `language` | `/language` |
| `research_type` | `/research_type` |
| `source_restrictions` | `/source_restrictions` |
| `research_title` | `/research_metadata/research_title` |
| `approved_plan_status` | `/approved_plan/status` |
| `locked_plan_structure` | `/approved_plan/nodes` |
| `required_output_type` | `/research_metadata/required_output_type` |
| `formatting_profile` | `/formatting_profile` |
| `page_count_target` | `/research_metadata/page_count_target` |
| `source_inventory` | `/sources` |
| `source_authority_level` | `/sources/*/authority_level` |
| `source_verification_status` | `/sources/*/verification_status` |
| `citation_records` | `/citations` |
| `footnote_records` | `/footnotes` |
| `bibliography_records` | `/bibliography` |
| `assumptions` | `/assumptions` |
| `unresolved_questions` | `/unresolved_questions` |
| `verification_markers` | `/verification_markers` |
| `state_machine_current_state` | `/state_machine/current_state` |
| `completed_gates` and `failed_gates` | `/state_machine/gates` |
| `reviewer_findings` | `/reviewer_results` |
| `revision_history` | `/validation_history` |
| `delivery_claims_allowed` | `/output_claims/allowed` |
| `delivery_claims_prohibited` | `/output_claims/prohibited` |
