# Error Recovery Rules

This file defines safe recovery behavior for production failures. Silent recovery is forbidden when it changes an approved professor plan, user requirement, citation status, or delivery claim.

## Recovery Record Format

For each recovery event, update task memory with:

- Error id.
- Detection condition.
- Severity: `Critical`, `High`, `Medium`, or `Low`.
- Affected state.
- Recoverability: `Recoverable`, `Recoverable with user input`, or `Not recoverable under current contract`.
- Permitted action.
- Prohibited action.
- Reviewer re-run requirements.
- Allowed final disclosure.
- Escalation condition.

## Error Cases

### Missing Title

- Detection condition: No research title or topic is supplied.
- Severity: Critical.
- Affected state: Intake.
- Recoverability: Recoverable with user input.
- Permitted action: Return `PAUSE` and ask for the approved or intended title.
- Prohibited action: Invent a title and proceed as if approved.
- Task-memory update: `research_title=Missing`, add unresolved question.
- Reviewer re-run requirements: Methodology reviewer after title is supplied.
- Allowed final disclosure: Not applicable because delivery is blocked.
- Escalation condition: User refuses to supply a title while requesting a full paper.

### Missing Researcher Data

- Detection condition: Cover metadata is required but researcher data is missing.
- Severity: Medium.
- Affected state: Intake and DOCX formatting preparation.
- Recoverability: Recoverable with user input or draft placeholders.
- Permitted action: Ask for cover data or use labeled non-final placeholders.
- Prohibited action: Invent personal or institutional data.
- Task-memory update: Add missing cover fields and prohibited final claims.
- Reviewer re-run requirements: Formatting reviewer before delivery.
- Allowed final disclosure: "Cover metadata remains pending."
- Escalation condition: User requests final cover without supplying required data.

### Missing Professor or Course Data

- Detection condition: Supervisor, professor, course, or department data is required but missing.
- Severity: Medium.
- Affected state: Intake.
- Recoverability: Recoverable with user input.
- Permitted action: Ask for the missing academic metadata.
- Prohibited action: Present placeholders as final cover content.
- Task-memory update: Add unresolved question.
- Reviewer re-run requirements: Final QA reviewer.
- Allowed final disclosure: "Professor/course metadata is pending."
- Escalation condition: Required institutional metadata remains missing at delivery.

### Missing Required File

- Detection condition: User requires an uploaded file, source, plan, or template, but it is absent.
- Severity: High.
- Affected state: Source and instruction audit.
- Recoverability: Recoverable with user input.
- Permitted action: Return `PAUSE` and ask for the file or permission to proceed without it.
- Prohibited action: Pretend the missing file was reviewed.
- Task-memory update: `source_inventory` or `formatting_profile` marks missing file.
- Reviewer re-run requirements: Relevant reviewer after file is supplied.
- Allowed final disclosure: "Required file was not available; final claim withheld."
- Escalation condition: User demands compliance with a missing exclusive file.

### Unreadable File

- Detection condition: Required file exists but cannot be opened, decoded, or parsed.
- Severity: High.
- Affected state: Source and instruction audit.
- Recoverability: Recoverable with user input or alternate format.
- Permitted action: Ask for a readable copy or alternate format.
- Prohibited action: Infer file content from filename.
- Task-memory update: Record file path/name, read failure, and blocked gate.
- Reviewer re-run requirements: Source audit and affected reviewer.
- Allowed final disclosure: "File could not be reviewed."
- Escalation condition: File is mandatory and no readable copy is provided.

### Missing Approved Plan

- Detection condition: User confirms an approved plan exists but does not provide it.
- Severity: Critical.
- Affected state: Approved plan validation.
- Recoverability: Recoverable with user input.
- Permitted action: Return `PAUSE` and request the approved plan or explicit permission to propose one.
- Prohibited action: Replace an existing approved plan with a generated plan.
- Task-memory update: `approved_plan_status=Confirmed but missing`.
- Reviewer re-run requirements: Plan reviewer.
- Allowed final disclosure: Not applicable for final paper because delivery is blocked.
- Escalation condition: User requests body drafting while withholding mandatory plan.

