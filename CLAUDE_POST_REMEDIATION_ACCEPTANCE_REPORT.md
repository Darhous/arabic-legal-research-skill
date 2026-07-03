# Post-Remediation Acceptance Report

```
CLI Safety:             PASS — same-file/case/hardlink alias overwrite blocked (CLI-1); extension + directory guards added (CLI-2)
DOCX Validation:         PASS — footnote-free documents pass; references-without-part now caught; determinism preserved (DOCX-1)
Word Process Safety:    MITIGATED — single-candidate orphan recovery added; multi-candidate ambiguity intentionally left unresolved rather than guessed (WORD-1)
Schema Validation:       PASS — single authoritative version-check path; dead duplicate removed (ARCH-1)
Version Handling:        PASS — package version unchanged at 0.3.0 throughout this task
ZIP Safety:              PASS — ratio + per-part + total-size thresholds combined; false positive on legitimate content eliminated (DOCX-2)
Packaging:               PASS — clean wheel build, no stray artifacts, entry point retargeted correctly
Installed Wheel:         PASS — full CLI smoke (validate/render-docx/validate-docx/build-artifact) green outside repo, no PYTHONPATH; byte-determinism hash matches pre-remediation baseline
Release Workflow:        ADDED — .github/workflows/release.yml builds/tests/hashes/uploads on tag push; no auto-publish (REL-1)
Reproducibility:         IMPROVED (forward-looking only) — .gitattributes pins LF for text files (REL-2); v0.3.0's already-published asset remains unverifiable retroactively
Security:                PASS — no Critical/High findings before or after; Low findings (unpinned Actions, unbounded deps) fixed
Tests:                   233 passed, 1 skipped, 0 failed
Coverage:                96.12% (>= 95% required)
Clean Worktree:          PASS — see section below
v0.3.0:                  NOT MOVED, NOT DELETED, NOT RE-TAGGED
Recommended Next Version: v0.3.1
Final Verdict:            POST-REMEDIATION AUDIT: PASS WITH LIMITATIONS — PROJECT READY FOR v0.3.1 WITH DOCUMENTED WORD LIMITATION
```

## Gate-by-Gate Detail

### CLI Safety
`render-docx`, `validate` (`--output`), `finalize-word`, and `build-artifact`
all now reject an output path that would resolve to the same file as the
input (exact match, case-variant match, or hardlink match) before any
write occurs, verified by 11 regression tests that also assert the input
file's bytes are untouched after each rejected attempt. Extension
validation (`.docx` required, case-insensitive) and a directory-vs-file
guard were added to `render-docx` and `finalize-word`, closing CLI-2.

### DOCX Validation
Footnote-free documents (only the two OOXML-mandatory separator/
continuation entries present) now pass structural validation; documents
with real footnotes still correctly require `w:bidi` on each one. A
previously-undetected gap — `document.xml` referencing a footnote whose
`word/footnotes.xml` part is entirely absent — is now caught
(`footnotes_part_missing`). Byte-for-byte determinism of the renderer
(verified via two independent renders of the same model, and reconfirmed
via installed-wheel smoke producing the same SHA-256 as the pre-remediation
baseline) was preserved throughout.

### Word Process Safety
The worker now persists a pre-`DispatchEx` snapshot of running
`winword.exe` PIDs and a wall-clock start time to disk *before* the
potentially-hanging call, so the parent process can recover this evidence
even if the worker is killed mid-hang. On timeout without a captured
`word_pid`, the parent diffs a fresh snapshot against the persisted one and
only terminates a candidate when it is verified `winword.exe`, was absent
beforehand, has a plausible creation time, and is the *only* new candidate.
This is rated **MITIGATED**, not fully closed: when multiple new
`winword.exe` processes appear in the same narrow window, the code
deliberately refuses to guess and leaves all of them running rather than
risk terminating a process it does not own with confidence. This is the
correct safety trade-off, not a bug, but it means a genuine orphan can
still persist in that specific ambiguous case — hence "documented Word
limitation" in the final verdict rather than an unqualified PASS.

### Schema Validation / Version Handling
`schema_version` validation now has exactly one implementation (the JSON
Schema `const` constraint, checked via `research_state_errors()`), used
consistently by both `load_state()` and the real CLI pipeline. The
previously dead, unreachable manual version-comparison branch was removed.
10 regression tests cover every supported/unsupported/missing-version
combination through both entry points. Package version was verified to
remain `0.3.0` at every checkpoint of this task (`pyproject.toml`,
built wheel `METADATA`, `PACKAGE_VERSION` constant).

