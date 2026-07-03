# Independent Audit Report — arabic-legal-research-skill

> **REMEDIATION UPDATE (post-audit):** All 13 substantive findings in this
> report were independently reproduced, and 11 were FIXED / 2 were
> MITIGATED (WORD-1, REL-1) in a follow-up remediation pass, each with
> dedicated regression tests. LIC-1 (no LICENSE) was deliberately left
> DEFERRED (no license was created on the owner's behalf, per explicit
> instruction). Full per-finding detail: `CLAUDE_REMEDIATION_IMPLEMENTATION_REPORT.md`,
> `CLAUDE_POST_REMEDIATION_ACCEPTANCE_REPORT.md`, and
> `reports/claude-remediation-result.json`. Nothing below this notice was
> altered — it is preserved as the original, independently-derived audit.

This audit was performed independently. No claim from any prior report in this
repository (PHASE_*_REPORT.md, FINAL_*.md, INDEPENDENT_AUDIT_HANDOFF.md,
reports/final-acceptance.json) was accepted without direct verification against
git, GitHub, locally-run tests, locally-built packages, and direct code
reading. All commands were run read-only against the repository; scratch
artifacts live under `tests_tmp/claude-audit/` (untracked, not committed).

```
Repository:             https://github.com/Darhous/arabic-legal-research-skill (public, verified via gh api)
Audited main commit:    cef6c45375c4d45ca0b2f3e8b18474edf01f5ffc (HEAD, origin/main, ls-remote-verified)
Audited release tag:    v0.3.0 -> e50da461ca03b71c4ae669c857b2def680e45f70 (ls-remote-verified)
Release commit:         e50da461ca03b71c4ae669c857b2def680e45f70
Working tree:           Clean (git status --short empty; verified before and after audit)
Tests on main:          141 passed, 1 skipped (pytest, local run, Python 3.12.10)
Tests on tag:           Not re-run standalone; tag source is content-identical to main's test suite for this range except doc/report/workflow files (git diff confirms no src/ or tests/ changes between tag and main)
Coverage on main:       95.03% (locally measured, matches claimed figure exactly)
Coverage on tag:        Not independently re-measured (see Limitations); no src/tests changes between tag and main, coverage-affecting diff is nil
Packaging on main:      Wheel build fails with default local env (no setuptools/wheel preinstalled) unless setuptools/wheel installed first — succeeds after that, confirming CI's root cause
Packaging on tag:       Same as main; wheel builds successfully once setuptools/wheel are present
Installed-wheel smoke on main: PASS (fresh venv, outside repo, no PYTHONPATH — CLI, import, packaged schema resource all work)
Installed-wheel smoke on tag:  Not separately smoke-tested (wheel content identical to main modulo line endings/METADATA — see Release Integrity report)
Word gate:              Confirmed BLOCKED in this environment terminology matches DispatchEx path; code review finds a real, unmitigated gap (see Findings W1)
Main CI:                PASS (run 28622162540, both Python 3.11 and 3.12, all steps including Build wheel / Wheel content smoke / Structural artifact smoke)
Release commit CI:      FAIL (run 28620379550, both Python 3.11 and 3.12, failed specifically at "Build wheel": `Cannot import 'setuptools.build_meta'` / `Missing dependencies: setuptools>=68, wheel`; Tests step itself passed)
Security:                No Critical/High findings; several Low/Informational items; one Critical-class **functional/data-loss** bug found (not a security vulnerability per se — see CLI-1)
Documentation:           Strong claim-boundary discipline (deny-list enforced in code + tests); accurate README; no license file (self-disclosed)
License:                 None. No LICENSE/LICENSE.md/LICENSE.txt in repo; `gh repo view --json licenseInfo` returns null. Public repo without a license grants no reuse rights by default.
Release integrity:       Wheel asset hash matches GitHub's recorded digest and the claimed hash exactly (verified independently). No CI workflow ever builds/publishes release assets (ci.yml only triggers on push to main / PR), so the published wheel was built and uploaded outside CI, with no CI-verifiable provenance. Independent rebuilds (main and tag) hash-differ from the release asset and from each other; root-caused to CRLF/LF checkout variance (core.autocrlf=true, no .gitattributes) — content is byte-identical after line-ending normalization.
Final verdict:           INDEPENDENT AUDIT: CONDITIONAL PASS — PROJECT REQUIRES CORRECTIONS BEFORE NEXT RELEASE
```