### Incomplete Approved Plan

- Detection condition: Approved plan is missing levels, headings, or expected parts.
- Severity: High.
- Affected state: Approved plan validation.
- Recoverability: Recoverable with user input.
- Permitted action: Preserve supplied headings and ask whether additions may be proposed.
- Prohibited action: Silently add, rename, reorder, or delete approved headings.
- Task-memory update: `locked_plan_structure` plus gap notes.
- Reviewer re-run requirements: Plan reviewer.
- Allowed final disclosure: "Approved plan gaps were preserved/disclosed."
- Escalation condition: Gaps make the body impossible and user gives no instruction.

### Contradictory Plan

- Detection condition: Approved headings conflict, duplicate meaning, or violate required hierarchy.
- Severity: High.
- Affected state: Approved plan validation.
- Recoverability: Recoverable with user input.
- Permitted action: Ask whether to preserve exact wording or propose a corrected version.
- Prohibited action: Correct approved headings without permission.
- Task-memory update: Conflict log, selected action, and plan lock status.
- Reviewer re-run requirements: Plan reviewer and methodology reviewer.
- Allowed final disclosure: "Plan conflict preserved by user instruction" when applicable.
- Escalation condition: User requires exact preservation and strict hierarchy simultaneously where impossible.

### Instruction Conflict

- Detection condition: Instructions conflict after applying priority, specificity, and recency rules.
- Severity: High.
- Affected state: Priority resolution.
- Recoverability: Recoverable with clarification.
- Permitted action: Return `PAUSE` with the minimum clarifying question.
- Prohibited action: Choose arbitrarily or hide the conflict.
- Task-memory update: Conflict, authorities, selected resolution if any.
- Reviewer re-run requirements: Affected reviewer after resolution.
- Allowed final disclosure: "Instruction conflict resolved by [authority]."
- Escalation condition: Same-authority conflict remains unresolved.

### Title Does Not Match Content

- Detection condition: Draft plan or body no longer covers the approved title.
- Severity: High.
- Affected state: Research design or body drafting.
- Recoverability: Recoverable by revision.
- Permitted action: Return `REVISE` and align plan/body with the title.
- Prohibited action: Change an approved title without permission.
- Task-memory update: Failed methodology gate and revision history.
- Reviewer re-run requirements: Methodology reviewer and plan reviewer.
- Allowed final disclosure: Not needed if corrected.
- Escalation condition: Approved title and approved plan are irreconcilable.

### Too Few Sources

- Detection condition: Claims or sections lack enough source support.
- Severity: High.
- Affected state: Citation and footnote integration.
- Recoverability: Recoverable by adding sources, narrowing claims, or marking gaps.
- Permitted action: Limit claims, ask for more sources, or mark items `Requires Verification`.
- Prohibited action: Invent references or overstate unsupported conclusions.
- Task-memory update: Source gaps and verification markers.
- Reviewer re-run requirements: Citation reviewer and bibliography reviewer.
- Allowed final disclosure: "Some citations require verification."
- Escalation condition: User requires fully verified sources without supplying enough source material.

### Unverifiable Source

- Detection condition: Source details cannot be confirmed from supplied material.
- Severity: Medium.
- Affected state: Source audit, citation, bibliography.
- Recoverability: Recoverable with source evidence.
- Permitted action: Mark as `Requires Verification`.
- Prohibited action: Fill missing publication data, page numbers, URLs, or access dates from imagination.
- Task-memory update: `source_verification_status=Requires Verification`.
- Reviewer re-run requirements: Citation and bibliography reviewers after evidence is supplied.
- Allowed final disclosure: Arabic-facing disclosure that verification remains required.
- Escalation condition: User demands "all sources verified" despite unresolved markers.

