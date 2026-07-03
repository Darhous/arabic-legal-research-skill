# PHASE 0 — Full Repository Audit (Framework Upgrade)

Date: 2026-07-03
Scope: full repository review before starting the Framework Upgrade (Phases 0–10).
Starting commit: `9fc5adc` (`docs: redesign README as beginner-friendly landing page, add MIT license`)

## 1. Current Project State

- Package: `arabic-legal-research-skill` (import name `legal_research_skill`), version `0.3.0`, Python `>=3.11`.
- Single CLI entry point `legal-research-skill` with 8 subcommands: `validate`, `schema-check`,
  `list-validators`, `explain`, `render-docx`, `validate-docx`, `finalize-word`, `build-artifact`.
- Test suite: 233 passed / 1 skipped, coverage gate enforced at `--cov-fail-under=95`, currently ~96.1%.
- `LICENSE` present (MIT + Arabic "لوجه الله" dedication). `README.md` already rebuilt as a
  landing page in the previous session (hero SVG, badges, audience table, ChatGPT/Claude/Codex
  usage sections, developer install, Mermaid workflow, license section, fixed footer).
- CI (`ci.yml`) runs on Windows, matrix Python 3.11/3.12, actions pinned to commit SHA,
  `permissions: contents: read`, builds wheel, smoke-tests packaged schemas and a structural
  artifact build. `release.yml` is tag-triggered (`v*`), builds + hashes + uploads a CI artifact
  only — it does **not** create a GitHub Release or publish anywhere.
- `git status`: clean except a phantom "modified" flag on `reports/claude-independent-audit.json`
  caused by `core.autocrlf=true` interacting with the repo's `eol=lf` `.gitattributes` rule; byte
  content is identical to `HEAD` (verified: `git diff --raw` empty, byte counts equal). No real
  content change — safe to `git add` in Phase 1 to clear the stat-dirty flag.
- No open branches other than `main`; two lightweight tags exist: `v0.3.0` and
  `checkpoint/phase5-conditional-accepted`. Neither will be moved by this upgrade unless Phase 10
  explicitly creates a new tag after all gates pass.

## 2. Strengths

- Real executable substance behind every claim: JSON Schema validation (Draft 2020-12), 11
  structural/content validators (`src/legal_research_skill/validators/`), a deterministic DOCX
  renderer + OOXML structural validator, and an isolated, timeout-bound Microsoft Word COM worker
  with orphan-process recovery — this is not a prompt-only skill.
- Legal-claim discipline is enforced in code, not just prose: `WORD_VALIDATED` requires an actual
  Word round-trip; `validators/output_claims.py` and `rules/output-contract.md` block premature
  "print-ready"/"submission-ready" claims.
- CI is genuinely reproducible: SHA-pinned actions, `.gitattributes` line-ending policy, fixed
  build-epoch timestamps for byte-identical DOCX/manifest output, installed-wheel smoke test in an
  isolated venv outside the repo.