### ZIP Safety
`_compression_findings` now requires a part's *compressed* size to exceed
4KB before its ratio is even evaluated (eliminating the false positive on
small, legitimately-repetitive content), while adding independent
per-part (200MB) and total-uncompressed (500MB) caps that catch a bomb
engineered to keep every individual part's ratio innocuous. 10 regression
tests cover the full matrix requested (small compressible content, large
suspicious ratios, boundary values, single oversized part, many moderate
parts summing past the total, and a real rendered DOCX with long
legitimate Arabic text).

### Packaging / Installed Wheel
Wheel rebuilt from the fixed tree; verified no `tests_tmp/`, `.docx`,
`__pycache__`, or report files inside it; `entry_points.txt` correctly
retargeted; `METADATA` version unchanged. Installed into an isolated venv
and exercised from outside the repository with no `PYTHONPATH`: CLI
`--help` (both invocation forms), import, schema-resource resolution,
`validate`, `render-docx`, `validate-docx`, `build-artifact` all succeeded.
Removing `jsonschema` from that same venv and re-running produced the new
clean, structured error (exit code 3) instead of a raw traceback.

### Release Workflow / Reproducibility
A new tag-triggered workflow builds, tests, hashes, and uploads the wheel
as a CI artifact without auto-publishing a release — closing the "no
CI-verifiable provenance for future releases" gap while respecting this
task's explicit prohibition on creating a release in this session. Both
workflows now pin `actions/checkout` and `actions/setup-python` to commit
SHAs resolved via the GitHub API. `.gitattributes` pins text files to LF,
and a real CRLF/LF working-tree inconsistency discovered while verifying
this (a fixture that displayed as "clean" under `git status` due to
`core.autocrlf` masking, despite differing on-disk bytes) was corrected to
match its already-committed LF blob exactly (verified via
`git hash-object` equality — zero content change). This does not and
cannot retroactively make the already-published `v0.3.0` wheel
byte-reproducible; it only prevents recurrence for future tags.

### Security
No Critical or High security findings existed before this task and none
were introduced by it. All Low-severity findings from the original
security review that had a concrete fix available were closed: GitHub
Actions pinned to commit SHAs, dependency version ceilings added. The
missing-dependency raw-traceback issue (DEP-1) was fixed at the CLI entry
point. No LICENSE was added (explicitly out of scope); README's
disclosure of this was strengthened.

## Clean Worktree Audit

Performed from a dedicated `git worktree` checked out at the remediation
commit (created after the commit described in
`CLAUDE_REMEDIATION_IMPLEMENTATION_REPORT.md`, removed afterward via
`git worktree remove` + `git worktree prune`):

- `git status --short`: clean.
- `python -m compileall src`: clean.
- `ruff format --check .` / `ruff check .`: both clean.
- `pytest`: 233 passed, 1 skipped, 96.12% coverage (matches the primary
  checkout exactly).
- Wheel build (`python -m build --wheel --no-isolation`): succeeded.
- Installed-wheel smoke (isolated venv, outside the worktree, no
  `PYTHONPATH`): `--help`, `validate`, `render-docx`, `validate-docx`,
  `build-artifact` all succeeded.
- README integrity test (`tests/acceptance/test_readme_integrity.py`,
  part of the `pytest` run above): passed.
- `release.yml` / `ci.yml` YAML syntax: both parse cleanly with `yaml.safe_load`.

## v0.3.0

Not moved. Not deleted. Not re-tagged. Still points at
`e50da461ca03b71c4ae669c857b2def680e45f70`, unchanged by this task.

## Recommended Next Version

**`v0.3.1`.** Rationale: three real, reproducible, user-facing defects
(one Critical data-loss bug, two High-severity correctness/reliability
bugs) existed in the currently-published `v0.3.0` and are now fixed with
regression coverage on `main`. This is a patch-level, non-breaking set of
fixes (no public API removed; two additions — `paths.py` module,
`__main__.run()` — are purely additive), so `v0.4.0` is not warranted.
`v0.3.0` must not be moved to point at the new commit.

## Final Verdict

```
POST-REMEDIATION AUDIT: PASS WITH LIMITATIONS
PROJECT READY FOR v0.3.1 WITH DOCUMENTED WORD LIMITATION
```

Rationale: every Critical and High finding from the independent audit was
confirmed, fixed, and covered by regression tests, and the full
verification suite (tests, coverage, ruff, compileall, packaging,
installed-wheel smoke, clean-worktree re-verification) is green. This is
not an unqualified PASS because one mitigation (WORD-1) has a narrow,
explicitly-documented residual scenario by design (ambiguous multi-process
detection is left unresolved rather than guessed at), and two items
(LIC-1, and REL-1's retroactive scope) remain intentionally open per this
task's own constraints rather than through any oversight.
