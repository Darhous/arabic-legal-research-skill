# Tests

This directory currently contains no executable tests. It documents the test coverage required before future automated validation claims can be made.

## Future Test Areas

- Required repository files exist.
- `SKILL.md` references all rule modules.
- Required document order is preserved.
- Methodological introduction components are present.
- Approved plan immutability is enforced.
- Only `قسم → باب → فصل → مبحث → مطلب` appears as body hierarchy.
- Prohibited body levels are rejected unless explicitly allowed.
- Citation rules distinguish direct and indirect quotation.
- Unverified sources are marked `Requires Verification`.
- Footnote policy prevents fake or decorative notes.
- Bibliography entries contain required metadata.
- Colored and black-and-white profile outputs preserve identical structure.
- DOCX formatting checks detect missing RTL, page size, margins, heading styles, and `مبحث` page breaks.

## Test Philosophy

Tests should verify behavior, not just file presence. When a requirement cannot be automatically verified, tests should require a clear warning in the generated QA report.

## Future Fixtures

Use minimal illustrative fixtures. Do not include copyrighted source excerpts or invented legal references presented as real sources.
