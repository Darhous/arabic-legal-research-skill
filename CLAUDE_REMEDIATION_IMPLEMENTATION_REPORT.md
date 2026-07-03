# Remediation Implementation Report

## 1. Starting commit

`cef6c45375c4d45ca0b2f3e8b18474edf01f5ffc` (`main`, matches `origin/main` exactly at
the start of this task; working tree held only the five untracked
`CLAUDE_*` audit report files from the prior independent-audit session,
plus `reports/claude-independent-audit.json` — no tracked file was
modified).

## 2. Prior findings (from the independent audit)

13 findings: 1 Critical (CLI-1), 3 High (DOCX-1, WORD-1, ARCH-1), 5 Medium
(ARCH-2, ARCH-3, DOCX-2, REL-1, REL-2), 4 Low (CLI-2, SEC-1, SEC-2, DEP-1),
plus one disclosed-but-not-remediable item (LIC-1, no LICENSE file) and one
documentation nicety (ARCH-4, broad `except Exception` usage). Treated as
hypotheses, not facts, per this task's instructions.

## 3. Reproduction evidence

Every finding below was re-derived against the actual current code before
any fix was written — not copied from the prior report:

- **CLI-1**: reproduced directly. `render-docx` with `--output` equal to
  `--input` (on a scratch copy of a fixture, never a tracked file)
  overwrote the JSON input with binary DOCX content, exit code 0.
- **DOCX-1**: reproduced directly. Rendering a research state with
  `footnotes: []` produced a DOCX that `validate_docx()` rejected with
  `footnote_rtl_missing`, because the mandatory separator/continuation
  footnote entries never carry `w:bidi`.
- **WORD-1**: not independently re-triggered live (no real `DispatchEx`
  hang was forced in this session), but confirmed by code tracing that
  `word_pid` is only populated in `evidence` *after* `DispatchEx` returns,
  and the pre-dispatch snapshot (`before_dispatch`) was never persisted
  anywhere the parent process could read it after a timeout — so a genuine
  hang before `DispatchEx` returns would leave the parent with no way to
  identify the spawned process. CONFIRMED by static analysis, consistent
  with the project's own prior diagnostics showing this exact hang has
  occurred in this environment.
