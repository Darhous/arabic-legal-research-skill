# PHASE 3 — Framework Identity Report

Date: 2026-07-03
Baseline commit: `ce3a78c` (Phase 2 license verification)

## What Was Added

New `docs/` directory with four beginner-friendly Arabic documents, each grounded in the actual
code and rule files reviewed during Phase 0 (no invented capabilities):

- **`docs/framework-vs-skill.md`** — explains the difference between a plain "Skill" (text
  instructions a model reads) and this project's "Framework" positioning (Skill + JSON Schema +
  11 executable validators + DOCX renderer/validator + optional Word gate + tests + CI). Includes
  a comparison table mapping each layer to its actual file location in the repo.
- **`docs/architecture.md`** — a Mermaid flowchart of the full pipeline (Schema → Phase 3
  validators → DOCX renderer → structural validation → optional Word gate → artifact manifest),
  followed by a layer-by-layer breakdown of every module under `src/legal_research_skill/`
  (validators, docx, word) with the actual file names.
- **`docs/limitations.md`** — explicit, itemized limits: no legal advice, no real source-content
  verification (metadata completeness only), structural DOCX validation vs. real Word validation,
  `WORD_VALIDATED` semantics, Windows-only Word gate, no PyPI publish yet, ~96% test coverage
  meaning, and model non-determinism risk that the executable layer is designed to reduce.
- **`docs/quickstart.md`** — four usage paths (no-install chat, Claude Code, Codex, developer CLI)
  with the exact install commands already verified against `pyproject.toml` in the existing README,
  plus a role-based "next step" table.

## Source-of-Truth Check

Every capability claim in the four new files was cross-checked against:
- `SKILL.md` (methodology, state machine, output contract)
- `src/legal_research_skill/cli.py` (actual 8 subcommands, no others claimed)
- `src/legal_research_skill/validators/` (actual 11 validator modules, listed by real filename)
- `pyproject.toml` (install commands, Python floor `>=3.11`, entry point name)
- `LICENSE` (legal-advice disclaimer wording reused verbatim in `docs/limitations.md`)

No new capability, command, or guarantee was invented.

## Forward References (Resolved in Later Phases)

`docs/quickstart.md` links to `prompts/chatgpt.md`, `prompts/claude.md`, `prompts/codex.md`
(Phase 4) and `playbooks/*.md` (Phase 5), which do not exist yet at the end of this phase. This is
intentional — Phase 9's final audit will re-check every link across the whole doc set once all
phases are complete.

## Verification

```
git status --short   -> only 4 new files under docs/ plus this report
pytest                -> not re-run this phase (no source code touched)
```

## Result

Framework identity is now documented independently of README, in depth suitable for readers who
want to understand *why* this is a Framework and not just a prompt. Proceeding to Phase 4 (model
usage guides and ready prompts).
