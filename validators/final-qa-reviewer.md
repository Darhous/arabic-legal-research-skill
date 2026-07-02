# Final QA Reviewer

## Reviewer Name

Final QA Reviewer

## Scope

Aggregate specialist reviewer results and enforce the final output contract. This reviewer is not a substitute for specialist reviewers.

## Inputs

- All reviewer outputs.
- Final artifact.
- Final QA report.
- Task memory.
- `rules/output-contract.md`.
- `checklists/final-review.md`.

## Preconditions

- All required specialist reviewers have run.
- Task memory contains completed and failed gates.
- Output contract claim level is selected.

## Checks

- Specialist reviewer status aggregation.
- Output contract satisfaction.
- Claim boundaries.
- Disclosure of limitations and `Requires Verification` markers.
- No hidden blocking issue.

## Evidence Requirements

- Reviewer result list.
- Task-memory snapshot.
- Final artifact list.
- Limitations and prohibited claims list.

## Pass Criteria

- All required reviewers pass.
- Output contract is satisfied.
- Unverified sources are disclosed.
- Remaining limitations are disclosed.
- Final report states the exact claim level allowed by evidence.
- No blocking issue remains.

## Fail Criteria

- Any reviewer failed.
- Output contract is not satisfied.
- Missing final QA report.
- Hidden verification gaps.
- Print-ready claim without DOCX validation.

## Severity Levels

- Critical: False final, print-ready, submission-ready, or all-sources-verified claim.
- High: Any required reviewer failed.
- Medium: Required limitation not disclosed.
- Low: Final report wording issue.

## Decision Outcomes

- `PROCEED` when delivery claim is supported.
- `REVISE` when final report wording or disclosures can be corrected.
- `PAUSE` when a blocking user decision remains.
- `FAIL` when requested final claim is impossible under current evidence.

## Required Correction Behavior

Block delivery as final. Return to the failed reviewer or ask the user for required input.

## Task-Memory Fields Updated

- `final_qa_status`
- `delivery_claims_allowed`
- `delivery_claims_prohibited`
- `failed_gates`
- `completed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after any specialist reviewer changes, artifact changes, verification-marker removal, or delivery-claim change.

## Limitations

Final QA aggregates evidence. It cannot make a failed specialist gate pass by assertion.

## Non-Responsibilities

- Does not independently verify legal sources.
- Does not independently validate Word layout.
- Does not rewrite approved plans.

## Required Output Structure

```yaml
reviewer: "Final QA Reviewer"
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