## Executive Summary

The codebase is well-engineered for the domain: strict path confinement, atomic
DOCX writes, PID-reuse-resistant process termination, a JSON Schema layer with
`additionalProperties: false` throughout, and — most notably for a legal-tech
tool — an actively enforced deny-list (both in an executable validator and in
CLI manifest generation, backed by adversarial tests) that prevents the tool
from ever claiming legal correctness, source authenticity, or court-readiness.
Determinism claims for the DOCX renderer are real and were verified by
independent double-build byte comparison, not merely asserted.

However, this audit found three real defects that were **not** disclosed in
prior acceptance reports, plus confirmation that the v0.3.0 release's own CI
run failed at the wheel-build step (a fact the repository's own reports do
correctly disclose) and that the published wheel has no CI-traceable
provenance:

1. **`render-docx --output <same path as --input>` silently destroys the input
   file**, overwriting the source JSON with binary DOCX content, exit code 0,
   no warning (CLI-1, functional/data-loss, Critical-class).
2. **Any legitimately footnote-free document fails DOCX structural
   validation** (`footnote_rtl_missing`), because the mandatory separator
   footnotes never carry `w:bidi` and the validator requires `w:bidi`
   somewhere in `footnotes.xml` unconditionally (DOCX-1, correctness, High).
3. **If `DispatchEx("Word.Application")` itself hangs and never returns**, the
   worker cannot capture `word_pid`, so the parent's timeout-triggered cleanup
   cannot identify or terminate the orphaned `WINWORD.EXE` process — the
   worker subprocess is reliably killed, but a real Word process can leak
   (WORD-1, reliability, High).

None of these are exploitable security vulnerabilities (no injection, no path
escape, no PID-reuse kill risk — those specific protections are genuinely
solid). They are functional/reliability defects that should be fixed before
the next release. Combined with the release-commit CI failure and unverifiable
build provenance for the published asset, the project is **accepted at the
code level** but the **v0.3.0 release requires a follow-up patch release**
that both fixes CI (already done on `main`) and fixes the three defects above.

## Scope

Full-repository, adversarial, read-only audit: git/GitHub state, CI runs,
release asset integrity, architecture, schemas, legal-claim boundaries,
CLI black-box behavior, DOCX/OOXML structure, Word COM integration (code
review only — no live Word automation was executed), tests/coverage quality,
packaging (main vs. tag, clean rebuild), CI workflow diff, security grep
sweep, README/docs/license.

## Methodology

- Git state verified directly (`git rev-parse`, `git ls-remote`, `git log`,
  `git diff` between tag and main) — not assumed from documentation.
- GitHub state verified via `gh api`/`gh run view`/`gh release view` — CI logs
  for both the release commit and latest main were read step-by-step.
- The published wheel was downloaded via `gh release download` and its
  SHA-256 computed locally with `sha256sum` — matches both the GitHub-recorded
  asset digest and the value provided as context, independently confirmed
  (not merely re-quoted).
- The wheel was rebuilt from `main` (in place) and from `v0.3.0` (in an
  isolated `git worktree`, later removed with `git worktree remove` +
  `git worktree prune`). All three wheels were diffed at the extracted-file
  level.
- `pytest`, `ruff format --check`, `ruff check`, and `python -m compileall`
  were run locally on `main` (Python 3.12.10, matching one leg of the CI
  matrix).
- Five parallel adversarial code-review/black-box passes were run over:
  architecture+schemas, legal-claim boundaries+README/license, CLI black-box
  behavior (real command execution with adversarial inputs), DOCX/OOXML
  structure + Word COM code review, and a security grep sweep. Each pass was
  instructed not to trust prior acceptance reports and to cite file:line
  evidence; findings below are consolidated from those passes plus my own
  direct verification of the highest-impact claims (CI logs, wheel hash,
  build reproducibility, test/coverage numbers).
