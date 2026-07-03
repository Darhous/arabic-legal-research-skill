# Changelog

## Unreleased — Framework Upgrade (2026-07-03)

- Added `docs/{architecture,limitations,quickstart,framework-vs-skill}.md` documenting the
  Skill-vs-Framework identity and internal architecture.
- Added `GPT.md`, `CLAUDE.md`, and `prompts/{general-use,chatgpt,claude,codex}.md` with
  ready-to-copy, per-model usage prompts and hallucination/claim-boundary warnings.
- Added 5 `playbooks/*.md` (role-based guides) and 6 `workflows/*.md` (scenario procedures),
  each ending in a mandatory final-review gate.
- Rebuilt `README.md` as a Framework landing page (new badges, Skill-vs-Framework/Playbooks/
  Workflows sections, rebranded hero image at `assets/readme/hero-arabic-legal-framework.svg`)
  while preserving the exact footer, license section, and install commands.
- Added 5 narrative examples under `examples/` (`basic-legal-research`, `legal-memo`,
  `contract-review`, `bad-vs-good-output`, `docx-artifact`).
- Archived 14 historical phase/implementation reports to `reports/archive/`.
- No source code, schema, CLI surface, or CI workflow change. No API or behavior change.
  Full test suite unaffected (233 passed, 1 skipped, 96.12% coverage).

## 0.3.0 - 2026-07-02

- Added executable Phase 3 validation for Arabic legal research state.
- Added deterministic DOCX draft generation and structural OOXML validation.
- Added artifact manifest generation and schema checks.
- Added isolated Microsoft Word worker with timeout-bound failure handling.
- Added package data for runtime schema loading from installed wheels.
- Added end-to-end, adversarial, reproducibility, and cleanup tests.
- Added Phase 6 public repository readiness files and README integrity checks.

Known limitation: real Microsoft Word automation is blocked in this environment at COM dispatch timeout.
