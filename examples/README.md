# Examples

This directory contains Phase 3 structured JSON fixtures for the executable validation substrate.

## Fixtures

- `fixtures/valid/minimal-valid.json` is a small valid text-level research state.
- `fixtures/valid/approved-plan-locked.json` preserves a locked professor-approved plan.
- `fixtures/valid/requires-verification-valid.json` is structurally valid while preserving an open `Requires Verification` marker and limited output claims.
- `fixtures/invalid/*.json` cover representative validator failures.
- `fixtures/manifest.json` records expected validators, rule IDs, decisions, and the reason each fixture exists.

## Example Policy

Examples must be clearly illustrative. They must not present fabricated legal references as verified sources.

Use `Requires Verification` for illustrative citation records that are intentionally not verified.

## Validation

Each example includes expected validation results through `fixtures/manifest.json`. If a fixture intentionally fails, its failure purpose is documented there.

These fixtures do not contain DOCX output and do not claim Microsoft Word validation.
