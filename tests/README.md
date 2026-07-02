# Tests

This directory contains the automated test suite for the executable validation substrate and Phase 4 DOCX artifact pipeline.

## Structure

- `tests/unit/` covers schema/model behavior, individual validators, DOCX render model helpers, OOXML validation edges, Word worker/runner behavior, and CLI behavior.
- `tests/acceptance/` contains adversarial Phase 3 acceptance and hardening tests.
- `tests/integration/` runs all fixtures from `examples/fixtures/manifest.json`, validates generated reports against `schemas/validation-report.schema.json`, and exercises DOCX CLI artifact paths.
- `tests/regression/` contains regression and robustness tests, including a synthetic large state.

## Commands

```bash
pytest
pytest --cov=legal_research_skill --cov-branch --cov-report=term-missing
```

Coverage is configured in `pyproject.toml` with branch coverage enabled and a minimum package coverage threshold of 95%.

## Fixtures

The test suite uses `examples/fixtures/manifest.json` rather than relying on fixture file names alone. Each manifest entry records expected schema validity, overall decision, failing validators, rule IDs, minimum finding counts, and forbidden findings.

Ordinary tests generate DOCX files only under ignored temporary paths and inspect OOXML directly. They do not require real Microsoft Word, Windows COM, or internet access. Word success, failure, timeout, and cleanup behavior are tested with fake worker/COM objects. The test suite does not perform internet verification, legal correctness review, visual review, or print-readiness certification.

Optional real-Word smoke testing is manual and environment-specific:

```bash
python -m legal_research_skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/phase4-artifact --format json
python -m legal_research_skill finalize-word tests_tmp/phase4-artifact/task-approved-plan-locked.docx --output tests_tmp/phase4-artifact/word-finalized.docx --word-timeout-seconds 60 --format json
```

If Word is unavailable or times out, that is reported as a Word gate result, not a unit-test failure.
