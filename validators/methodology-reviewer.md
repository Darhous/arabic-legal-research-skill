# Methodology Reviewer

## Reviewer Name

Methodology Reviewer

## Scope

Validate Arabic legal academic methodology and research-design completeness.

## Inputs

- Research title.
- Research problem.
- Objectives.
- Methodological introduction.
- Research design.
- Conclusion.
- `rules/police-academy-methodology.md`.
- `checklists/methodology-review.md`.

## Preconditions

- Priority resolution is complete.
- Plan reviewer has passed or plan status is explicitly not applicable.
- Research design exists.

## Checks

- Title adequacy.
- Research problem, objectives, importance, method, limits, questions, hypotheses, tools, concepts, difficulties, and plan.
- Conclusion linkage to body.
- Absence of decorative methodology sections.

## Evidence Requirements

- Methodological introduction component map.
- Research design notes.
- Body-to-conclusion linkage.

## Pass Criteria

- Title satisfies methodology requirements.
- Research problem is defined and connected to the title.
- Objectives, importance, limits, questions, hypotheses, method, tools, concepts, difficulties, and plan are present where required.
- Conclusion includes summary, results, and recommendations.
- Results and recommendations derive from the body.

## Fail Criteria

- Missing methodological introduction component.
- Generic or disconnected research problem.
- Unsupported results or recommendations.
- Methodology sections are decorative rather than functional.

## Severity Levels

- Critical: Missing research title or research problem.
- High: Missing required introduction component.
- Medium: Weak or generic methodological reasoning.
- Low: Minor wording issue that does not affect methodology.

## Decision Outcomes

- `PROCEED` when methodology is complete.
- `REVISE` when the Skill can strengthen methodology internally.
- `PAUSE` when missing title/topic/approved plan input blocks methodology.
- `FAIL` when methodology completion is claimed despite unresolved critical gaps.

## Required Correction Behavior

Revise missing or weak methodology components before body drafting or delivery.

## Task-Memory Fields Updated

- `methodology_components_status`
- `research_title`
- `assumptions`
- `failed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after changes to title, plan, introduction, design, body, conclusion, results, or recommendations.

## Limitations

This reviewer does not verify source authenticity or Word formatting.

## Non-Responsibilities

- Does not approve citations.
- Does not approve footnote counts.
- Does not validate DOCX generation.

## Required Output Structure

```yaml
reviewer: "Methodology Reviewer"
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
