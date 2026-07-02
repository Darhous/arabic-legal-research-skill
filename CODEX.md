# CODEX.md

This file tells Codex how to maintain and implement the `arabic-legal-research-skill` repository.

## Project Purpose

Build a serious open-source Claude Skill framework for producing Arabic legal academic research papers and preparing them for validated Microsoft Word delivery.

The repository must support:

- Claude Skill operation through `SKILL.md`.
- Codex development and maintenance.
- Modular methodology rules.
- Arabic RTL DOCX generation and structural validation.
- Citation and footnote review contracts.
- Colored and black-and-white print profiles.
- Future automated tests for structure and formatting assumptions.
- Final quality review before any claim of success.

## Development Rules

- Keep `SKILL.md` as the central operating manual.
- Keep detailed rules modular under `rules/`.
- Keep institution assumptions under `profiles/`.
- Keep review gates under `checklists/`.
- Keep reviewer contracts under `validators/`; do not describe them as executable validators until code exists.
- Keep implementation notes under `scripts/`, `templates/`, `tests/`, and `examples/`.
- Do not bury operational rules in README only.
- Do not create prompt-only behavior where validation is required.
- Do not claim DOCX readiness unless generation and validation checks pass.
- Keep `schema_version`, `report_schema_version`, package version, and validator versions aligned.
- Add new rule IDs only through the central registry in `src/legal_research_skill/rules.py`.
- Keep reports deterministic; do not use unbounded timestamps or random IDs in validation output.
- Do not add silent defaults when loading research-state JSON; reject unsupported fields through schema validation.
- Keep tests and fixtures updated whenever schema paths, rule IDs, or validator behavior change.
- Do not allow unsupported claims such as print-ready, submission-ready, DOCX generated, Word-compatible, all citations verified, or automated legal validation without the required evidence.

## Suggested Implementation Roadmap

1. Keep the structured JSON research-state schema stable unless a migration is explicitly scoped.
2. Extend DOCX generation and validation through `src/legal_research_skill/docx/`.
3. Keep Microsoft Word automation isolated under `src/legal_research_skill/word/`; never run COM automation in the CLI process without timeout isolation.
4. Add tests under `tests/` for rule compliance, heading hierarchy, forbidden heading levels, citation markers, style profile invariants, DOCX package security, and Word gate failure modes.
5. Add minimal examples under `examples/`.
6. Add template assets under `templates/` only after a fixture policy exists.

## DOCX Implementation Guidance

Prefer a maintainable DOCX library that can control:

- Section page size and margins.
- RTL paragraph and run properties.
- Arabic fonts.
- Heading styles.
- Page borders.
- Footnotes and references.
- Page numbers.
- Table of contents fields.
- Bibliography section formatting.

Word-specific behavior, especially footnote numbering restart per page, may require:

- Low-level WordprocessingML changes.
- Section properties.
- Field updates in Microsoft Word.
- Post-generation validation by opening in Word or LibreOffice.

If tooling cannot enforce or verify a requirement, the script must emit a warning and the final report must mark the item as not validated.

Word automation must use an isolated worker process with `DispatchEx("Word.Application")`, a configurable timeout, and structured results. On timeout, terminate only the worker process. Do not call broad process-kill commands such as killing every `WINWORD.EXE`; that risks terminating the user's own Word sessions.

## Testing Expectations

Tests should cover:

- Required file presence.
- Required document order.
- Required methodological introduction components.
- Approved plan immutability.
- Allowed hierarchy: `قسم → باب → فصل → مبحث → مطلب`.
- Prohibited headings unless explicitly requested.
- Citation verification markers.
- Footnote minimum policy and fake-footnote prevention.
- Colored and black-and-white profile structural equivalence.
- Markdown rule references from `SKILL.md`.
- JSON Schema validation for research state and validation reports.
- Cross-reference, priority, approved-plan, hierarchy, methodology, citation, footnote, bibliography, verification-marker, output-claim, and gate-readiness validators.
- CLI exit codes and deterministic reports.
- DOCX structural validation reports, artifact manifests, Word timeout behavior, and optional Word gate CLI paths.

## Failure Policy

Codex must preserve these failure rules in scripts and tests:

- Missing mandatory data causes a clear failure or user question.
- Unverified source data is marked `Requires Verification`.
- The canonical priority order remains defined only in `rules/priority-hierarchy.md`.
- Approved plans are not changed without explicit user instruction.
- Fake references and decorative footnotes are forbidden.
- Final output is not called print-ready unless validation passes.

## Repository Hygiene

- Use UTF-8 Markdown.
- Preserve Arabic text accurately.
- Avoid secrets in examples, tests, fixtures, and reports.
- Keep examples minimal and clearly marked as illustrative.
- Do not commit generated binary DOCX files; keep smoke-test artifacts under ignored `tests_tmp/`.
- Do not push automatically.
