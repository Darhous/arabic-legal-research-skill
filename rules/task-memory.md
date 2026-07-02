# Task Memory Model

The Skill must maintain explicit task state throughout production. This is a precise documentation contract for future schema work, not an executable schema in Phase 2.

## Field Status Values

Use these status values:

- `Known`
- `Missing`
- `Pending User`
- `Derived`
- `Assumed`
- `Requires Verification`
- `Passed`
- `Failed`
- `Not Applicable`

## Required State Fields

| Field | Purpose | Expected type or example | Updated by | Updated when | Decision use |
|---|---|---|---|---|---|
| `task_identifier` | Identify the production run. | string, date-based id, or user-supplied id. | Intake state. | Task start. | Links findings, revisions, and delivery report. |
| `user_request` | Preserve the current task request. | text summary plus key exclusions. | Intake state. | Task start and user changes. | Defines scope and prevents drift. |
| `jurisdiction` | Track legal system or country if relevant. | `Egypt`, `UAE`, `Not specified`. | Intake/audit states. | When sources or topic imply jurisdiction. | Controls source authority and legal terminology. |
| `institution_profile` | Identify selected institution/profile. | `police-academy`, `generic-arabic-university`. | Priority resolution. | After audit. | Selects default methodology and formatting. |
| `language` | Track output language and script direction. | `Arabic RTL`. | Intake state. | Task start. | Controls language and formatting review. |
| `research_type` | Identify research kind. | legal academic paper, plan, review, introduction. | Intake state. | Task start. | Controls required phases. |
| `source_restrictions` | Record exclusive or mandatory source constraints. | uploaded-only, official sources first, open web disallowed. | Audit state. | Source audit. | Prevents unauthorized source expansion. |
| `research_title` | Preserve approved or working title. | Arabic title or `Missing`. | Intake/research design. | Intake and title revisions. | Blocks design if missing. |
| `approved_plan_status` | Identify whether a professor-approved plan exists. | `Provided`, `Confirmed but missing`, `Absent`, `Unclear`. | Intake/plan validation. | Intake and plan review. | Determines PAUSE or proposed-plan path. |
| `locked_plan_structure` | Preserve approved plan headings exactly. | ordered heading map. | Plan validation. | After approved plan review. | Prevents unauthorized heading changes. |
| `required_output_type` | Track requested deliverable. | DOCX, DOCX-ready source, review report. | Intake state. | Task start. | Controls output contract claims. |
| `formatting_profile` | Track visual style profile. | colored print, black-and-white print, official template. | Formatting preparation. | After priority resolution. | Controls formatting reviewer. |
| `page_count_target` | Track page or word constraints. | `20 pages`, `Missing`, `Not Applicable`. | Intake/design. | Intake and planning. | Detects impossible compression. |
| `source_inventory` | List all available sources. | records with id, type, authority level, metadata. | Source audit. | When source material is added. | Feeds citation and bibliography reviewers. |
| `source_authority_level` | Rank source authority. | official law, court judgment, book, article, website. | Source audit. | Source classification. | Resolves legal source conflicts. |
| `source_verification_status` | Track source confidence. | verified, partial, `Requires Verification`, rejected. | Source audit/citation review. | Source review. | Blocks verified-source claims. |
| `citation_records` | Track claim-to-source links. | claim id, source id, direct/indirect, location. | Citation integration. | Citation drafting and review. | Enables citation reviewer. |
| `footnote_records` | Track footnote linkage. | page, footnote id, citation id, source id, relevance note. | Footnote integration. | Footnote drafting and review. | Enables same-page relevance review. |
| `bibliography_records` | Track reference list entries. | source id, formatted entry, metadata completeness. | Bibliography building. | Bibliography drafting and review. | Detects missing/unused references. |
| `assumptions` | Record best-effort assumptions. | list with rationale and authority level. | Any state. | Whenever assumed. | Must be disclosed or resolved. |
| `unresolved_questions` | Track blocking questions. | list with state and reason. | Decision engine. | On PAUSE. | Prevents premature delivery. |
| `verification_markers` | Track all `Requires Verification` markers. | marker id, location, reason, owner. | Citation/footnote/bibliography reviewers. | When verification is incomplete. | Prevents removal without evidence. |
| `state_machine_current_state` | Track current state. | state name from decision engine. | Each state. | State entry/exit. | Controls allowed transitions. |
| `completed_gates` | List gates passed. | state/reviewer ids. | Each gate. | Gate pass. | Supports final QA. |
| `failed_gates` | List gates failed. | state/reviewer ids plus reason. | Each gate. | Gate failure. | Routes correction. |
| `reviewer_findings` | Preserve reviewer outputs. | reviewer id, status, evidence, corrections. | Reviewer contracts. | Internal review. | Final QA input. |
| `revision_history` | Track material changes. | timestamp, state, change, reason. | Any state. | Each correction cycle. | Audits recovery and plan protection. |
| `delivery_claims_allowed` | Claims supported by evidence. | content review completed, DOCX generated, print-ready. | Final QA. | Before delivery. | Controls final wording. |
| `delivery_claims_prohibited` | Claims not supported. | print-ready, all citations verified, submission-ready. | Final QA. | Before delivery. | Prevents false claims. |

## Verification Marker Rules

`Requires Verification` is the canonical internal status marker. It must not be inserted blindly into polished Arabic research prose.

When delivering Arabic-facing output, disclose it with an appropriate Arabic note such as:

```text
تتطلب هذه الإحالة تحققًا إضافيًا قبل التسليم النهائي.
```

Remove the marker only when a source owner or reviewer provides sufficient verification evidence. Do not remove it for style, formatting, or page-count reasons.

## Minimum State Before Drafting

Before drafting, task memory must identify:

- Research title status.
- Approved plan status.
- Applicable priority decisions.
- Selected profile or fallback profile.
- Source inventory status.
- Required output type and style.

## Minimum State Before Delivery

Before delivery, task memory must identify:

- Current state.
- All completed and failed gates.
- All reviewer findings.
- All `Requires Verification` markers.
- Citation, footnote, bibliography, and formatting status.
- DOCX readiness status.
- Allowed and prohibited delivery claims.

If any required delivery field is missing, do not deliver final work.
