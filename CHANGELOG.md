# Changelog

## 0.3.0 - 2026-07-02

- Added executable Phase 3 validation for Arabic legal research state.
- Added deterministic DOCX draft generation and structural OOXML validation.
- Added artifact manifest generation and schema checks.
- Added isolated Microsoft Word worker with timeout-bound failure handling.
- Added package data for runtime schema loading from installed wheels.
- Added end-to-end, adversarial, reproducibility, and cleanup tests.
- Added Phase 6 public repository readiness files and README integrity checks.

Known limitation: real Microsoft Word automation is blocked in this environment at COM dispatch timeout.