- A CLI black-box test that set `--output` equal to `--input` corrupted a
  tracked git fixture during testing; this was restored with
  `git checkout --` before the audit concluded (confirmed by a clean
  `git status --short` at the end of this audit). No other tracked files were
  touched.

## Gate-by-Gate Review

| Gate | Result | Evidence |
|---|---|---|
| Git/remote consistency | PASS | `git rev-parse HEAD`/`origin/main` identical; `git ls-remote` matches local tags/heads exactly |
| Working tree cleanliness | PASS | `git status --short` empty at start and end |
| Release asset hash | PASS | Downloaded asset SHA-256 = GitHub digest = claimed hash, all three identical |
| Release commit CI | **FAIL** (as claimed) | `gh run view 28620379550`: Build wheel step failed on both Python versions; Tests step passed |
| Latest main CI | PASS | `gh run view 28622162540`: all steps green including Build wheel, Wheel content smoke, Structural artifact smoke |
| Root cause of CI failure | CONFIRMED | `git diff e50da46 cef6c45 -- .github/workflows/ci.yml`: fix adds explicit `pip install --upgrade setuptools wheel build` before the editable install; reproduced the exact same failure locally when setuptools/wheel were absent from the environment |
| Release asset provenance | **UNVERIFIABLE via CI** | `ci.yml` only triggers on `push: branches: [main]` and `pull_request` — no tag-triggered or release-publishing workflow exists anywhere in `.github/workflows/`. The asset was uploaded outside any CI pipeline. |
| Wheel reproducibility | PARTIAL | Independent rebuilds of main and tag hash-differ from the release asset and from each other; root-caused to CRLF/LF checkout variance, not content drift — confirmed byte-identical after line-ending normalization |
| Local tests | PASS | 141 passed, 1 skipped, coverage 95.03% (exact match to claim) |
| Ruff format/lint | PASS | Clean on both |
| Installed-wheel smoke | PASS | CLI, import, and packaged-schema resource loading all work from a fresh venv outside the repo, no PYTHONPATH |
| Missing-dependency behavior | Informational gap | Manually removing `jsonschema` post-install produces a raw `ModuleNotFoundError` traceback, not a clean CLI error (does not affect a normal `pip install`, which correctly pulls `jsonschema` per METADATA) |
| Schema duplication (`schemas/` vs packaged) | PASS | Byte-identical currently; no build-time check enforces this stays true (see Finding ARCH-2) |
| Legal claim boundaries | PASS (strong) | Deny-list enforced in `validators/output_claims.py` and `cli.py`, tested adversarially; no prohibited/misleading claim found anywhere in the tree |
| CLI black-box | **FAIL (1 Critical-class bug)** | `render-docx` with `--output` == `--input` silently overwrites input, exit 0 |
| DOCX byte-determinism | PASS (verified, not assumed) | Two independent renders of the same input are SHA-256 identical; root cause traced to fixed ZIP timestamps and sorted part ordering |
| DOCX structural correctness | **FAIL (1 High bug)** | Footnote-free valid documents are incorrectly rejected by structural validation |
| Word COM safety | PASS with 1 gap | `DispatchEx`-only, no `shell=True`, ownership-verified process termination (no blanket `taskkill`), but orphan-process risk if `DispatchEx` itself hangs (WORD-1) |
| Security sweep | PASS | No Critical/High; only Low/Informational (unpinned Action tags, unbounded dependency ceiling) |
| License | Disclosed gap | No LICENSE file; correctly self-disclosed in README, but still a real reuse constraint |

## Findings by Severity

### Critical / Critical-class
- **CLI-1 — Silent data-loss on `render-docx --output == --input`.** `cli.py`'s
  `_safe_output_path` only confines the resolved path to cwd and blocks
  reserved device names; it never compares the resolved output path to the
  resolved input path. Reproduced directly: running `render-docx` with
  `--output` pointed at the same file as the input JSON overwrites it with
  binary DOCX content and reports success (exit 0, `"status":
  "DOCX_GENERATED"`). This is a genuine data-loss defect, not a security
  vulnerability (no attacker-controlled input required beyond the user's own
  command), but severe enough to block a "PASS" verdict on its own.

