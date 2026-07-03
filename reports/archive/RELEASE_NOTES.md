# Release Notes - 0.3.0

## Summary

`arabic-legal-research-skill` 0.3.0 provides an executable Arabic legal research validation substrate with structural DOCX artifact generation.

## Included

- Research-state JSON Schema validation.
- Phase 3 validation pipeline and CLI reports.
- Arabic RTL DOCX generation.
- Structural DOCX package validation.
- Artifact manifest schema and hashes.
- Isolated Microsoft Word worker path with bounded timeout behavior.
- Wheel build and installed-wheel smoke verification.

## Quality

- Local Phase 6 result: `141 passed, 1 skipped`, coverage `95.03%`.
- Test suite target: coverage at or above 95%.
- Ruff formatting and linting are required.
- CI builds the package and runs a structural artifact smoke test.

## Known Limitations

- The real Microsoft Word gate is blocked on this machine at `DispatchEx("Word.Application")`.
- Structural validation is not a human legal review.
- Source authenticity and legal correctness are not externally verified by this tool.
- No PyPI publication is claimed for this release.
