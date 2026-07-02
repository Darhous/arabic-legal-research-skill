# Contributing

Contributions should preserve the repository's evidence-first contract.

## Local Checks

Run these before opening a pull request:

```bash
python -m compileall src
ruff format --check .
ruff check .
pytest
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
```

Use `tests_tmp/` or another ignored local directory for generated DOCX files.

## Contribution Rules

- Do not weaken the coverage threshold.
- Do not skip difficult tests to make a change pass.
- Do not add fabricated legal sources, citations, or reviewer results.
- Do not claim Microsoft Word success unless the real Word gate completes.
- Do not commit generated DOCX files, temporary diagnostics, caches, or secrets.
- Keep Arabic text encoded as UTF-8.

## Pull Requests

Include the changed behavior, commands run, test result, and any limitation that remains. If a change touches Word automation, include timeout and cleanup evidence.