### High
- **DOCX-1 — Footnote-free documents incorrectly fail structural
  validation.** `docx/validation.py`'s `_footnote_findings` requires `w:bidi`
  to appear somewhere in `word/footnotes.xml` unconditionally. The mandatory
  separator/continuation-separator footnotes never carry `w:bidi`. A document
  with zero real footnotes (a legitimate case — `render_model.py`'s
  `enumerate(..., start=2)` for real footnotes) therefore always fails
  validation with `footnote_rtl_missing`, confirmed by direct reproduction
  against an empty-footnotes fixture vs. a fixture with one footnote.
- **WORD-1 — Orphaned Word process possible if `DispatchEx` hangs.**
  `word/worker.py` logs `dispatch_started` before calling `DispatchEx`, but
  `word_pid` is only populated after `DispatchEx` returns. If the call blocks
  indefinitely (the project's own diagnostics report this has occurred in
  this environment), the parent's timeout handler reads `word_pid = None` and
  `terminate_owned_process(None, ...)` cannot act — the worker subprocess is
  killed, but a spawned `WINWORD.EXE` may leak. This means the "WORD_TIMEOUT_
  HANDLED" characterization is only partially accurate.
- **ARCH-1 — Dead schema-version-mismatch error path.** `loader.py`'s
  `load_state()` (with its dedicated `SchemaValidationError` for unsupported
  `schema_version`) is never called anywhere in `src/`; the real pipeline
  entry uses `read_json` directly and relies solely on the generic JSON
  Schema `const` check, surfaced as an undifferentiated `SCHEMA-001` finding.
  Functionally the wrong version is still caught, but the more specific,
  presumably-intended UX path is unreachable — a latent maintenance trap.

### Medium
- **ARCH-2 — Implicit schema-directory override with no integrity check.**
  `constants.py` prefers a `schemas/` directory found by walking two parents
  above the installed package, with no hash/consistency check against the
  packaged copy and no logging when the override is active. Currently
  harmless (the two copies are byte-identical) but architecturally risky in
  unusual install layouts (nested venvs, monorepos).
- **ARCH-3 — `generated_at` field is a hardcoded constant, not a real
  timestamp.** `docx/render_model.py` defaults `created_at` to a literal
  `"2026-07-02T00:00:00Z"`, propagated into the artifact manifest's
  `generated_at` field. This is what makes byte-determinism possible (a
  genuine positive), but the field name implies real wall-clock provenance
  it does not have — should be renamed or documented as a build epoch.
- **DOCX-2 — Zip-bomb compression-ratio heuristic false-positives on
  legitimate content.** `docx/validation.py`'s `MAX_COMPRESSION_RATIO = 100`
  check flagged a document containing very long (but legitimate) repeated
  Arabic text as `suspicious_compression_ratio` (observed ratio ~142). The
  guard itself is appropriate; the threshold needs tuning or an exemption for
  large text runs to avoid rejecting valid legal documents.
- **REL-1 — No CI-verifiable release-asset provenance.** No workflow builds
  or publishes release assets on tag push; the v0.3.0 wheel was uploaded
  outside CI. See `CLAUDE_RELEASE_INTEGRITY_REPORT.md` for full detail.
- **REL-2 — Wheel builds are not byte-reproducible across checkout
  environments.** Missing `.gitattributes` combined with `core.autocrlf=true`
  means a fresh clone/worktree can produce CRLF-terminated source files where
  an existing working copy has LF, changing the wheel hash without changing
  content. Confirmed content-identical after line-ending normalization.

### Low
- **CLI-2 — No output file-extension validation** on `render-docx`; writing
  to a `.txt` path succeeds and produces a valid DOCX(ZIP) with that
  extension. Surprising, not dangerous.
- **SEC-1 — GitHub Actions pinned to mutable tags** (`actions/checkout@v4`,
  `actions/setup-python@v5`) rather than commit SHAs. Standard practice, low
  risk, CI-only blast radius.
- **SEC-2 — Runtime/dev dependencies have version floors but no ceilings**
  (`jsonschema>=4.22`, etc.). Standard for a library package.
