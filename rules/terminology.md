# Canonical Terminology

Use these terms consistently across the repository.

## Terms

- Rule: A normative requirement stored under `rules/`.
- Checklist: A human-readable review list under `checklists/`; not executable.
- Reviewer Contract: A documented internal reviewer specification under `validators/`; not executable in Phase 2.
- Validator: A generic term for validation responsibility. In Phase 2, use `Reviewer Contract` unless referring to future implementation.
- Executable Validator: Future code that automatically checks a rule or contract. None exists in Phase 2.
- Gate: A required pass/fail checkpoint in the state machine.
- Decision: One of `PROCEED`, `REVISE`, `PAUSE`, or `FAIL`.
- State: A named phase in `rules/decision-engine.md`.
- Task Memory: The explicit task-state record defined in `rules/task-memory.md`.
- Profile: Institution or style defaults under `profiles/`.
- Fixture: Future test/example input data. No fixture files exist in Phase 2.
- Generator: Future code that produces DOCX or other artifacts. No generator exists in Phase 2.
- Readiness Review: A documented assessment of whether a claim may be made.
- Manual Validation: Human inspection in Microsoft Word or an explicitly accepted equivalent for behavior that cannot be proven from Markdown alone.

## Verification Marker

`Requires Verification` is the canonical internal status marker.

Do not use variants such as:

- Require Verification
- Verification Required
- Needs Verification
- Unverified as a replacement marker
- يحتاج إلى تحقق as an internal marker
- يتطلب التحقق as an internal marker

Arabic-facing final disclosure may translate the status into prose, but task memory and reviewer contracts must retain `Requires Verification` until sufficient evidence permits removal.