- **ARCH-1**: reproduced by tracing `loader.load_state()`: its manual
  `schema_version` comparison is preceded by `research_state_errors(data)`,
  which already raises for any schema violation including an unsupported
  `schema_version` (the schema's `const: "0.3.0"` constraint catches it).
  The manual check is provably unreachable, not merely unused by the CLI.
- **ARCH-2**: confirmed by reading `constants.py`: the worktree-schema
  override activates purely on path existence, with no integrity check, no
  logging, and no way to disable it.
- **ARCH-3**: confirmed `RenderConfig.created_at` defaults to a hardcoded
  literal (`"2026-07-02T00:00:00Z"`) used unconditionally by every
  production CLI invocation.
- **DOCX-2**: reproduced directly. A DOCX part containing `"a" * 5000`
  triggered `suspicious_compression_ratio` despite being entirely
  legitimate, low-risk content.
- **REL-1**: confirmed `.github/workflows/ci.yml` has no tag trigger and no
  publish step; no workflow anywhere builds or verifies release assets.
- **REL-2**: reproduced directly. Rebuilding the wheel from `main` and from
  a fresh `git worktree` of `v0.3.0` produced three different SHA-256
  hashes (release asset, main-build, tag-build); root-caused to
  `core.autocrlf=true` with no `.gitattributes`, confirmed content-identical
  after stripping `\r`.
- **CLI-2**: reproduced directly. `render-docx --output draft.txt`
  succeeded and wrote a valid DOCX (ZIP) under a non-`.docx` name.
- **SEC-1 / SEC-2**: confirmed by reading `ci.yml` and `pyproject.toml`.
- **DEP-1**: reproduced directly. Uninstalling `jsonschema` post-install
  and running `python -m legal_research_skill --help` raised a raw,
  unhandled `ModuleNotFoundError` traceback.
- **LIC-1**: confirmed no `LICENSE`/`LICENSE.md`/`LICENSE.txt` file exists;
  `gh repo view --json licenseInfo` returns `null`.

No finding was found to be a false positive. All 13 substantive findings
were CONFIRMED.

## 4. Findings confirmed

CLI-1, DOCX-1, WORD-1, ARCH-1, ARCH-2, ARCH-3, DOCX-2, REL-1, REL-2, CLI-2,
SEC-1, SEC-2, DEP-1 (13 of 13).

## 5. Findings rejected

None. (LIC-1 and ARCH-4 were confirmed as accurate observations but are not
"fixed" in the code-defect sense — see sections 18 and 25 below for why.)

## 6. Files changed

```
.github/workflows/ci.yml                          (pin actions, add permissions)
.github/workflows/release.yml                      (new)
.gitattributes                                      (new)
README.md                                           (license disclosure strengthened)
examples/fixtures/valid/approved-plan-locked.json   (line-ending renormalization only;
                                                      content byte-identical to HEAD)
pyproject.toml                                      (dependency bounds, entry point)
src/legal_research_skill/__main__.py                (guarded dependency import)
src/legal_research_skill/artifacts/manifest.py       (generated_at docstring)
src/legal_research_skill/cli.py                      (output-alias + extension guards)
src/legal_research_skill/constants.py                (schema-dir override redesign)
src/legal_research_skill/docx/render_model.py         (DEFAULT_BUILD_EPOCH constant + docs)
src/legal_research_skill/docx/renderer.py             (clarifying comment only)
src/legal_research_skill/docx/validation.py           (footnote logic + zip-bomb thresholds)
src/legal_research_skill/loader.py                    (removed dead version-check branch)
src/legal_research_skill/paths.py                     (new: shared path-safety helpers)
src/legal_research_skill/word/finalization.py          (robust alias check, extension, dir guard)
src/legal_research_skill/word/processes.py             (orphan-process recovery primitives)
src/legal_research_skill/word/runner.py                (timeout fallback recovery path)
src/legal_research_skill/word/worker.py                (persist pre-dispatch snapshot)
tests/unit/test_docx_validation_edges.py               (updated compression-ratio fixture size)
+ 15 new regression/unit test files (see section 19)
+ reports/claude-remediation-start-state.json (new)
```

No file outside this list was modified. No file was deleted.

## 7. Design decisions

- **Centralize path-safety logic once, reuse everywhere.** A new
  `src/legal_research_skill/paths.py` module holds `resolve_confined_path`,
  `is_same_file_target`, `has_extension`, and `WINDOWS_RESERVED_NAMES`,
  replacing duplicated logic that previously existed separately in
  `cli.py` and `word/finalization.py`.
- **Do not weaken the byte-reproducibility guarantee.** An initial attempt
  to fix ARCH-3 by defaulting `RenderConfig.created_at` to real wall-clock
  time broke two existing acceptance tests
  (`test_reproducibility_idempotency_and_no_temp_leakage`,
  `test_manifest_semantics_are_stable_except_expected_paths_and_timestamps`)
  that assert two independent CLI invocations of the same input produce
  byte-identical DOCX output and manifests. This is a deliberate, tested
  project guarantee, not an oversight — the fix was reverted to a
  documentation-only change (rename nothing, but clearly document the
  constant as a fixed build epoch, not a real timestamp).
- **Prefer minimal-risk fixes to "raw traceback on missing dependency."**
  Rather than restructuring `schema_validation.py`'s module-level
  `jsonschema` import (which is imported transitively by most of the
  codebase and would be a much larger blast radius), the fix defers and
  guards the import at the single entry point (`__main__.py`), and
  retargets both the `python -m` and console-script entry points there.
- **Version-check consolidation kept the schema-based check as
  authoritative**, not the reverse, because it is the actively tested path
  (`SchemaIntegrityValidator`, exercised by two pre-existing adversarial
  tests) and produces a structured `ValidationReport` finding rather than
  aborting with a raised exception — arguably better CLI UX. `load_state()`
  was simplified to rely on the same single check instead of duplicating it.
- **Schema-directory override: opt-in, not opt-out.** Rather than deleting
  the worktree-schema override entirely (losing a real, if narrow,
  development convenience), it now requires an explicit
  `LEGAL_RESEARCH_SKILL_USE_WORKTREE_SCHEMAS=1` environment variable *and*
  a `pyproject.toml` sanity check that the candidate directory is a genuine
  project checkout, closing the "unrelated ancestor directory" attack
  surface while keeping the feature available on purpose.

## 8. CLI overwrite fix (CLI-1)

`paths.is_same_file_target()` combines resolved-path equality (which is
already case-insensitive for `WindowsPath`, covering exact and
case-variant aliases even for a not-yet-created output path) with
`os.path.samefile()` (covering hardlink aliases once both paths exist).
`cli._safe_output_path()` now accepts an optional `input_path` and raises
`InputError` before any write occurs if the two would resolve to the same
file; `_render_docx`, `_validate` (via `_write_or_print`), `_finalize_word`,
and `_build_artifact` (via an explicit check on the derived `pre_word`
path) all call it. `word/finalization.py`'s pre-existing string-equality
check was upgraded to use the same shared helper.

## 9. DOCX footnote fix (DOCX-1)

`docx/validation.py::_footnote_findings` now only requires `w:bidi` on
footnotes whose ID is not one of the two OOXML-mandatory reserved IDs
(`-1` separator, `0` continuationSeparator). A genuinely footnote-free
document (only the two reserved entries present) now passes. While fixing
this, a second, previously-undetected gap was found and closed in the same
function family: a document whose `document.xml` contains
`w:footnoteReference` elements but whose package has **no**
`word/footnotes.xml` part at all was previously never flagged (the
footnote-checking code only runs `if footnotes is not None`, i.e. only if
the part exists). This now raises a new `footnotes_part_missing` finding.

## 10. Word process ownership fix (WORD-1)

`word/worker.py` now takes a `before_dispatch` process snapshot, derives
the set of pre-existing `winword.exe` PIDs from it (`winword_pids()`), and
persists that set plus a wall-clock `worker_started_at` timestamp to the
diagnostics JSONL file *before* calling `DispatchEx` — so this evidence
survives even if the worker process is killed mid-hang.
`word/processes.py` adds `process_creation_time()` (real `GetProcessTimes`
Win32 call) and `find_new_owned_word_processes()`, which diffs a fresh
`winword.exe` snapshot against the persisted pre-dispatch set and only
marks a candidate `ownership_verified=True` when: its executable resolves
to `winword.exe`, its creation time is not earlier than the worker's start
(with a 1-second slack for clock granularity), and it is the *only* new
candidate found (multiple simultaneous new `winword.exe` processes are
left unverified — ownership cannot be disambiguated from PID/timing
evidence alone, and the code deliberately does not guess).
`word/runner.py`'s timeout handler now falls back to this recovery path
whenever `word_pid` was never captured, and only calls
`terminate_owned_process` on verified candidates.

## 11. Version validation fix (ARCH-1)

`loader.load_state()` no longer duplicates the version check; it relies
solely on `research_state_errors()` (the JSON Schema `const` constraint),
matching the pipeline's own authoritative path. The now-fully-unused
`SUPPORTED_RESEARCH_SCHEMA_VERSION` constant was removed from
`constants.py`.

## 12. Schema override fix (ARCH-2)

See section 7. `constants.resolve_schemas_dir()` replaces the old
path-existence check; default mode always returns the packaged schema
directory. Overriding requires an explicit environment variable and a
`pyproject.toml`-presence sanity check on the candidate root.

## 13. Timestamp fix (ARCH-3)

Documentation-only (see section 7's rationale for why a behavioral change
was rejected). `render_model.py` now defines `DEFAULT_BUILD_EPOCH` as a
named, documented constant; `RenderConfig.created_at`, `renderer.py`'s
`_core_xml`, and `ArtifactManifest.generated_at` all carry comments/
docstrings clarifying it is a fixed build epoch, not a real generation
timestamp, unless a caller explicitly supplies one.

## 14. ZIP protection fix (DOCX-2)

`docx/validation.py::_compression_findings` now combines the existing
ratio threshold with: a `MIN_COMPRESSED_BYTES_FOR_RATIO_CHECK` floor (a
part's compressed size must exceed 4KB before its ratio is even
evaluated), a `MAX_PART_UNCOMPRESSED_BYTES` per-part cap (200MB,
independent of ratio), and a `MAX_TOTAL_UNCOMPRESSED_BYTES` cap across all
parts combined (500MB) to catch a bomb engineered to keep every individual
part's ratio innocuous.

## 15. Release workflow (REL-1)

New `.github/workflows/release.yml`, triggered on `push: tags: ["v*"]` and
`workflow_dispatch`. Builds and tests the tagged commit, builds the wheel,
runs the existing wheel-content smoke check, computes and records a
SHA-256 sum, runs an installed-wheel smoke test in an isolated venv outside
the repo (no `PYTHONPATH`), and uploads the wheel plus checksum as a
workflow artifact via `actions/upload-artifact`. It does **not** create a
GitHub Release and does **not** publish to PyPI — per this task's explicit
constraints, publishing remains a separate, deliberate, human-triggered
step. `permissions: contents: read` (least privilege); no secrets used.
Both this workflow and `ci.yml` now pin `actions/checkout` and
`actions/setup-python` to specific commit SHAs (resolved via `gh api
repos/actions/checkout/git/refs/tags/v4` etc., not guessed), not mutable
version tags.

## 16. Reproducibility changes (REL-2)

New `.gitattributes` pins tracked text files (`*.py`, `*.json`, `*.md`,
etc.) to `eol=lf`, independent of `core.autocrlf`. While verifying this, a
tracked fixture (`examples/fixtures/valid/approved-plan-locked.json`) was
found to already have CRLF line endings **on disk in this working tree**
(git's `status`/`diff` machinery was masking this via `core.autocrlf`
normalization during comparison — `git hash-object` on the working-tree
file matched the committed LF blob exactly). The file was rewritten to LF
directly (`\r\n` → `\n`), which produces the exact same git blob hash as
what is already committed — a pure line-ending fix with zero content
change, not a functional edit. Byte-for-byte reproducibility of the
*already-published* `v0.3.0` wheel asset remains unprovable retroactively
(see the updated Release Integrity report); this change prevents the
problem going forward for any future tag.

## 17. Dependency changes

`pyproject.toml`: `jsonschema>=4.22,<5`, `pytest>=8.0,<10`,
`pytest-cov>=5.0,<8`, `ruff>=0.5,<1` — floors unchanged, ceilings added at
the next major boundary above the versions actually in use
(jsonschema 4.26.0, pytest 9.1.1, pytest-cov 7.1.0, ruff 0.15.20), so no
currently-installed version is invalidated. No lockfile was introduced (a
library package intentionally does not pin exact versions).

## 18. Documentation changes

`README.md`'s "License Status" section gained one explicit sentence: being
a public GitHub repository does not, by itself, grant any right to reuse,
copy, modify, redistribute, or commercially use the code; without a
`LICENSE` file, all rights are reserved by default. No `LICENSE` file was
created (explicitly forbidden by this task's instructions) — this is a
documentation clarification, not a resolution of the underlying gap, and
is correctly tracked as **DEFERRED** below, not FIXED.

## 19. Tests added

15 new test files, 96 new test cases total:

| File | Tests | Covers |
|---|---|---|
| `tests/regression/test_output_path_safety.py` | 11 | CLI-1 |
| `tests/unit/test_paths.py` | 10 | shared `paths.py` module |
| `tests/regression/test_docx_footnote_validation.py` | 9 | DOCX-1 |
| `tests/regression/test_word_orphan_process_recovery.py` | 11 | WORD-1 |
| `tests/unit/test_processes_real_windows_api.py` | 8 | WORD-1 (real Win32 API calls) |
| `tests/regression/test_schema_version_validation.py` | 10 | ARCH-1 |
| `tests/regression/test_schema_directory_override.py` | 5 | ARCH-2 |
| `tests/regression/test_timestamp_labeling.py` | 3 | ARCH-3 |
| `tests/regression/test_zip_bomb_thresholds.py` | 10 | DOCX-2 |
| `tests/regression/test_line_ending_policy.py` | 7 | REL-2 |
| `tests/regression/test_output_extension_validation.py` | 6 | CLI-2 |
| `tests/regression/test_missing_dependency_error.py` | 2 | DEP-1 (process-isolated) |
| `tests/unit/test_docx_validation_edges.py` (updated) | — | compression-ratio fixture updated to still trigger past the new floor |

Every test asserts on observable behavior (exit codes, file contents/
hashes, structured findings) rather than matching a string in isolation.

## 20. Test results

`pytest` (full suite, from repo root): **233 passed, 1 skipped, 0 failed.**

## 21. Coverage

**96.12%** total (threshold: 95%, `--cov-fail-under=95`). Two modules
needed dedicated new tests to stay above the line after the new code was
added: `src/legal_research_skill/paths.py` (100%, via
`tests/unit/test_paths.py`) and `src/legal_research_skill/word/processes.py`
(90%, up from 74% at the start of this task, via
`tests/unit/test_processes_real_windows_api.py`, which exercises the real
Win32 API bodies against a disposable, safely-terminated child process
rather than mocking them out).

## 22. Ruff

`ruff format .` reformatted 9 files (all newly-added or newly-edited);
`ruff format --check .` and `ruff check .` both pass clean afterward.

## 23. Compileall

`python -m compileall src` — clean, no errors.

## 24. Packaging

Wheel rebuilt from the fixed working tree (`python -m build --wheel
--no-isolation`, `dist/arabic_legal_research_skill-0.3.0-py3-none-any.whl`).
Verified: no `tests_tmp/`, `.docx`, `__pycache__`, or temporary report files
inside the wheel; `entry_points.txt` correctly lists
`legal-research-skill = legal_research_skill.__main__:run`; `METADATA`
still reports `Version: 0.3.0` (unchanged, as required for this task).

## 25. Installed-wheel smoke

Installed into a fresh venv, invoked from outside the repo root, no
`PYTHONPATH`: `--help` (both `python -m legal_research_skill` and the
`legal-research-skill` console script), `import`, packaged-schema
resource resolution, `validate`, `render-docx`, `validate-docx`, and
`build-artifact` all succeeded. The rendered DOCX's SHA-256
(`4d410ebbde3bfa95bb3763ae3c18846869a101c489e07aa000a69de701ba7b33`)
matched the hash independently computed for the same fixture during the
original audit — confirming the byte-determinism guarantee survived every
fix in this remediation. Uninstalling `jsonschema` from this same venv and
re-running `--help` produced the clean, structured DEP-1 fix message
(exit code 3), not a raw traceback.

## 26. Clean worktree audit

See `CLAUDE_POST_REMEDIATION_ACCEPTANCE_REPORT.md` for the results of the
post-commit clean-worktree re-verification (compileall, ruff, pytest,
wheel build, installed-wheel smoke, structural artifact smoke, README
integrity, release-workflow YAML validity).

## 27. Remaining risks

- **WORD-1 is mitigated, not eliminated.** If more than one new
  `winword.exe` process appears simultaneously (a real hang plus an
  unrelated user-initiated Word launch in the same narrow window), the
  code correctly refuses to guess and leaves both running rather than
  risk killing the wrong one — meaning a genuine orphan can still survive
  in that specific ambiguous scenario. This is a deliberate safety
  trade-off (never kill on ambiguous evidence), not an oversight.
- **REL-1 does not retroactively verify the already-published `v0.3.0`
  wheel.** The new release workflow only applies to future tags.
- **LIC-1 remains open by design** — no license was added, per explicit
  instruction. The project remains "all rights reserved" until the owner
  makes a deliberate licensing decision.
- **Byte-reproducibility of the `v0.3.0` release asset specifically**
  cannot be established after the fact; only future releases benefit from
  `.gitattributes`.

## 28. Recommended version action

**`v0.3.1` REQUIRED.** All three highest-severity findings (CLI-1, DOCX-1,
WORD-1) were real, reproducible defects present in the currently-published
`v0.3.0`, now fixed on `main` with regression coverage. `v0.3.0` should not
be moved or deleted; a new patch tag should be cut once this remediation
commit is reviewed and accepted.

## 29. Final verdict

See `CLAUDE_POST_REMEDIATION_ACCEPTANCE_REPORT.md`.
