# Release Integrity Report — v0.3.0

> **REMEDIATION UPDATE (post-audit):** REL-1 (no CI-verified release
> provenance) is MITIGATED going forward — a new `.github/workflows/release.yml`
> now builds, tests, hashes, and uploads a wheel artifact on tag push (no
> auto-publish). REL-2 (non-reproducible builds) is FIXED going forward — a
> new `.gitattributes` pins tracked text files to `eol=lf`. Neither change
> retroactively establishes provenance or byte-reproducibility for the
> already-published `v0.3.0` asset described below; that historical gap is
> permanent and unresolvable after the fact. `v0.3.0` was NOT moved,
> deleted, or re-tagged. See `CLAUDE_REMEDIATION_IMPLEMENTATION_REPORT.md`
> section 15-16 and `reports/claude-remediation-result.json` for detail.

Independent verification only. All values below were re-derived directly from
git, GitHub, and local rebuilds — none were copied from prior project reports
without independent reproduction.

## Tag and Commit

- Tag `v0.3.0` → commit `e50da461ca03b71c4ae669c857b2def680e45f70`, confirmed
  via both local `git show-ref --tags` and `git ls-remote --tags origin`
  (identical values — no local/remote drift on this tag).
- `main` HEAD → commit `cef6c45375c4d45ca0b2f3e8b18474edf01f5ffc`, confirmed
  via `git rev-parse HEAD`, `git rev-parse origin/main`, and
  `git ls-remote --heads origin` (all identical).
- The `v0.3.0` tag targets `main` (`targetCommitish: "main"` per
  `gh release view`), i.e. it is one commit behind the current tip of `main`.
- `git diff e50da46 cef6c45 --stat` shows the only changes between the
  release commit and current `main` are: `.github/workflows/ci.yml` (1 line),
  and six documentation/report files (`FINAL_PROJECT_ACCEPTANCE_REPORT.md`,
  `FINAL_RELEASE_CHECKLIST.md`, `INDEPENDENT_AUDIT_HANDOFF.md`,
  `PHASE_6_IMPLEMENTATION_REPORT.md`, `PHASE_6_REVIEW_REPORT.md`,
  `reports/final-acceptance.json`). **No file under `src/`, `tests/`,
  `schemas/`, or `examples/` differs between the release commit and current
  `main`.** This is not a "tag conflict" in any sense — it is exactly what it
  looks like: a post-release documentation/CI-hygiene commit, with zero
  functional code drift.
- A second local tag, `checkpoint/phase5-conditional-accepted` (commit
  `6754707d78c07b303ad4b727560957fe43541304`), exists **locally only** — it
  was never pushed (`git ls-remote --tags origin` does not list it). Not a
  release-relevant artifact, but noted for completeness.

## CI

- Release-commit CI run (`28620379550`, triggered by the push of `e50da46`):
  **FAIL**. Both `test (3.11)` and `test (3.12)` jobs passed every step
  through `Tests`, then failed at `Build wheel` with:
  - Python 3.12: `pyproject_hooks._impl.BackendUnavailable: Cannot import
    'setuptools.build_meta'`
  - Python 3.11: `ERROR Missing dependencies: setuptools>=68, wheel`
  - `Wheel content smoke` and `Structural artifact smoke` were both `skipped`
    as a direct consequence.
- Latest main CI run (`28622162540`, triggered by push of `cef6c45`):
  **PASS**, all steps green on both Python versions, including Build wheel,
  Wheel content smoke, and Structural artifact smoke.
- Root cause, confirmed by diff and by local reproduction: at the release
  commit, `.github/workflows/ci.yml`'s "Install package and dev tools" step
  ran `pip install -e ".[dev]"` then `pip install build`, without ever
  explicitly ensuring `setuptools`/`wheel` were present for the
  `--no-isolation` build step. The fix commit adds
  `python -m pip install --upgrade setuptools wheel build` **before** the
  editable install. I reproduced the exact same failure locally (a fresh
  Python 3.12.10 install with no `setuptools`/`wheel` present) and confirmed
  the fix resolves it — this is a genuine, correctly-diagnosed, correctly-
  fixed CI environment defect, not a flaky/nondeterministic failure and not a
  defect in the shipped source code.

## Release Asset

- Asset: `arabic_legal_research_skill-0.3.0-py3-none-any.whl`, 68,470 bytes.
- SHA-256, computed independently after `gh release download v0.3.0`:
  `5d7a67cd936bacd770b15f6e5cb915f64d830d0834841ff2641f386758bfc246`
