# PHASE 5 — Playbooks and Workflows Report

Date: 2026-07-03
Baseline commit: `8d20900` (Phase 4 model prompts)

## What Was Added

### `playbooks/` — role-based entry points (5 files)

- `general-user.md`, `student.md`, `lawyer.md`, `researcher.md`, `developer.md`.

Each follows the same structure: who it's for, when to use it, step-by-step execution, a ready
prompt, mistakes to avoid, and expected output — matching the user's exact required structure.
Role-specific caveats were added deliberately: `lawyer.md` warns against pasting real client data
into a public chat; `student.md` enforces the approved-plan protection rule from `SKILL.md`;
`researcher.md` and `developer.md` point to the real CLI commands (`schema-check`, `validate`,
`pytest`) rather than only text-only chat usage.

### `workflows/` — scenario-based procedures (6 files)

- `legal-research.md` — full academic research, staged section-by-section (matches the 13-state
  machine order already defined in `rules/decision-engine.md`/`SKILL.md`, without duplicating it).
- `legal-memo.md` — short legal memo/opinion drafting with a "structure first, then full drafting"
  discipline and a `checklists/citation-review.md` gate.
- `contract-review.md` — structural contract review with an explicit "this is not a legal opinion"
  boundary throughout.
- `case-analysis.md` — issue-spotting and balanced two-sided argument analysis for academic/prep
  use, explicitly not a verdict.
- `docx-production.md` — the real CLI pipeline (`schema-check` → `validate` → `render-docx` →
  `validate-docx` → `build-artifact` → optional `--require-word`), with the exact result states
  (`STRUCTURALLY_VALID`, `WORD_VALIDATED`, `NOT_AVAILABLE`, `TIMEOUT`, `FAILED`, `BLOCKED`) taken
  directly from `SKILL.md` §"Result states" and `cli.py`.
- `final-review.md` — mandatory last step for every other workflow; both a text-only chat path
  (apply all 4 `checklists/*.md` explicitly, no vague "looks good") and an executable path
  (`validate --fail-on warning`, `validate-docx`, `explain <RULE-ID>`).

## Accuracy Check

- All CLI commands in `docx-production.md` and `final-review.md` were verified against
  `src/legal_research_skill/cli.py`'s actual subcommands and flags (`--fail-on`, `--require-word`,
  `--word-timeout-seconds`, `--output-dir`, `--format`) — no invented flags.
- Result-state names match `SKILL.md` exactly.
- Every workflow/playbook explicitly repeats the no-legal-advice boundary rather than assuming the
  reader already read `LICENSE`/`docs/limitations.md`.

## Verification

```
ls playbooks/ workflows/   -> 5 + 6 files present as required
pytest                      -> not affected (no source code changed); no test references these
                                new docs by name
```

## Result

Every user role now has an actionable, non-theoretical entry point, and every common scenario has
a step-by-step workflow ending in the mandatory final-review gate. Proceeding to Phase 6 (README
rebuild as the framework landing page, which will link into all of `docs/`, `prompts/`,
`playbooks/`, and `workflows/`).
