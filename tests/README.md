# Tests

This directory contains the Phase 3 automated test suite for the executable validation substrate.

## Structure

- `tests/unit/` covers schema/model behavior, individual validators, and CLI behavior.
- `tests/acceptance/` contains adversarial Phase 3 acceptance and hardening tests.
- `tests/integration/` runs all fixtures from `examples/fixtures/manifest.json` and validates generated reports against `schemas/validation-report.schema.json`.
- `tests/regression/` contains regression and robustness tests, including a synthetic large state.

## Commands

```bash
pytest
pytest --cov=legal_research_skill --cov-branch --cov-report=term-missing
```

Coverage is configured in `pyproject.toml` with branch coverage enabled and a minimum package coverage threshold of 95%.

## Fixtures

The test suite uses `examples/fixtures/manifest.json` rather than relying on fixture file names alone. Each manifest entry records expected schema validity, overall decision, failing validators, rule IDs, minimum finding counts, and forbidden findings.

The tests do not perform DOCX generation, Word automation, internet verification, legal correctness review, or final RTL rendering validation.
