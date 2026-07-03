# Recommended Actions — arabic-legal-research-skill

Based on `CLAUDE_INDEPENDENT_AUDIT_REPORT.md`,
`CLAUDE_RELEASE_INTEGRITY_REPORT.md`, and `CLAUDE_SECURITY_FINDINGS.md`.
No fixes were applied as part of this audit — diagnosis is intentionally
separated from remediation.

> **REMEDIATION UPDATE (post-audit):** Every "Must fix" and "Should fix"
> item below with a concrete, safe implementation has now been applied
> (items 1-10 and 12 in "Should fix"), each with regression tests. Item 11
> ("Add an explicit LICENSE file") was deliberately **not** done — choosing
> a license is the project owner's decision, not something to be made on
> their behalf, per this task's own explicit instruction not to add a
> license. All "Do not do" items below were honored throughout the
> remediation: `v0.3.0` was not moved, no history was rewritten, and no new
> release/tag was created. See `CLAUDE_REMEDIATION_IMPLEMENTATION_REPORT.md`
> for what changed and why, and `reports/claude-remediation-result.json`
> for the per-item machine-readable status.

## Must fix before next release

1. **CLI-1 — Add an input-path vs. output-path equality check to
   `render-docx` (and any other command that both reads and writes files)
   before writing.** Currently `--output` pointed at the same path as the
   input silently overwrites the source JSON with binary DOCX content, exit
   code 0. This is a real data-loss defect.
2. **DOCX-1 — Fix `docx/validation.py`'s footnote validation so a
   footnote-free document is not required to have `w:bidi` on the
   separator/continuation-separator footnotes.** Either exempt those
   synthetic footnotes from the `w:bidi` requirement, or only enforce the
   requirement when real footnotes exist.
3. **WORD-1 — Give the Word worker a way to identify and clean up a
   `WINWORD.EXE` process spawned by a `DispatchEx` call that never returns.**
   At minimum, take a process snapshot immediately before calling
   `DispatchEx` and diff against a post-timeout snapshot to find new
   `winword.exe` processes, so ownership-verified cleanup can still run even
   when `word_pid` was never captured.
4. **Publish a v0.3.1 patch release** once the above are fixed, so the tagged
   release history reflects a passing CI run and does not carry these three
   defects forward as "accepted."

## Should fix

5. **REL-1 — Add a tag-triggered, CI-based release workflow** that builds
   and uploads the wheel as part of the `v*` tag push, so future release
   assets have CI-verifiable provenance instead of being built and uploaded
   out-of-band.
6. **REL-2 — Add a `.gitattributes` file** pinning `*.py`, `*.json`, and
   other text sources to `text eol=lf`, so wheel builds are byte-reproducible
   regardless of `core.autocrlf` or checkout history.
7. **ARCH-1 — Either wire `loader.load_state()`'s dedicated
   `SchemaValidationError` path into the real pipeline entry point, or remove
   it** — currently it is dead code that looks like the intended
   version-mismatch UX but is never reached.
8. **ARCH-2 — Add an explicit override signal (log line, `--no-worktree-
   schemas` flag, or a hash check) when the worktree-relative `schemas/`
   directory wins over the packaged copy**, so a future divergence between
   the two is visible rather than silent.
9. **ARCH-3 — Rename or document `generated_at`/`created_at`** in the render
   config and artifact manifest as a fixed build epoch, not a real
   generation timestamp, to avoid misleading anyone who treats it as audit
   evidence of when the artifact was actually produced.
10. **DOCX-2 — Tune or scope the `MAX_COMPRESSION_RATIO` zip-bomb heuristic**
    so legitimately long, repetitive Arabic text does not trigger a false
    `suspicious_compression_ratio` rejection.
11. **License — Add an explicit LICENSE file.** The repository is public
    with no license; this is already honestly disclosed in the README, but
    it remains a real constraint on reuse/redistribution for anyone who
    wants to build on this project, and should be resolved with an
    intentional choice rather than left as a permanent disclosure.

## Nice to have

12. Add a `py.typed` marker and a minimal `mypy` config to CI, given the
    codebase already carries comprehensive type hints — this would convert
    an unenforced convention into an enforced guarantee.
13. Document the CLI's exit-code contract (0/1/2/3/4) in one place (e.g. a
    table in README or a docstring on `main()`), rather than leaving callers
    to infer it from reading all of `cli.py`.
14. Pin GitHub Actions to full commit SHAs instead of `@v4`/`@v5` tags for
    incremental CI supply-chain hardening (Low risk today, cheap to fix).
15. Add an explicit upper bound or a lockfile for dependencies
    (`jsonschema`, dev tools) if reproducible CI environments become a
    priority.
16. Improve the missing-dependency runtime error (`jsonschema` absent) to
    fail with a clean, actionable message instead of a raw traceback — low
    priority since a normal install is unaffected.
17. Push (or delete) the local-only `checkpoint/phase5-conditional-accepted`
    tag — it currently exists only in the local clone that was audited and
    is invisible on the remote, which could confuse future audits or
    contributors who diff local vs. remote tags.

## Do not do

- **Do not force-move the `v0.3.0` tag.** It is correctly immutable and
  currently the correct historical pointer; moving it would rewrite
  published history that others may already depend on.
- **Do not rewrite published history** (no `git reset --hard` on shared
  branches, no force-push over `main` or the tag) to "fix" the release
  commit's CI failure retroactively — ship a new patch tag instead.
- **Do not delete the v0.3.0 GitHub Release** to hide the failed CI run —
  the asset is intact, correctly hashed, and installable; deleting it would
  remove a legitimate, currently-usable artifact. Annotate it and supersede
  it with v0.3.1 instead.
- **Do not treat CI-green on `main` as sufficient evidence that `v0.3.0` is
  "fine as published"** — the release commit's own CI run genuinely failed,
  and this audit found real defects independent of that CI issue; both need
  addressing before calling this release fully accepted.