### Incomplete Bibliographic Data

- Detection condition: Source lacks author, title, publisher, date, URL, or access date where required.
- Severity: Medium.
- Affected state: Bibliography building.
- Recoverability: Recoverable with metadata or marker.
- Permitted action: Request metadata or mark entry `Requires Verification`.
- Prohibited action: Invent missing metadata.
- Task-memory update: Bibliography record with missing fields.
- Reviewer re-run requirements: Bibliography reviewer.
- Allowed final disclosure: "Bibliographic metadata requires verification."
- Escalation condition: Submission requires complete metadata and it remains missing.

### Citation Without Source Record

- Detection condition: A citation appears without a matching source inventory record.
- Severity: High.
- Affected state: Citation and footnote integration.
- Recoverability: Recoverable by linking or removing citation.
- Permitted action: Create a source record from real supplied data or remove unsupported citation.
- Prohibited action: Leave orphan citation in final output.
- Task-memory update: Failed citation record.
- Reviewer re-run requirements: Citation and bibliography reviewers.
- Allowed final disclosure: Not acceptable for final output unless removed or marked.
- Escalation condition: Orphan citation cannot be resolved.

### Footnote Without Citation Linkage

- Detection condition: Footnote has no claim/source linkage.
- Severity: High.
- Affected state: Citation and footnote integration.
- Recoverability: Recoverable by linking, rewriting, or removing footnote.
- Permitted action: Link to same-page claim and source or remove decorative note.
- Prohibited action: Keep decorative footnote to satisfy count.
- Task-memory update: Footnote record failure.
- Reviewer re-run requirements: Footnote reviewer and citation reviewer.
- Allowed final disclosure: Footnote count limitation if removal reduces count.
- Escalation condition: Page footnote minimum cannot be met without fake notes.

### Unused Bibliography Entry

- Detection condition: Bibliography entry is not cited or otherwise justified.
- Severity: Medium.
- Affected state: Bibliography building.
- Recoverability: Recoverable by citation linkage or removal.
- Permitted action: Link to a real citation or remove from bibliography.
- Prohibited action: Pad bibliography with unused entries.
- Task-memory update: Bibliography record status.
- Reviewer re-run requirements: Bibliography reviewer.
- Allowed final disclosure: Not needed if corrected.
- Escalation condition: User demands unused bibliography padding.

### Used Source Missing from Bibliography

- Detection condition: A cited source has no bibliography entry.
- Severity: High.
- Affected state: Bibliography building.
- Recoverability: Recoverable.
- Permitted action: Add a real bibliography entry with metadata or marker.
- Prohibited action: Deliver final bibliography with cited source omitted.
- Task-memory update: Failed bibliography record.
- Reviewer re-run requirements: Bibliography reviewer.
- Allowed final disclosure: Not acceptable for final output unless corrected.
- Escalation condition: Metadata unavailable and no marker allowed.

### Missing Word Template

- Detection condition: User or institution requires a template that is not supplied.
- Severity: High.
- Affected state: DOCX formatting preparation.
- Recoverability: Recoverable with user input.
- Permitted action: Pause and ask for the template or permission to use defaults.
- Prohibited action: Claim compliance with a missing template.
- Task-memory update: `formatting_profile=Pending User`.
- Reviewer re-run requirements: Formatting reviewer and DOCX readiness reviewer.
- Allowed final disclosure: "Official template was not applied."
- Escalation condition: Template compliance is mandatory.

### DOCX Generation Unavailable

- Detection condition: No DOCX generator exists or generation is out of scope.
- Severity: Medium.
- Affected state: DOCX formatting preparation.
- Recoverability: Deferred implementation.
- Permitted action: Provide DOCX-ready source preparation and prohibit print-ready claims.
- Prohibited action: Claim DOCX generated, final DOCX, or print-ready.
- Task-memory update: `delivery_claims_prohibited` includes DOCX/print-ready claims.
- Reviewer re-run requirements: DOCX readiness reviewer must fail or mark not applicable for source-only output.
- Allowed final disclosure: "DOCX generation not performed."
- Escalation condition: User requires a generated DOCX in this phase.

