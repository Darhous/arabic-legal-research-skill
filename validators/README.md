# Reviewer Contracts

This directory defines internal reviewer contracts for the Arabic Legal Research Production Skill.

These files are documentation contracts only. They are not executable validators, automated checks, or test implementations in Phase 2.

## Base Reviewer Contract

Each reviewer file must define:

- Reviewer name.
- Scope.
- Inputs.
- Preconditions.
- Checks.
- Evidence requirements.
- Severity levels.
- Decision outcomes.
- Required output structure.
- Task-memory fields updated.
- Re-run conditions.
- Limitations.
- Non-responsibilities.

## Required Output Structure

Each reviewer must return a structured result in this shape:

```yaml
reviewer: "<reviewer name>"
status: "PASS | FAIL"
decision: "PROCEED | REVISE | PAUSE | FAIL"
findings:
  - id: ""
    severity: "Critical | High | Medium | Low"
    description: ""
    evidence: ""
    affected_locations: []
    required_corrections: []
verification_required: []
task_memory_updates: []
rerun_required: true
limitations: []
```

This is a documented output contract, not an executable schema.

## Delivery Rule

The Skill must not deliver final work unless all required reviewer contracts return `PASS`.

If any reviewer returns `FAIL`, the workflow returns to correction or pauses for required user input.

## Responsibility Boundaries

- Citation reviewer checks claim-source integrity; footnote reviewer checks footnote relevance, placement requirements, and page linkage.
- Footnote reviewer checks footnote records; bibliography reviewer checks reference-list completeness and metadata.
- Formatting reviewer checks formatting plans and visible layout requirements; DOCX readiness reviewer checks generated DOCX evidence and Word-specific behavior.
- Plan reviewer protects approved plan structure; methodology reviewer checks research design and methodological completeness.
- Language reviewer checks Arabic academic style; methodology reviewer checks methodological substance.
- Final QA reviewer aggregates specialist results; it must not replace specialist reviewers.

## Reviewer Files

- `plan-reviewer.md`
- `methodology-reviewer.md`
- `language-reviewer.md`
- `citation-reviewer.md`
- `footnote-reviewer.md`
- `bibliography-reviewer.md`
- `formatting-reviewer.md`
- `docx-readiness-reviewer.md`
- `final-qa-reviewer.md`
