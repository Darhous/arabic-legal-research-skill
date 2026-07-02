# Language Reviewer

## Reviewer Name

Language Reviewer

## Scope

Validate formal Arabic legal academic style.

## Inputs

- Drafted introduction.
- Research body.
- Conclusion.
- Footnote text where relevant.
- `rules/language.md`.

## Preconditions

- Draft text exists.
- Required language is Arabic unless a user instruction says otherwise.

## Checks

- Objectivity.
- Legal academic tone.
- Avoidance of rhetorical, emotional, sarcastic, or self-praising language.
- Clarity without harmful compression.

## Evidence Requirements

- Affected passages or section references.
- Explanation of language risk.

## Pass Criteria

- Language is objective, precise, analytical, and legally disciplined.
- No rhetorical, emotional, sarcastic, mocking, or self-praising style appears.
- First-person expressions are limited and academically justified.
- Claims avoid unsupported absolute wording.
- Legal reasoning is clear enough for academic review.

## Fail Criteria

- Oratory or excitement style.
- Vague, inflated, or ambiguous expressions.
- Unnecessary verbosity.
- Harmful over-compression.
- Personal criticism not scientifically necessary.

## Severity Levels

- Critical: Language creates academic dishonesty or defamatory/personal attack risk.
- High: Tone is non-academic across a section.
- Medium: Repeated vague or overbroad wording.
- Low: Local style polish issue.

## Decision Outcomes

- `PROCEED` when style passes.
- `REVISE` when wording can be corrected internally.
- `PAUSE` only when user preference or institution language requirement is required.
- `FAIL` when final language quality is claimed despite blocking style defects.

## Required Correction Behavior

Rewrite defective passages in neutral academic Arabic and re-check.

## Task-Memory Fields Updated

- `reviewer_findings`
- `revision_history`
- `failed_gates`

## Re-run Conditions

Re-run after any substantive text rewrite.

## Limitations

This reviewer checks style and tone, not legal source verification.

## Non-Responsibilities

- Does not verify citations.
- Does not decide methodology completeness.
- Does not validate DOCX layout.

## Required Output Structure

```yaml
reviewer: "Language Reviewer"
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