- Prior remediation work (this session's predecessor) already closed 15 audit findings with
  dedicated regression tests — the technical foundation is solid going into the Framework Upgrade.
- README is already close to landing-page quality: hero SVG, badge row, ChatGPT/Claude/Codex
  ready-made prompts, install steps that match `pyproject.toml` exactly, Mermaid diagrams.

## 3. Weaknesses / Gaps Relative to the "Framework" Positioning

- No `docs/` directory yet — no `architecture.md`, `limitations.md`, `quickstart.md`, or
  `framework-vs-skill.md` to explain the Skill-vs-Framework distinction the user wants to lead with.
- No dedicated `GPT.md`, `CLAUDE.md`, or `prompts/` directory — only `CODEX.md` (a maintainer guide,
  not an end-user model-usage guide) and prompt snippets embedded inline in `README.md`.
- No `playbooks/` or `workflows/` directories — role-specific usage paths (student, lawyer,
  researcher, developer, general user) are not documented as standalone, actionable guides.
- `examples/` currently only holds JSON Schema fixtures for tests
  (`examples/fixtures/valid|invalid/*.json`, `examples/fixtures/docx/*`) plus a short
  `examples/README.md`. There are no narrative, beginner-facing examples
  (`input.md` / `expected-output.md` / `notes.md`) for research/memo/contract-review scenarios.
- README does not yet explicitly frame the project as a "Framework" (badges, Skill-vs-Framework
  table, links to playbooks/workflows/docs) — Phase 6 will extend rather than discard the existing
  README.
- Root directory is cluttered with 14 historical phase/report Markdown files
  (`PHASE_2_REPORT.md` … `PHASE_6_REVIEW_REPORT.md`, `IMPLEMENTATION_REPORT.md`,
  `FINAL_PROJECT_ACCEPTANCE_REPORT.md`, `FINAL_RELEASE_CHECKLIST.md`,
  `INDEPENDENT_AUDIT_HANDOFF.md`, `RELEASE_NOTES.md`) from earlier development phases. These are
  historically valid evidence but hurt first-impression browsability of the repo root.
- `build/` (setuptools build cache) and `src/arabic_legal_research_skill.egg-info/` are present on
  disk but already git-ignored — no tracked artifact leakage, only local clutter.
- `.coverage`, `.ruff_cache/` also present locally and already ignored — no action needed beyond
  confirming `.gitignore` coverage (done, see below).

## 4. Files That Need Cleanup (Phase 1 candidates)

Move to `reports/archive/` (historical, superseded by later phases, safe to archive — not delete):

- `PHASE_2_REPORT.md`, `PHASE_2_ACCEPTANCE_REPORT.md`
- `PHASE_3_IMPLEMENTATION_REPORT.md`, `PHASE_3_ACCEPTANCE_REPORT.md`
- `PHASE_4_IMPLEMENTATION_REPORT.md`
- `PHASE_5_IMPLEMENTATION_REPORT.md`, `PHASE_5_ACCEPTANCE_REPORT.md`
- `PHASE_6_IMPLEMENTATION_REPORT.md`, `PHASE_6_REVIEW_REPORT.md`
- `IMPLEMENTATION_REPORT.md`
- `FINAL_PROJECT_ACCEPTANCE_REPORT.md`, `FINAL_RELEASE_CHECKLIST.md`
- `INDEPENDENT_AUDIT_HANDOFF.md`
- `RELEASE_NOTES.md` (superseded by `CHANGELOG.md`)

Not touched (kept at root — current/authoritative, referenced by README or actively load-bearing):

- `README.md`, `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- `SKILL.md`, `CODEX.md`
- `CLAUDE_INDEPENDENT_AUDIT_REPORT.md`, `CLAUDE_RELEASE_INTEGRITY_REPORT.md`,
  `CLAUDE_SECURITY_FINDINGS.md`, `CLAUDE_RECOMMENDED_ACTIONS.md`,
  `CLAUDE_REMEDIATION_IMPLEMENTATION_REPORT.md`, `CLAUDE_POST_REMEDIATION_ACCEPTANCE_REPORT.md`,
  `README_PROFESSIONAL_UPGRADE_REPORT.md` (most recent, still-referenced audit trail — kept at
  root per the "do not delete anything important without reason" rule; these are the most recent
  and complete evidence chain, unlike the older `PHASE_*` files which they superseded).

Local, git-ignored, no action required: `build/`, `src/arabic_legal_research_skill.egg-info/`,
`.coverage`, `.ruff_cache/`, `tests_tmp/`, `.claude/`.

## 5. Files That Must NOT Be Touched

- `examples/fixtures/**` — test fixtures with byte-exact content relied upon by
  `tests/regression/test_line_ending_policy.py` and reproducibility tests.
- `schemas/*.json` and `src/legal_research_skill/schemas/*.json` — canonical schema copies; must
  stay in sync (checked by tests).
- `rules/*.md`, `checklists/*.md`, `validators/*.md`, `profiles/*/profile.md`, `templates/README.md`
  — the methodology substance of `SKILL.md`; Phase 3–5 additions must reference these, not replace
  them.
- `pyproject.toml` version (`0.3.0`) and public CLI surface — no API/behavior change planned in this
  upgrade; it is documentation- and packaging-hygiene-only unless Phase 8 finds a real defect.
- `.git/`, any tag (`v0.3.0`, `checkpoint/phase5-conditional-accepted`) — no destructive git
  operations planned or permitted.

## 6. Risks for the Upgrade

- **Scope creep risk**: adding `docs/`, `prompts/`, `playbooks/`, `workflows/`, and expanded
  `examples/` is a large volume of new Markdown. Mitigation: every new file must describe only
  capabilities that exist in code today (verified against `SKILL.md`, `CODEX.md`, and
  `src/legal_research_skill/`); no invented features.
- **Claim-boundary risk**: "Framework" positioning must not imply the project performs legal advice,
  guarantees print-readiness, or guarantees `WORD_VALIDATED` without an actual Word round-trip.
  Mitigation: reuse the exact disclaimer language already present in `LICENSE` and `SKILL.md`
  §"Final Output Contract" everywhere the capability is described.
- **Coverage regression risk**: this upgrade is documentation-only for Phases 0–7; no source files
  under `src/` are expected to change, so the 95% coverage gate should be unaffected. Phase 8 will
  re-run the full gate to confirm.
- **README merge risk**: the existing README is already high quality. Phase 6 must extend it
  (Framework badges, Skill-vs-Framework table, links to new docs/playbooks/workflows) rather than
  regenerate it from scratch, to avoid losing already-verified content (exact footer link order,
  exact ready-made prompts, exact color palette).
- **Footer/attribution requirement**: this session's addition (Ahmed Darhous's identity/contact
  comment convention) must be applied consistently as a non-content-affecting HTML/Markdown
  comment or the existing footer block, never altering the technical meaning of any file.

## 7. Final Execution Plan (Phases 1–10)

1. **Phase 1 — Cleanup**: archive the 14 historical files listed in §4 into `reports/archive/`,
   clear the phantom CRLF diff on `reports/claude-independent-audit.json`, confirm `.gitignore`,
   run `pytest`. Commit + push.
2. **Phase 2 — LICENSE**: verify existing `LICENSE` already satisfies all "لوجه الله" MIT
   requirements (it does — confirmed by reading it in full during this audit); document rather than
   rewrite. Commit + push only if any adjustment is made.
3. **Phase 3 — Framework identity**: add `docs/architecture.md`, `docs/limitations.md`,
   `docs/quickstart.md`, `docs/framework-vs-skill.md` in simple Arabic, grounded in `SKILL.md`.
4. **Phase 4 — Model prompts**: add `GPT.md`, `CLAUDE.md`, `prompts/{chatgpt,claude,codex,general-use}.md`
   (`CODEX.md` already exists and stays as the maintainer-facing file; a user-facing Codex usage
   prompt goes in `prompts/codex.md`).
5. **Phase 5 — Playbooks/workflows**: add `playbooks/{general-user,student,lawyer,researcher,developer}.md`
   and `workflows/{legal-research,legal-memo,contract-review,case-analysis,docx-production,final-review}.md`.
6. **Phase 6 — README**: extend (not replace) the current README with Framework badges, a
   Skill-vs-Framework table, and links to the new docs/playbooks/workflows sections; re-verify all
   links, images, and install commands.
7. **Phase 7 — Examples**: add narrative examples under `examples/` (`basic-legal-research/`,
   `legal-memo/`, `contract-review/`, `bad-vs-good-output/`, `docx-artifact/`).
8. **Phase 8 — QA gates**: `pip install -e ".[dev]"`, `pytest`, `ruff format --check .`,
   `ruff check .`, `python -m compileall src`, `legal-research-skill list-validators`.
9. **Phase 9 — Final audit**: cross-check every new file against the live code/tests, write
   `FINAL_FRAMEWORK_UPGRADE_REPORT.md`.
10. **Phase 10 — Release**: update `CHANGELOG.md`; tag/release only if every gate is green and only
    after this is confirmed as in-scope for this run.

No `git reset --hard`, `push --force`, `rebase`, or destructive operation is planned or needed at
any phase.
