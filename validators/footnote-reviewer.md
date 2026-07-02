# Footnote Reviewer

## Reviewer Name

Footnote Reviewer

## Scope

Validate footnote relevance, page linkage, integrity, RTL requirements, and page-level footnote policy.

## Inputs

- Footnotes per page.
- Same-page content.
- Citation status.
- DOCX footnote settings when available.
- `rules/footnotes.md`.

## Preconditions

- Citation records exist or citation reviewer has identified pending citation gaps.
- Footnote records exist for pages where footnotes are required.
- Formatting or pagination assumptions are documented.

## Checks

- Same-page relevance.
- Two-footnotes-per-page policy where possible.
- Fake/decorative note prevention.
- RTL/right-side requirements.
- Per-page numbering restart claim boundaries.

## Evidence Requirements

- Page or section references.
- Footnote ids.
- Linked citation/source ids.
- Explanation for pages with fewer than two footnotes.

## Pass Criteria

- Every page has at least two relevant footnotes where possible.
- Footnotes relate directly to same-page content.
- Footnotes are not fake or decorative.
- Unverified footnotes are marked `Requires Verification`.
- Footnotes are RTL and right aligned.
- Per-page numbering restart is validated or limitation is reported.

## Fail Criteria

- Fake or decorative footnotes.
- Footnotes unrelated to same-page content.
- Too few footnotes without explanation.
- Unverified footnotes presented as verified.
- RTL or placement failure.
- Numbering restart claimed without validation.

## Severity Levels

- Critical: Fake footnotes or invented source data.
- High: Footnotes unrelated to same-page content.
- Medium: Count policy unmet with documented legitimate limitation.
- Low: Local footnote formatting issue.

## Decision Outcomes

- `PROCEED` when footnote rules pass.
- `REVISE` when notes can be linked, rewritten, or removed.
- `PAUSE` when source or pagination information is mandatory.
- `FAIL` when final footnote compliance is claimed without evidence.

## Required Correction Behavior

Remove fake notes, add real relevant notes where supported, mark unverifiable sources, or report legitimate limitations.

## Task-Memory Fields Updated

- `footnote_records`
- `verification_markers`
- `formatting_status`
- `failed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after pagination changes, footnote edits, citation changes, or DOCX footnote setting changes.

## Limitations

This reviewer cannot prove Microsoft Word bottom placement or per-page restart without DOCX/Word validation.

## Non-Responsibilities

- Does not verify full bibliography metadata.
- Does not judge methodology.
- Does not certify DOCX readiness.

## Required Output Structure

```yaml
reviewer: "Footnote Reviewer"
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
