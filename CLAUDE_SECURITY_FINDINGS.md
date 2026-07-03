# Security Findings — arabic-legal-research-skill

> **REMEDIATION UPDATE (post-audit):** No Critical/High/Medium finding
> existed in this report, so none required fixing. The two Low findings
> with an available concrete fix were closed: SEC-1 (GitHub Actions pinned
> to mutable tags) — `actions/checkout` and `actions/setup-python` are now
> pinned to commit SHAs in both `ci.yml` and the new `release.yml`; SEC-2
> (unbounded dependency versions) — `pyproject.toml` now declares upper
> bounds. A related item discovered outside this report's original scope,
> DEP-1 (a missing required dependency produced a raw traceback instead of
> a clean error), was also fixed — see
> `CLAUDE_REMEDIATION_IMPLEMENTATION_REPORT.md` for detail. This did not
> change the security posture assessed below in any other way.

Scope: `src/legal_research_skill/` (all subpackages), `tests/`, `scripts/`
(if present), `.github/workflows/ci.yml`, `pyproject.toml`. Method: targeted
grep sweep for dangerous patterns (`eval(`, `exec(`, `pickle`, `os.system`,
`shell=True`, `subprocess`/`Popen`, `DispatchEx`/`Dispatch(`,
`TerminateProcess`/`OpenProcess`/`taskkill`, `requests`/`urllib`/`http(s)://`,
`tempfile`/`mktemp`, `extractall`/`ZipFile`, `symlink`, `.resolve(`), followed
by manual code reading of every match, plus a full independent read of
`word/processes.py`, `word/finalization.py`, `docx/validation.py`, and
`docx/package.py`. No live Microsoft Word automation was executed as part of
this security pass (code review only, per audit constraints). No exploit was
executed against a production system; all reproduction was local, read-only
where possible, and confined to `tests_tmp/claude-audit/`.

**This report does not state the codebase is "secure" in absolute terms.**
It states what was checked, what was found, and what remains unverified.

## Categories Checked

| Category | Verdict |
|---|---|
| Command injection | No issues found. Single `subprocess.Popen` call (`word/runner.py`), invoked with a list of arguments, no `shell=True` anywhere in `src/`. |
| Path traversal (CLI output paths) | No issues found. `cli.py`'s `_safe_output_path` and `word/finalization.py`'s path validation both confine resolved paths to cwd and block Windows reserved device names. Directly tested with `../`, absolute paths, and reserved names (`CON`, `NUL`) — all blocked with clean exit code 2. **Note:** this does not cover the separate CLI-1 data-loss finding (input==output overwrite), which is a missing check, not a traversal escape — see `CLAUDE_INDEPENDENT_AUDIT_REPORT.md`. |
| Zip Slip (write) | No issues found. DOCX package writer only ever writes a fixed, internally-defined set of part names — never derived from untrusted input. |
| Zip Slip (read) / malicious .docx | No issues found. `docx/validation.py` never extracts to disk; it reads zip entries into memory only, and explicitly rejects unsafe part names (absolute paths, `..`, backslashes) before any XML parsing. |
| Symlink escape / TOCTOU | No issues found. No explicit `is_symlink()` check exists, but `Path.resolve()` (used for all output-path validation) follows symlinks before the cwd-containment check runs, so a symlink pointing outside cwd would still be caught by that check. Not independently exploit-tested. |
| PID reuse / unsafe process termination | No issues found; a positive finding. `word/processes.py`'s `terminate_owned_process` only calls `TerminateProcess` when ownership is verified: the PID must resolve to `winword.exe` **and** must not have existed in a pre-dispatch process snapshot. No blanket `taskkill`/"kill all WINWORD.EXE" pattern exists anywhere in `src/` (grepped explicitly — zero matches). |
| Temp file races | No issues found. No `tempfile.mktemp` usage. Atomic replace pattern (`os.replace`) used for the final DOCX swap in `word/finalization.py`, with `finally`-block cleanup of the staging temp file. |
| XML external entity (XXE) | No issues found for the current threat model. `docx/validation.py` uses stdlib `xml.etree.ElementTree`, which does not resolve external entities/DTDs by default on the Python versions this project targets (>=3.11). This assumption would need re-verification if the project ever switches XML backends (e.g., to `lxml` with entity resolution enabled). |
| Zip bomb / oversized input | No issues found. `docx/validation.py` enforces a max package size, a max part count, and a max compression-ratio check before any XML parsing. `loader.py` caps JSON input at 5,000,000 bytes before `json.loads`. (Note: the compression-ratio check has a false-positive quality issue on legitimate long text — see DOCX-2 in the main audit report; this is a correctness/usability issue, not a security gap.) |
| Manifest hash tampering | No issues found; scope note only. `artifacts/manifest.py` computes SHA-256 over actual file content for traceability, but these hashes are not re-verified anywhere else in the pipeline to gate a trust decision — they are evidentiary/audit records, not an enforced integrity boundary. Not a vulnerability; noted so no one assumes stronger guarantees than exist. |
| Secrets / PII in source | None found. Grep for `api_key`, `secret`, `password`, `token`, `BEGIN PRIVATE KEY` across `src/` returned only unrelated variable/prose false positives. |
| Dependency declarations | No issues found beyond standard library-package practice (see Low findings). |
| GitHub Actions supply chain | No issues found beyond standard practice (see Low findings). |
| Outbound network calls | None found. No `requests`/`urllib`/hardcoded `http(s)://` calls anywhere in `src/` — this tool does not fetch anything from the network at runtime, consistent with its documented "no source authenticity verified online" disclaimer. |

