# Bibliography Reviewer

## Reviewer Name

Bibliography Reviewer

## Scope

Validate references list completeness, metadata, and consistency with used sources.

## Inputs

- Used sources.
- Source inventory.
- Bibliography entries.
- Verification status.
- `rules/bibliography.md`.

## Preconditions

- Citation reviewer has produced citation/source records.
- Used source list exists.
- Bibliography draft exists or is explicitly pending.

## Checks

- Every cited source appears in bibliography.
- No unjustified unused bibliography entries.
- Metadata completeness.
- Internet source URL and access data.
- RTL formatting boundaries.

## Evidence Requirements

- Source ids.
- Bibliography entry locations.
- Missing metadata list.
- Verification marker list.

## Pass Criteria

- Every cited source appears in the bibliography.
- Bibliography entries contain enough metadata for review.
- Internet sources include URL and access date/time.
- Unverified sources are marked `Requires Verification`.
- Bibliography is RTL except for URLs and Latin identifiers.

## Fail Criteria

- Cited source missing from bibliography.
- Bibliography entry has no supporting citation and no reason for inclusion.
- Metadata is too incomplete.
- Internet metadata is missing.
- Unverified source is presented as verified.

## Severity Levels

- Critical: Fabricated bibliography entry.
- High: Used source missing from bibliography.
- Medium: Incomplete metadata marked for verification.
- Low: Ordering or formatting inconsistency.

## Decision Outcomes

- `PROCEED` when bibliography passes.
- `REVISE` when entries can be linked, removed, or marked.
- `PAUSE` when mandatory metadata must come from the user.
- `FAIL` when bibliography completeness is falsely claimed.

## Required Correction Behavior

Add missing entries, remove unsupported entries, complete metadata, or mark entries `Requires Verification`.

## Task-Memory Fields Updated

- `bibliography_records`
- `used_sources`
- `verification_markers`
- `failed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after any citation, source inventory, or bibliography entry change.

## Limitations

This reviewer does not verify footnote placement or methodology.

## Non-Responsibilities

- Does not decide whether a footnote is same-page relevant.
- Does not validate Word layout.
- Does not replace citation reviewer source-authenticity checks.

## Required Output Structure

```yaml
reviewer: "Bibliography Reviewer"
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
