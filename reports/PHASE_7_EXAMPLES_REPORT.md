# PHASE 7 — Professional Examples Report

Date: 2026-07-03
Baseline commit: `a65b82e` (Phase 6 README)

## What Was Added

Five narrative example directories under `examples/`, each with `input.md` / `expected-output.md`
/ `notes.md`, paired with the corresponding `playbooks/`/`workflows/` guide:

- `examples/basic-legal-research/` — pairs with `playbooks/general-user.md` and
  `workflows/legal-research.md`; illustrative structure only (explicitly labeled as such in
  `notes.md`), using a jurisdiction-neutral topic (general contractual liability) to avoid implying
  a real national-law opinion.
- `examples/legal-memo/` — pairs with `workflows/legal-memo.md`; fictional facts, no cited article
  numbers (since none can be verified inside a static example), explicit closing disclaimer text
  required from the model.
- `examples/contract-review/` — pairs with `workflows/contract-review.md`; a short, clearly
  simplified illustrative contract, with review output tied to specific real clauses (no abstract
  commentary).
- `examples/bad-vs-good-output/` — pairs with `docs/framework-vs-skill.md`; side-by-side comparison
  of a rule-violating output (invented citation, invented quote, first-person absolute claims,
  `أولًا/ثانيًا` headings) against a compliant one, with a table mapping each violation to the
  specific rule file it breaks, plus real `legal-research-skill validate` commands against existing
  invalid fixtures (`hierarchy-level-jump.json`, `dangling-citation-source.json`) so a reader can
  see the executable check catch the same class of error.
- `examples/docx-artifact/` — pairs with `workflows/docx-production.md`. **This is the one example
  built from a real, captured tool run**, not hand-written illustrative text: `build-artifact` was
  actually executed against `examples/fixtures/valid/approved-plan-locked.json` during this phase,
  and `expected-output.md` reproduces the real `final_artifact_status`, `allowed_claims`,
  `prohibited_claims`, `word_evidence`, and validator/DOCX-check summary from that run.

`examples/README.md` was given a short new top section explaining the two kinds of content now in
the directory (narrative examples vs. the pre-existing Phase 3 JSON fixtures) without altering the
existing fixture documentation.

## Accuracy / Safety Check

- No example presents a fabricated citation, statute number, or case name as real; every invented
  detail in `bad-vs-good-output/` is explicitly flagged in its `notes.md` as intentionally
  fabricated for illustration.
- Every example repeats or links the "not legal advice" boundary at least once.
- `docx-artifact/expected-output.md` is the only file in this phase containing literal tool output,
  and it was captured from an actual `legal-research-skill build-artifact` run on this machine, not
  invented; the scratch output directory (`tests_tmp/examples-docx-artifact/`) was deleted after
  capture — no generated binary DOCX was committed, consistent with `CODEX.md`'s hygiene rule.

## Verification

```
link-resolution scan over examples/**/*.md   -> no missing relative targets
pytest -q                                     -> 233 passed, 1 skipped, coverage 96.12%
```

## Result

Every playbook/workflow now has a concrete, runnable-or-reproducible example next to it instead of
staying purely theoretical. Proceeding to Phase 8 (QA gate verification).
