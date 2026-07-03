# Examples

<!-- Designed by Ahmed Darhous -- https://github.com/darhous -->

This directory contains two kinds of examples:

1. Narrative, beginner-friendly scenario examples (`basic-legal-research/`, `legal-memo/`,
   `contract-review/`, `bad-vs-good-output/`, `docx-artifact/`), each with `input.md` (the prompt
   sent to a model), `expected-output.md` (an illustrative or, for `docx-artifact/`, a real
   captured result), and `notes.md` (caveats and how to reproduce it). See
   [`playbooks/`](../playbooks/) and [`workflows/`](../workflows/) for the guides these examples
   accompany.
2. Phase 3 structured JSON fixtures for the executable validation substrate (below) — used by the
   automated test suite, not narrative examples.

## Fixtures

- `fixtures/valid/minimal-valid.json` is a small valid text-level research state.
- `fixtures/valid/approved-plan-locked.json` preserves a locked professor-approved plan.
- `fixtures/valid/requires-verification-valid.json` is structurally valid while preserving an open `Requires Verification` marker and limited output claims.
- `fixtures/invalid/*.json` cover representative validator failures.
- `fixtures/manifest.json` records expected validators, rule IDs, decisions, and the reason each fixture exists.
- `fixtures/docx/manifest.json` records representative Phase 4 DOCX artifact expectations. Binary DOCX files are generated during tests and smoke runs under ignored temporary paths, not committed.

## Example Policy

Examples must be clearly illustrative. They must not present fabricated legal references as verified sources.

Use `Requires Verification` for illustrative citation records that are intentionally not verified.

## Validation

Each example includes expected validation results through `fixtures/manifest.json`. If a fixture intentionally fails, its failure purpose is documented there.

These fixtures do not contain committed DOCX output and do not claim Microsoft Word validation. Use the Phase 4 CLI to generate disposable artifacts:

```bash
python -m legal_research_skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/phase4-artifact
```
