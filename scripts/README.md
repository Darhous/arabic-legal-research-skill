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

Phase 4 DOCX artifact commands:

```bash
python -m legal_research_skill render-docx examples/fixtures/valid/approved-plan-locked.json --output tests_tmp/sample.docx
python -m legal_research_skill validate-docx tests_tmp/sample.docx --format json
python -m legal_research_skill finalize-word tests_tmp/sample.docx --output tests_tmp/sample.word.docx --word-timeout-seconds 60 --format json
python -m legal_research_skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/phase4-artifact
python -m legal_research_skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/phase4-artifact-word --require-word --word-timeout-seconds 60
```

Word automation is optional by default and requires Windows, Microsoft Word, and pywin32. `--require-word` makes the Word gate mandatory for `build-artifact`; unavailable Word, COM failure, or timeout returns a blocked external-gate result. The default timeout is 60 seconds. The implementation terminates only the isolated worker process on timeout and does not kill user Word sessions.

Exit codes:

- `0`: validation completed and no finding reached the selected threshold.
- `1`: validation completed and a finding reached the selected threshold.
- `2`: usage, configuration, or input error.
- `3`: unexpected internal execution error.

Additional Phase 4 exit-code behavior:

- `0`: DOCX artifact or requested Word gate succeeded.
- `1`: DOCX or artifact structural validation failed.
- `2`: usage, input, configuration, or unsafe path error.
- `3`: required Word gate was not available, timed out, or was blocked.
- `4`: Word automation failed unexpectedly after the gate was requested.

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

## DOCX and Word Caveat

Phase 4 can generate and structurally validate DOCX files. Microsoft Word validation is only claimed after the optional Word gate opens, updates, saves, reopens, and structurally validates the resulting DOCX. `WORD_VALIDATED` is not legal correctness review, human visual review, source authenticity verification, or print-ready certification.