- This **matches exactly**: (a) the digest GitHub itself recorded for the
  asset (`gh release view ... --json assets` →
  `"digest":"sha256:5d7a67cd..."`), and (b) the hash provided as context for
  this audit. No tampering or corruption between upload and download.
- Release author: `Darhous` (repo owner), confirmed via
  `gh api repos/.../releases/tags/v0.3.0 --jq '.author.login'`.

## Build Provenance

- **No CI workflow in this repository builds or publishes release assets.**
  `.github/workflows/ci.yml` is the only workflow file present, and its
  trigger is `on: push: branches: ["main"]` and `pull_request` only — there
  is no `on: push: tags:` trigger and no step anywhere that runs
  `gh release create`/`upload-release-asset`/similar. This means: **the
  published v0.3.0 wheel was not built by CI at all.** It was built locally
  and uploaded manually/out-of-band by the release author. There is no
  CI-generated log, artifact, or attestation tying the published bytes to a
  specific, reproducible build step.
- Because the release-commit CI run failed at exactly the "Build wheel" step
  (see above), it is certain the published wheel was **not** an artifact
  salvaged from that failed CI run either — it must have come from a local
  build on the maintainer's machine.
- I independently rebuilt the wheel twice: once from the current `main`
  working tree in place, and once from `v0.3.0` in an isolated
  `git worktree` (removed afterward via `git worktree remove` +
  `git worktree prune`). Results:

  | Source | SHA-256 |
  |---|---|
  | Published release asset | `5d7a67cd936bacd770b15f6e5cb915f64d830d0834841ff2641f386758bfc246` |
  | Rebuilt from `main` (in place) | `3fc23f32b511a02ccd3779f14ce4e4f0fff16d99f810211c1e9654a793ace8be` |
  | Rebuilt from `v0.3.0` (clean worktree) | `3f50bd96aa8ee7354d9ef6a601be399a581d65b0e2742b633846e8f5c85774b1` |

  All three differ. Root cause, confirmed by extracting and diffing all three
  wheels file-by-file: the fresh `git worktree add v0.3.0` checkout produced
  **CRLF**-terminated Python source files, while the pre-existing `main`
  working tree has **LF**-only files for the same content, and the published
  release wheel also uses **LF**. This is caused by `core.autocrlf = true`
  (confirmed via `git config --get core.autocrlf`) with **no `.gitattributes`
  file** in the repository to pin text-file line endings — checkout behavior
  is therefore environment/history-dependent rather than deterministic. After
  stripping `\r` from all three copies of every differing file (e.g. `cli.py`,
  `docx/package.py`), the content is **byte-identical** across all three
  builds. There is no functional or content divergence — only a build-
  environment artifact.

- **Conclusion on provenance:** source-content provenance for the v0.3.0
  wheel is fully established (it matches current `main`/tag source exactly,
  modulo line endings). **Byte-for-byte build provenance cannot be
  established** — no CI log or reproducible-build attestation exists tying
  the exact published bytes to a specific commit/environment, and this
  audit's own rebuild attempts could not reproduce the exact byte sequence
  even from the correct commit, due to the line-ending issue above.

## Main/Tag Divergence Classification

The divergence between `main` (`cef6c45`) and the release tag (`e50da46`) is
correctly classified as: **expected post-release CI-hygiene and documentation
commit**. It is explicitly **not**: a tag conflict, a versioning defect, a
silent code change hidden behind a docs commit (verified via `git diff
--stat`: zero `src/`/`tests/`/`schemas/` changes), or evidence of any
intentional history rewrite.

## Versioning Recommendation

- **Do not force-move the `v0.3.0` tag.** It correctly and immutably points
  at the commit it was created from; moving it would rewrite published
  history that consumers may already reference.
- **A `v0.3.1` patch release is warranted**, for two independent reasons:
  1. The CI fix (setuptools/wheel install order) is real and already merged
     to `main`, but `v0.3.0`'s own CI run remains permanently red in GitHub's
     history — a new tag lets the release history reflect a green build.
  2. This audit found three additional defects (CLI-1 data-loss bug, DOCX-1
     footnote-validation false-rejection, WORD-1 orphan-process gap — see
     `CLAUDE_INDEPENDENT_AUDIT_REPORT.md`) present in both `main` and
     `v0.3.0` that should be fixed and released before v0.3.0 is treated as
     final/definitive.
- The v0.3.0 release itself should not be deleted (its asset is intact,
  correctly hashed, and installable), but its release notes or a pinned
  comment should note the known CI failure and point to the forthcoming
  patch release once available.
