# Arabic Legal Research Production Skill

`arabic-legal-research-skill` is an open-source Claude Skill framework for producing Arabic legal academic research papers and preparing them for print-ready Microsoft Word delivery.

The repository is designed as a **Legal Research Production Operating System**, not a prompt-only writing aid. It defines staged execution, instruction priority, decision rules, task memory, internal reviewers, quality gates, and a final output contract.

## What It Does

- Guides Claude through a strict legal research production workflow.
- Audits user, university, course, professor, template, and methodology instructions before drafting.
- Protects approved professor research plans from accidental modification.
- Enforces Arabic legal academic methodology.
- Enforces the body hierarchy `قسم → باب → فصل → مبحث → مطلب`.
- Separates methodology, structure, language, citation, footnote, bibliography, formatting, and readiness rules.
- Requires internal reviewers to pass before final delivery.
- Treats unverified citations as `Requires Verification` instead of fabricating sources.
- Provides Phase 3 JSON Schema validation for structured research state.
- Provides Phase 3 executable text-level validators for schema integrity, cross references, priority decisions, approved plans, hierarchy, methodology, citations, footnotes, bibliography, verification markers, output claims, and gate readiness.
- Provides a Python CLI that emits machine-readable JSON reports and human-readable summaries.
- Generates deterministic Arabic RTL DOCX draft artifacts from validated research-state JSON.
- Validates generated DOCX packages structurally as OPC/OOXML.
- Optionally runs a Microsoft Word gate in an isolated worker process with a bounded timeout.

## What It Does Not Do

- It does not permit fake citations, decorative footnotes, or invented references.
- It does not rewrite approved professor plans unless the user explicitly requests that.
- It does not treat generic profiles as stronger than uploaded university instructions.
- It does not claim print readiness when DOCX formatting, footnotes, table of contents, or reviewer gates are unvalidated.
- It does not automate source authenticity checks over the internet.
- It does not determine legal correctness automatically.
- It does not claim Microsoft Word validation unless the optional Word gate opens, updates, saves, reopens, and structurally validates the DOCX.
- It does not claim print readiness or human legal acceptance in Phase 4.

## Methodological Basis

The first version encodes rules derived from:

**"الوجيز في مناهج البحث العلمي للدراسات القانونية والأمنية"**
Prepared by Dr. Ibrahim El-Shereai, Police Academy, 2024.

The guide defines scientific research as organized research efforts by a researcher to study a research problem using a scientific method, reaching results and recommendations under academic supervision.

The repository treats good legal academic research as depending on three connected dimensions:

- الموضوع
- الشكل
- المنهج

## Repository Layout

```text
.
├── SKILL.md
├── CODEX.md
├── IMPLEMENTATION_REPORT.md
├── PHASE_2_REPORT.md
├── PHASE_3_IMPLEMENTATION_REPORT.md
├── pyproject.toml
├── schemas/
│   ├── research-state.schema.json
│   ├── validation-report.schema.json
│   └── README.md
├── src/
│   └── legal_research_skill/
├── rules/
│   ├── decision-engine.md
│   ├── priority-hierarchy.md
│   ├── output-contract.md
│   ├── error-recovery.md
│   ├── task-memory.md
│   ├── terminology.md
│   ├── police-academy-methodology.md
│   ├── structure.md
│   ├── language.md
│   ├── citations.md
│   ├── footnotes.md
│   ├── formatting.md
│   └── bibliography.md
├── validators/
│   ├── README.md
│   ├── plan-reviewer.md
│   ├── methodology-reviewer.md
│   ├── language-reviewer.md
│   ├── citation-reviewer.md
│   ├── footnote-reviewer.md
│   ├── bibliography-reviewer.md
│   ├── formatting-reviewer.md
│   ├── docx-readiness-reviewer.md
│   └── final-qa-reviewer.md
├── checklists/
│   ├── final-review.md
│   ├── methodology-review.md
│   ├── citation-review.md
│   └── formatting-review.md
├── profiles/
│   ├── police-academy/profile.md
│   └── generic-arabic-university/profile.md
├── templates/
│   └── README.md
├── scripts/
│   └── README.md
├── tests/
│   ├── README.md
│   ├── integration/
│   ├── regression/
│   └── unit/
└── examples/
    ├── README.md
    └── fixtures/
```

## Operating Model

The Skill runs through strict phases:

