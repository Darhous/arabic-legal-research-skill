# Phase 4 Traceability

| Requirement | Code | Tests | Evidence |
|---|---|---|---|
| Phase 3 gate controls DOCX generation | `docx/render_model.py`, `cli.py` | `tests/unit/test_docx_render_model.py`, `tests/integration/test_artifact_cli.py` | `PHASE_4_IMPLEMENTATION_REPORT.md` |
| Deterministic DOCX package generation | `docx/renderer.py`, `docx/package.py` | `tests/integration/test_docx_generation.py` | Byte equality test before Word |
| Arabic RTL structure in OOXML | `docx/rtl.py`, `docx/styles.py`, `docx/renderer.py` | `tests/integration/test_docx_generation.py`, `tests/unit/test_docx_validation_edges.py` | XML checks for `w:bidi`, `w:rtl`, `w:lang` |
| Word footnotes and linkage | `docx/renderer.py`, `docx/validation.py` | `tests/integration/test_docx_generation.py`, `tests/unit/test_docx_validation_edges.py` | `word/footnotes.xml`, references, orphan checks |
| TOC and PAGE fields | `docx/fields.py`, `docx/validation.py` | `tests/integration/test_docx_generation.py` | Field-code checks |
| Artifact manifest schema | `artifacts/manifest.py`, `schemas/artifact-manifest.schema.json` | `tests/unit/test_schema_and_models.py`, `tests/integration/test_artifact_cli.py` | Draft 2020-12 validation |
| Word isolation and timeout | `word/runner.py`, `word/worker.py`, `word/finalization.py` | `tests/unit/test_word_automation.py`, `tests/integration/test_artifact_cli.py` | Worker-only timeout result |
| No global Word process kill | `word/runner.py` | `tests/unit/test_word_automation.py` | Timeout evidence records worker-only termination |
| Build artifact sequencing | `cli.py` | `tests/integration/test_artifact_cli.py` | Generated DOCX path passed to Word gate |
| Structural vs Word claims | `cli.py`, `artifacts/manifest.py` | `tests/integration/test_artifact_cli.py` | Manifest allowed/prohibited claims |
| Path safety and temp cleanup | `word/finalization.py`, `cli.py` | `tests/unit/test_word_automation.py`, `tests/integration/test_artifact_cli.py` | No partial final output on failure |