## Findings

**Critical:** None.

**High:** None.

**Medium:** None.

**Low:**

1. **GitHub Actions pinned to mutable version tags, not commit SHAs.**
   `.github/workflows/ci.yml` uses `actions/checkout@v4` and
   `actions/setup-python@v5`. A compromised or re-tagged upstream action
   could inject code into CI runs. Impact is scoped to CI environment only
   (does not affect the shipped package). First-party GitHub actions, common
   and generally low-risk practice. Confidence: CONFIRMED.
2. **Runtime and dev dependencies are floor-pinned only** (`jsonschema>=4.22`,
   `pytest>=8.0`, etc.), with no upper bound. A future breaking or malicious
   upstream release could be pulled automatically on a fresh install.
   Standard practice for a library package. Confidence: CONFIRMED.

**Informational:**

1. No explicit `is_symlink()` rejection before path resolution in output-path
   validators — behavior is effectively safe today because `Path.resolve()`
   already follows symlinks before the cwd-containment check, but this
   reasoning was not independently exploit-tested (no symlink was actually
   planted and attacked during this audit).
2. Manifest hashes are evidentiary, not enforced elsewhere in the pipeline —
   see above.
3. `xml.etree.ElementTree`'s XXE-safe-by-default behavior is a property of
   the Python version, not an explicit hardening choice in this codebase; if
   the XML backend or minimum Python version ever changes, this must be
   re-verified.
4. Manually uninstalling a required dependency (`jsonschema`) after
   installation causes a raw, unhandled traceback rather than a clean CLI
   error. This does not affect a normal `pip install` (which correctly pulls
   the dependency per package metadata), so it is not rated above
   Informational, but it is a minor robustness gap.

## Limitations

- Real Microsoft Word COM automation was **not executed** as part of this
  security pass — findings on `word/` are based on static code tracing only,
  cross-referenced against the project's own diagnostics showing a real
  `DispatchEx` hang has occurred in this environment. The orphan-process risk
  (WORD-1 in the main audit report) is a reliability finding, not classified
  here as a security vulnerability, since it requires the Word gate to be
  explicitly invoked by the user and does not grant an attacker any new
  capability.
- Fuzzing, dependency-vulnerability scanning (e.g. `pip-audit`), and static
  analysis tooling (e.g. `bandit`, `semgrep`) were **not** run — this was a
  manual grep-and-read review only. Their absence does not imply the
  codebase would pass or fail such tools; it is simply out of this audit's
  executed scope.
- Symlink-escape and TOCTOU scenarios were reasoned about but not physically
  exploit-tested with a real symlink.
- This report should not be read as "the codebase is secure" in an absolute
  sense — only that the specific categories and patterns listed above were
  checked and, within this scope, no Critical/High/Medium issues were
  identified.
