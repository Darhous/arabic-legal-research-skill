# DOCX Readiness Reviewer

## Reviewer Name

DOCX Readiness Reviewer

## Scope

Validate whether a generated DOCX artifact exists and whether DOCX-specific claims are supported.

## Inputs

- Generated `.docx`, when available.
- DOCX validation report.
- Formatting reviewer result.
- Footnote reviewer result.
- Table of contents status.
- Page number status.
- `rules/output-contract.md`.

## Preconditions

- Formatting reviewer has run.
- Required output type is known.
- If a DOCX claim is requested, a DOCX artifact or explicit non-generation limitation exists.

## Checks

- DOCX artifact existence.
- Structural validation evidence.
- Microsoft Word or accepted equivalent behavior evidence.
- TOC, page numbers, footnotes, RTL, bibliography, appendices.
- Claim boundaries under `rules/output-contract.md`.

## Evidence Requirements

- Artifact path or explicit statement that generation was not performed.
- Validation report.
- Manual Word inspection result when Word-specific behavior is claimed.

## Pass Criteria

- DOCX file exists.
- DOCX opens successfully in Microsoft Word or accepted validator.
- Arabic RTL layout is validated.
- Footnotes are validated as bottom, RTL, right aligned.
- Footnote restart per page is validated or documented as a limitation.
- Table of contents exists and is updatable.
- Page numbers are present.
- Bibliography and appendices are correctly placed.

## Fail Criteria

- No DOCX file exists for a DOCX deliverable.
- Word-specific formatting is unvalidated.
- TOC is missing or stale without warning.
- Footnote behavior is claimed without validation.
- Output is plain text but called print-ready.

## Severity Levels

- Critical: Print-ready, final DOCX, or Word-compatible claim without evidence.
- High: DOCX requested but no artifact exists.
- Medium: Word-specific behavior requires manual validation.
- Low: Non-blocking readiness-report wording issue.

## Decision Outcomes

- `PROCEED` when DOCX readiness claim is supported.
- `REVISE` when readiness report wording or validation gaps can be corrected.
- `PAUSE` when a mandatory artifact/template must be supplied.
- `FAIL` when the requested final DOCX claim cannot be supported.

## Required Correction Behavior

Return to DOCX formatting preparation or clearly label output as non-final DOCX-ready source only.

## Task-Memory Fields Updated

- `formatting_status`
- `delivery_claims_allowed`
- `delivery_claims_prohibited`
- `failed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after DOCX generation, DOCX validation, TOC update, page-number update, footnote validation, or Word manual inspection.

## Limitations

This reviewer cannot pass print-ready claims when no DOCX artifact and Word/manual validation evidence exist.

## Non-Responsibilities

- Does not validate legal methodology.
- Does not verify citation authenticity.
- Does not replace final QA aggregation.

## Required Output Structure

```yaml
reviewer: "DOCX Readiness Reviewer"
status: "PASS | FAIL"
decision: "PROCEED | REVISE | PAUSE | FAIL"
findings: []
severity: "Critical | High | Medium | Low"
evidence: []
affected_locations: []
required_corrections: []
verification_required: []
task_memory_updates: []
rerun_required: true
limitations: []
```
