# CODEX.md

This file tells Codex how to maintain and implement the `arabic-legal-research-skill` repository.

## Project Purpose

Build a serious open-source Claude Skill framework for producing Arabic legal academic research papers and preparing them for validated Microsoft Word delivery.

The repository must support:

- Claude Skill operation through `SKILL.md`.
- Codex development and maintenance.
- Modular methodology rules.
- Future Arabic RTL DOCX generation.
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

## Suggested Implementation Roadmap

1. Define a structured research source format, such as YAML or JSON, for title, metadata, plan, headings, paragraphs, citations, footnotes, and bibliography.
2. Implement a DOCX generator under `scripts/`.
3. Implement a DOCX validator that checks document structure, RTL settings, styles, margins, page sections, footnotes, bibliography, and table of contents requirements where technically possible.
4. Add tests under `tests/` for rule compliance, heading hierarchy, forbidden heading levels, citation markers, and style profile invariants.
5. Add minimal examples under `examples/`.
6. Add template assets under `templates/`.

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
- Do not commit generated binary DOCX files until the repository has a policy for fixtures and file size.
- Do not push automatically.