### RTL Layout Uncertainty

- Detection condition: RTL layout cannot be inspected or validated.
- Severity: Medium.
- Affected state: Formatting preparation and DOCX readiness.
- Recoverability: Recoverable through rendering/Word inspection.
- Permitted action: Mark layout as requiring final inspection.
- Prohibited action: Claim correct RTL layout without evidence.
- Task-memory update: Formatting status and prohibited claims.
- Reviewer re-run requirements: Formatting reviewer and DOCX readiness reviewer.
- Allowed final disclosure: "Layout requires final Microsoft Word inspection."
- Escalation condition: User demands print-ready claim without inspection.

### TOC Field Not Updated

- Detection condition: TOC field is absent, stale, or not updatable.
- Severity: Medium.
- Affected state: DOCX readiness.
- Recoverability: Recoverable in Word or generator.
- Permitted action: Require field update/inspection.
- Prohibited action: Present stale TOC as final.
- Task-memory update: DOCX readiness limitation.
- Reviewer re-run requirements: DOCX readiness reviewer.
- Allowed final disclosure: "Word field behavior requires manual validation."
- Escalation condition: Submission requires updated TOC and it remains unvalidated.

### Page Number Uncertainty

- Detection condition: Page numbering cannot be inspected or is inconsistent.
- Severity: Medium.
- Affected state: DOCX readiness.
- Recoverability: Recoverable through formatting validation.
- Permitted action: Mark page-number behavior unvalidated.
- Prohibited action: Claim final pagination.
- Task-memory update: Formatting status and prohibited claims.
- Reviewer re-run requirements: Formatting and DOCX readiness reviewers.
- Allowed final disclosure: "Page-number behavior requires validation."
- Escalation condition: Print-ready claim requested without page-number validation.

### Per-Page Footnote Numbering Uncertainty

- Detection condition: Footnote numbering restart per page cannot be enforced or validated.
- Severity: Medium.
- Affected state: DOCX readiness.
- Recoverability: Recoverable through WordprocessingML/Word validation.
- Permitted action: Disclose limitation and require manual validation.
- Prohibited action: Claim per-page restart passed without evidence.
- Task-memory update: Footnote limitation and delivery claim prohibition.
- Reviewer re-run requirements: Footnote reviewer and DOCX readiness reviewer.
- Allowed final disclosure: "Per-page footnote numbering requires Microsoft Word validation."
- Escalation condition: Institution requires this behavior and no validation is possible.

### Reviewer Disagreement

- Detection condition: Two reviewer contracts return incompatible decisions.
- Severity: High.
- Affected state: Internal review.
- Recoverability: Recoverable by priority hierarchy and scope boundaries.
- Permitted action: Apply reviewer scope, priority hierarchy, and final QA arbitration.
- Prohibited action: Ignore the stricter blocking finding.
- Task-memory update: Reviewer conflict and resolution reason.
- Reviewer re-run requirements: Affected reviewers and final QA reviewer.
- Allowed final disclosure: "Reviewer conflict resolved by [rule]."
- Escalation condition: Conflict cannot be resolved by scope or priority.

### Repeated Revision Failure

- Detection condition: Same gate fails after repeated correction attempts.
- Severity: High.
- Affected state: Current failed gate.
- Recoverability: Depends on failure type.
- Permitted action: Escalate to `PAUSE` for missing external input or `FAIL` for impossible final claim.
- Prohibited action: Continue cycling without reporting the blocker.
- Task-memory update: Revision history and failed gate count.
- Reviewer re-run requirements: Failed reviewer only after material correction.
- Allowed final disclosure: "Gate remains blocked by [reason]."
- Escalation condition: Three repeated failures for the same blocking reason.
