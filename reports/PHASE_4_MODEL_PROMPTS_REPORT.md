# PHASE 4 — Model Usage Guides and Ready Prompts Report

Date: 2026-07-03
Baseline commit: `f3c069e` (Phase 3 framework identity)

## What Was Added

- **`GPT.md`** (new, root) — end-user guide for GPT-family models, short pointer set to
  `SKILL.md`/`rules/`/`checklists/`, a condensed ready prompt, and a strict-rules list (no invented
  sources, no premature print-ready/Word-validated claims, no legal-advice framing).
- **`CLAUDE.md`** (new, root) — end-user + Claude Code guide. This file is auto-loaded by Claude
  Code when it opens the repository as a working directory, so it doubles as the project's live
  operating contract for any future Claude Code session working on this repo: read `SKILL.md`
  first, prefer real CLI validation over text-only review when Python is available, never run Word
  automation outside the existing isolated worker, never create a git tag/release without explicit
  in-conversation authorization.
- **`prompts/general-use.md`** (new) — a model-agnostic ready prompt (works with any chat model that
  can read the repo link or pasted `SKILL.md` content), with an explicit hallucination warning and
  a required end-of-response disclosure (what was followed, what needs verification, what still
  needs human/legal review).
- **`prompts/chatgpt.md`** (new) — ChatGPT-specific usage steps, ready prompt, and ChatGPT-specific
  caveats (long-conversation instruction drift, browsing limitations, text-only layer vs. CLI).
- **`prompts/claude.md`** (new) — both Claude usage paths (plain chat vs. Claude Code) with a
  side-by-side comparison table of what each path can and cannot verify.
- **`prompts/codex.md`** (new) — Codex-specific usage steps and ready prompt, plus an explicit
  split between "use Codex to produce research" (points to `SKILL.md`) vs. "use Codex to develop
  the codebase" (points to `CODEX.md`).
- **`CODEX.md`** (modified, minimal) — added a two-line pointer near the top directing end-users
  who want the ready-made usage prompt to `prompts/codex.md`, clarifying `CODEX.md` itself remains
  the maintainer/development contract. No existing content removed or reworded.

All four `prompts/*.md` files and `GPT.md`/`CLAUDE.md` carry a non-rendering HTML attribution
comment at the top (`<!-- تصميم: أحمد درهوس ... -->`), consistent with the free/"لوجه الله"
licensing model — visible in source, invisible in rendered Markdown, no effect on content.

## Consistency Check

Every ready prompt in this phase explicitly requires: no invented sources/citations,
`Requires Verification` marking, the mandatory heading hierarchy, and a ban on declaring
print-ready/submission-ready/Word-validated without the actual gates in
`docs/limitations.md` / `rules/output-contract.md` passing. This matches `SKILL.md` and `LICENSE`
verbatim in spirit, avoiding any drift between what the prompts promise and what the code enforces.

## Verification

```
git status --short   -> new files under prompts/, GPT.md, CLAUDE.md, modified CODEX.md, this report
grep for CODEX.md/CLAUDE.md/GPT.md in tests/ -> no test depends on their exact content
```

No source code changed; test suite unaffected by this phase.

## Result

Every supported model (ChatGPT/GPT, Claude, Codex, and any generic model) now has a dedicated,
ready-to-copy usage guide with explicit hallucination and claim-boundary warnings. Proceeding to
Phase 5 (playbooks and workflows).
