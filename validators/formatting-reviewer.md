# Formatting Reviewer

## Reviewer Name

Formatting Reviewer

## Scope

Validate Arabic academic formatting requirements at the formatting-plan or artifact level before DOCX readiness review.

## Inputs

- Formatting plan.
- Selected output style.
- Uploaded Word template if any.
- Page setup.
- Heading map.
- Paragraph styles.
- `rules/formatting.md`.

## Preconditions

- Bibliography building is complete or explicitly not applicable.
- Formatting profile and template status are known.
- Required output type is known.

## Checks

- A4 and print-margin requirements.
- RTL requirements.
- Arabic font requirements.
- Heading and `مبحث` page-break requirements.
- Paragraph justification, indentation, and line spacing.
- Colored/black-and-white structural invariance.

## Evidence Requirements

- Formatting profile.
- Template authority if supplied.
- Heading map.
- Known limitations where DOCX generation is unavailable.

## Pass Criteria

- A4 page size is specified.
- Print-ready margins are specified.
- Arabic RTL applies throughout.
- Arabic academic font is selected.
- Page borders are planned or applied.
- Headings are centered and bold.
- Each `مبحث` starts on a new page.
- Paragraphs are justified, indented, and consistently spaced.
- Colored and black-and-white profiles preserve identical structure.

## Fail Criteria

- Missing A4 or margin settings.
- RTL not applied to Arabic content.
- `مبحث` page break missing.
- Heading style inconsistent.
- Profile changes alter structure.
- Plain text output is claimed to validate Word layout.

## Severity Levels

- Critical: Formatting claim would falsely imply print readiness.
- High: RTL, page setup, or `مبحث` page-break requirement missing.
- Medium: Font, spacing, or indentation requirement incomplete.
- Low: Non-blocking style inconsistency.

## Decision Outcomes

- `PROCEED` when formatting plan/artifact is adequate for the next gate.
- `REVISE` when formatting requirements can be corrected internally.
- `PAUSE` when a mandatory official template is missing.
- `FAIL` when print-ready formatting is claimed without validation evidence.

## Required Correction Behavior

Correct formatting plan or mark the output as not print-ready until DOCX tooling validates it.

## Task-Memory Fields Updated

- `formatting_profile`
- `formatting_status`
- `delivery_claims_prohibited`
- `failed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after template changes, profile changes, heading changes, pagination changes, or DOCX generation.

## Limitations

This reviewer does not prove generated DOCX behavior or Microsoft Word field behavior.

## Non-Responsibilities

- Does not verify citations.
- Does not validate bibliography metadata.
- Does not certify DOCX readiness.

## Required Output Structure

```yaml
reviewer: "Formatting Reviewer"
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