1. Intake
2. Source and instruction audit
3. Priority resolution
4. Approved plan validation
5. Research design
6. Methodological introduction drafting
7. Body drafting
8. Citation and footnote integration
9. Bibliography building
10. DOCX formatting preparation
11. Internal review
12. Final QA
13. Delivery

No phase may start until the previous phase passes. Missing information, unresolved contradictions, insufficient sources, or failed review gates stop the workflow.

## Priority System

The canonical priority order is defined only in `rules/priority-hierarchy.md`. Other files must reference that rule instead of redefining a competing order.

## Required Research Order

Generated research documents must follow this order unless the user provides an explicit institution rule that overrides it:

1. Cover
2. Cover copy
3. Quran verse, Hadith, or quotation page
4. Dedication
5. Acknowledgements
6. Methodological introduction
7. Research body
8. Conclusion: summary, results, recommendations
9. References list
10. Appendices if any
11. Table of contents

## Body Hierarchy

Use only this hierarchy for the research body unless the user explicitly asks otherwise:

```text
قسم → باب → فصل → مبحث → مطلب
```

Do not use `فرع`, `بند`, `أولًا/ثانيًا`, numbers, letters, or symbols unless the user explicitly requests them.

## Core Failure Rules

The Skill must not claim success unless validation checks pass.

- If required research data is missing, ask the user.
- If the user supplies an approved research plan, treat it as mandatory.
- Do not change, reorder, delete, or rename approved plan headings unless the user explicitly requests it.
- Do not invent citations, footnotes, references, Hadith sources, Quran references, URLs, or access dates.
- If a source cannot be verified, mark it as `Requires Verification`.
- If DOCX footnote behavior cannot be validated in Word, mark the issue clearly in the final report.

## Internal Review System

The `validators/` folder defines reviewer roles for:

- Approved plan compliance.
- Methodology compliance.
- Academic language.
- Citation integrity.
- Footnote integrity.
- Bibliography completeness.
- Formatting readiness.
- DOCX readiness.
- Final QA.

The Skill must not deliver final work unless all required reviewers pass.

## Output Profiles

The repository defines two output style profiles:

- Colored print version.
- Black-and-white print version.

Both preserve the same academic structure and differ only in visual styling.

## Current Status

Phase 4 adds a DOCX artifact pipeline. It includes deterministic DOCX generation, structural OOXML validation, artifact manifests, and an optional Microsoft Word finalization gate.

Structural validation means the package, XML parts, relationships, styles, RTL properties, fields, page setup, and footnote links pass automated checks. Word validation is narrower and explicit: Microsoft Word must open the generated DOCX, update fields and TOC, repaginate, save, reopen, and then pass structural validation again.

The Word gate is optional by default. Use `--require-word` to make it mandatory for `build-artifact`. The default Word timeout is 60 seconds, and the implementation runs Word automation in a worker process so the CLI cannot hang indefinitely. The tool does not kill general user Word sessions.

Example commands:

```bash
python -m legal_research_skill render-docx examples/fixtures/valid/approved-plan-locked.json --output tests_tmp/sample.docx
python -m legal_research_skill validate-docx tests_tmp/sample.docx --format json
python -m legal_research_skill finalize-word tests_tmp/sample.docx --output tests_tmp/sample.word.docx --word-timeout-seconds 60 --format json
python -m legal_research_skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/phase4-artifact
python -m legal_research_skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/phase4-artifact-word --require-word --word-timeout-seconds 60
```

## Roadmap

- Phase 5: legal content expansion and review workflows that build on the Phase 4 artifact pipeline.
- Later phase: add template assets and release documentation.
- Later phase: perform the professional GitHub README visual redesign.

## Safety and Academic Integrity Notice

This repository is built for academic assistance and document production. It must preserve academic honesty. Users remain responsible for institutional compliance, source verification, and final submission decisions.

The Skill must never fabricate authorities, cases, laws, books, articles, Hadith references, Quran references, URLs, access dates, or page numbers.

## Limitations

- Current executable validation covers research-state structure, DOCX package structure, and bounded Word automation behavior.
- Microsoft Word validation requires Windows, Microsoft Word, and pywin32.
- CI and ordinary tests do not require Microsoft Word.
- `WORD_VALIDATED` does not mean human legal review, source authenticity verification, or print-ready acceptance.
- `print-ready` remains prohibited unless the current policy's structural, Word, and visual/human review gates are all satisfied.