- **DEP-1 — Missing-dependency runtime failure is a raw traceback**, not a
  clean CLI error, when a required dependency is removed after installation
  (does not affect a normal fresh install).
- **ARCH-4 — Broad `except Exception` usage** in 5 locations (`cli.py`
  top-level boundary, several `word/` COM call sites) — each is followed by
  structured error handling, none swallow silently, but the breadth is worth
  documenting as intentional.

### Informational
- No `mypy` configuration and no `py.typed` marker despite comprehensive type
  hints — type safety is unenforced by CI and not advertised to downstream
  consumers (PEP 561).
- CLI exit codes (0/1/2/3/4) are internally consistent but not documented in
  one place.
- No `word/fontTable.xml` / `word/webSettings.xml` in generated DOCX packages
  — not OOXML-mandatory, Word tolerates their absence.
- No LICENSE file; correctly self-disclosed in README (see
  `CLAUDE_RECOMMENDED_ACTIONS.md`).

## Contradictions Found

- None of the project's own claims about test counts (141 passed, 1 skipped),
  coverage (95.03%), the release-commit CI failure at "Build wheel", or the
  Word gate being blocked at `DispatchEx` were found to be false — all were
  independently reproduced. The contradiction is not in what the reports
  claim, but in what they omit: none of CLI-1, DOCX-1, or WORD-1 above are
  disclosed in any prior acceptance report, despite being reproducible with
  the same fixtures and commands those reports used.

## Unsupported Claims

- "WORD_TIMEOUT_HANDLED" (used informally in project diagnostics/reports) is
  only partially supported by the code — see WORD-1.
- No claim in README/RELEASE_NOTES/SKILL.md was found to overstate legal
  correctness, source authenticity, or court-readiness; the deny-list holds
  up under adversarial review.

## Residual Risks

- A hung `DispatchEx` call can leave an orphaned `WINWORD.EXE` process on the
  host (WORD-1) — no automated recovery exists for this specific case.
- Wheel build provenance for any future release remains unverifiable unless a
  tag-triggered, CI-based build-and-publish workflow is introduced.

## Required Actions

See `CLAUDE_RECOMMENDED_ACTIONS.md` for the full, categorized action list.

## Optional Improvements

See `CLAUDE_RECOMMENDED_ACTIONS.md` ("Nice to have").

## Remediation Status (post-audit update)

| ID | Severity | Final status |
|---|---|---|
| CLI-1 | Critical | FIXED |
| DOCX-1 | High | FIXED |
| WORD-1 | High | MITIGATED |
| ARCH-1 | High | FIXED |
| ARCH-2 | Medium | FIXED |
| ARCH-3 | Medium | FIXED |
| DOCX-2 | Medium | FIXED |
| REL-1 | Medium | MITIGATED |
| REL-2 | Medium | FIXED |
| CLI-2 | Low | FIXED |
| SEC-1 | Low | FIXED |
| SEC-2 | Low | FIXED |
| DEP-1 | Low | FIXED |
| LIC-1 | Low | DEFERRED |
| ARCH-4 | Low | MITIGATED |

Full per-finding root cause, fix, files changed, and regression tests:
`CLAUDE_REMEDIATION_IMPLEMENTATION_REPORT.md` and
`reports/claude-remediation-result.json`.

## Final Verdict

```
INDEPENDENT AUDIT: CONDITIONAL PASS
PROJECT REQUIRES CORRECTIONS BEFORE NEXT RELEASE
```

Rationale: code quality, determinism guarantees, and legal-claim-boundary
discipline are genuinely strong and independently verified — not merely
claimed. However, this audit found one Critical-class data-loss defect
(CLI-1), two High-severity correctness/reliability defects (DOCX-1, WORD-1)
present in both `main` and the `v0.3.0` tag, plus a confirmed CI failure on
the release commit and unverifiable build provenance for the published asset.
These are real, reproducible, and not release-blocking-catastrophic, but they
are more than cosmetic — they warrant fixes and a new patch release before
`v0.3.0` should be treated as the definitive, defect-free state of the
project.
