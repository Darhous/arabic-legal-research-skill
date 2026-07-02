# Scripts

This directory contains no standalone scripts. Phase 3 implements validation tooling as an installable Python package and CLI under `src/legal_research_skill/`.

## Implemented CLI

Run the executable validators with:

```bash
python -m legal_research_skill validate examples/fixtures/valid/minimal-valid.json
legal-research-skill validate examples/fixtures/valid/minimal-valid.json
legal-research-skill schema-check examples/fixtures/valid/minimal-valid.json
legal-research-skill list-validators
legal-research-skill explain PLAN-001
```

Implemented `validate` options:

- `--format json`
- `--format text`
- `--output PATH`
- `--validator NAME`
- `--exclude-validator NAME`
- `--fail-on warning|low|medium|high|critical`
- `--show-passed`
- `--compact`

Exit codes:

- `0`: validation completed and no finding reached the selected threshold.
- `1`: validation completed and a finding reached the selected threshold.
- `2`: usage, configuration, or input error.
- `3`: unexpected internal execution error.

## Implemented Validators

The CLI runs executable validators for:

- Required data is missing.
- Approved plan headings are changed.
- Prohibited heading levels appear.
- Citations are missing or unverifiable.
- Footnotes are fake, unrelated, or insufficient without explanation.
- Bibliography metadata is incomplete.
- Output claims exceed evidence.
- State-machine gates are blocked or require reruns.

## DOCX Caveat

No DOCX generator, Word automation, or Word rendering validator exists in Phase 3. The CLI reports these as limitations rather than claiming print readiness.
