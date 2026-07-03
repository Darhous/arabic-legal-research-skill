# PHASE 6 — README Framework Landing Page Report

Date: 2026-07-03
Baseline commit: `5ad4006` (Phase 5 playbooks/workflows)

## Decision: Extend, Not Replace

Per the Phase 0 plan, the existing README (already a high-quality landing page from a previous
session) was **extended**, not regenerated from scratch, to avoid losing already-verified content:
the exact footer link order, the exact ready-made prompts, and the exact color palette.

## What Changed

- **Hero asset renamed and rebranded**: `assets/readme/hero.svg` → `assets/readme/hero-arabic-legal-framework.svg`
  (via `git mv`, history preserved). Title/desc updated to "Arabic Legal Research Skill Framework",
  and the on-image headline text now reads "Arabic Legal Research Skill Framework" /
  "مهارة البحث القانوني العربي — إطار عمل" / a tech-stack subline
  ("Skill + Schema + Executable Validators + DOCX Pipeline + Word Gate"). `README.md`'s hero
  `<img>` and `tests/acceptance/test_readme_integrity.py`'s `HERO` constant were both updated to
  the new path — no duplicate/orphaned asset left behind.
- **H1/H3 updated**: "Arabic Legal Research Skill" → "**Arabic Legal Research Skill Framework**";
  subtitle now "مهارة البحث القانوني العربي — إطار عمل متكامل".
- **Two new badges**: "Legal AI" and "Type: Framework", added to the existing badge row without
  removing any existing (real, non-fake) badge.
- **New "🧭 Skill vs Framework" section**: a 6-row table mapping each Framework layer (Skill
  instructions, JSON Schema, executable validators, DOCX renderer/validator, optional Word gate,
  automated tests) to its real file location, linking out to the four new `docs/*.md` files.
- **New "📚 أدلة الاستخدام حسب دورك (Playbooks)" section**: table linking all 5 `playbooks/*.md`.
- **New "🔧 سيناريوهات جاهزة (Workflows)" section**: table linking all 6 `workflows/*.md`, ending
  with the mandatory `final-review.md`.
- **Nav pills updated**: added anchors for "Skill vs Framework", "Playbooks", "Workflows".
- **Project structure tree/table expanded**: now lists `CLAUDE.md`, `GPT.md`, `docs/`, `prompts/`,
  `playbooks/`, `workflows/` alongside the existing entries, each with a one-line description.
- **Claude Code section**: now points to `CLAUDE.md` (the file Claude Code auto-reads) instead of
  only `SKILL.md`, and links `prompts/claude.md` for the full ready prompt.
- **ChatGPT/Claude no-install section and Codex section**: each now links to its dedicated
  `prompts/*.md` file for the fuller version with model-specific caveats.

## What Was NOT Changed

- Footer link order and exact signature markup (Instagram → LinkedIn → Facebook → WhatsApp →
  GitHub, `Designed &amp; Developed by <a href="mailto:ahmeddarhous@gmail.com">Ahmed Darhous</a>`)
  — untouched, still verified byte-for-byte by
  `tests/acceptance/test_readme_integrity.py::test_readme_footer_links_and_signature_are_exact`.
- Color palette (`#0B132B` / `#C9A227` / `#F8F5EC` / `#334155` / `#1E3A8A`) — unchanged, reused in
  the new badges and hero text.
- Developer install commands — unchanged, still match `pyproject.toml` exactly.
- License section, security section, contribution section — unchanged.

## Verification

```
pytest tests/acceptance/test_readme_integrity.py -q   -> 5 passed
pytest -q (full suite)                                -> 233 passed, 1 skipped, coverage 96.12%
ruff check .                                           -> All checks passed!
python -m compileall src -q                            -> clean
```

A standalone link-resolution script confirmed every relative Markdown link in `README.md` (all
`docs/`, `prompts/`, `playbooks/`, `workflows/` references included) resolves to an existing file
— zero missing targets.

## Result

README is now an explicit Framework landing page: it leads with the Framework badges and identity,
routes every reader (by model or by role) to a dedicated, deeper guide, and every install command
and internal link was re-verified against the live code and file tree. Proceeding to Phase 7
(practical examples).
