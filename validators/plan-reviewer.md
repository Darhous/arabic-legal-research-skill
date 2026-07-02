# Plan Reviewer

## Reviewer Name

Plan Reviewer

## Scope

Validate approved plan protection and body hierarchy compliance.

## Inputs

- User instructions.
- Uploaded approved professor plan.
- Proposed plan when no approved plan exists.
- Body hierarchy map.
- `rules/structure.md`.
- `rules/priority-hierarchy.md`.

## Preconditions

- Priority resolution is complete.
- Approved plan status is known.
- Body hierarchy map exists or is explicitly pending.

## Checks

- Approved plan preservation.
- Proposed plan permissibility when no approved plan exists.
- Restricted hierarchy compliance.
- Conflict handling under `rules/priority-hierarchy.md`.

## Evidence Requirements

- Exact approved heading text and order, if supplied.
- User instruction authorizing any plan change, if a change is made.
- Body hierarchy map.

## Pass Criteria

- Approved plan headings are preserved exactly.
- Approved heading order and nesting are preserved.
- No approved heading is renamed, deleted, merged, or reordered.
- If no approved plan exists, proposed plan is balanced and connected to the title.
- Body hierarchy uses only `قسم → باب → فصل → مبحث → مطلب` unless the user explicitly allows otherwise.

## Fail Criteria

- Approved plan was changed without explicit user instruction.
- Plan conflicts are ignored.
- Prohibited hierarchy levels appear without permission.
- Proposed plan does not cover the title or research problem.

## Severity Levels

- Critical: Confirmed approved plan is missing or altered without permission.
- High: Prohibited hierarchy appears without permission.
- Medium: Proposed plan is weak but recoverable.
- Low: Non-blocking clarity issue in plan documentation.

## Decision Outcomes

- `PROCEED` when pass criteria are met.
- `REVISE` when the plan can be corrected without external input.
- `PAUSE` when approved plan permission or missing plan input is required.
- `FAIL` when final plan compliance is claimed despite unresolved blocking issues.

## Required Correction Behavior

Restore approved headings exactly or pause for user permission to change them. Remove prohibited hierarchy levels unless explicitly requested.

## Task-Memory Fields Updated

- `approved_plan_status`
- `locked_plan_structure`
- `body_hierarchy_map`
- `failed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after any plan, hierarchy, title, or approved-plan permission change.

## Limitations

This reviewer does not judge citation support, legal language quality, or DOCX layout.

## Non-Responsibilities

- Does not validate source metadata.
- Does not validate bibliography entries.
- Does not approve formatting claims.

## Required Output Structure

```yaml
reviewer: "Plan Reviewer"
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
