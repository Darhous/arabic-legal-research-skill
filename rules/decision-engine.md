# Decision Engine

This file defines the operating state machine and gate decisions for the Skill. It is a documented operating contract, not executable code.

## Decision Outcomes

Use one decision at every gate:

- `PROCEED` - all exit criteria are satisfied and the next state may start.
- `REVISE` - the current artifact can be corrected without mandatory external input.
- `PAUSE` - mandatory information is missing or a same-authority conflict cannot be resolved.
- `FAIL` - a specific artifact, gate, verification, technical action, or final contract cannot honestly pass under current conditions.

`FAIL` must include a recovery path unless the requested final claim is impossible. Distinguish:

- Artifact failure.
- Reviewer gate failure.
- Source verification failure.
- Recoverable technical failure.
- Final output contract failure.

## PAUSE Discipline

Do not use `PAUSE` for optional preferences. Use best-effort execution, documented assumptions, and `Requires Verification` when safe.

Use `PAUSE` only when continuing would be materially incorrect, such as:

- Missing research topic/title.
- User confirmed an approved professor plan exists but did not provide it.
- User supplied an exclusive file/template and it is missing or unreadable.
- Same-priority instructions conflict and cannot be resolved by specificity or recency.
- Required page count makes mandatory structure impossible without user choice.

## State Machine Table

| State | Purpose | Required inputs | Outputs | Entry criteria | Exit criteria | Allowed next state | Gate failure behavior | Task memory updates | Reviewer |
|---|---|---|---|---|---|---|---|---|---|
| Intake | Capture task scope and mandatory metadata. | User request, title/topic, output type, known institution data, approved plan status. | Intake record and missing-input list. | New task begins. | Mandatory intake fields are known, explicitly optional, or safely pending. | Source and instruction audit. | `PAUSE` for missing title or confirmed missing approved plan; otherwise record assumptions. | `task_identifier`, `user_request`, `research_title`, `required_output_type`, `unresolved_questions`. | None. |
| Source and instruction audit | Classify all supplied authorities and files. | Intake record, uploaded instructions, sources, templates, plans. | Instruction/source inventory. | Intake passed. | All available materials are classified by authority, type, readability, and verification status. | Priority resolution. | `PAUSE` for unreadable mandatory exclusive file; `REVISE` for misclassified materials. | `source_inventory`, `source_restrictions`, `source_verification_status`. | None. |
| Priority resolution | Resolve conflicts under the canonical hierarchy. | Instruction inventory, profile, templates, plan status. | Priority decision log. | Audit passed. | Conflicts are resolved or clarified; no duplicate priority order is used. | Approved plan validation. | `PAUSE` for unresolved same-authority conflict. | `assumptions`, `unresolved_questions`, `completed_gates`. | None. |
| Approved plan validation | Protect professor-approved structure. | Approved plan, user instructions, hierarchy rules. | Locked plan map or plan absence record. | Priority resolution passed. | Plan is locked, absent, or explicitly marked incomplete with user-approved recovery. | Research design. | `PAUSE` if confirmed plan missing; `REVISE` if system-proposed plan conflicts. | `approved_plan_status`, `locked_plan_structure`, `body_hierarchy_map`. | Plan reviewer. |
| Research design | Define methodology and proposed structure when allowed. | Title, problem, objectives, plan status, methodology rules. | Research design record. | Plan gate passed. | Design covers problem, objectives, method, limits, and allowed hierarchy. | Methodological introduction drafting. | `REVISE` weak design; `PAUSE` only for missing mandatory topic data. | `methodology_components_status`, `assumptions`. | Methodology reviewer when design is complete. |
| Methodological introduction drafting | Draft required introduction components. | Research design and methodology components. | Draft introduction. | Research design passed. | All required components are present or explicitly justified. | Body drafting. | `REVISE` missing or decorative sections. | `methodology_components_status`, `revision_history`. | Methodology reviewer and language reviewer. |
| Body drafting | Draft body under locked/proposed hierarchy. | Locked plan or approved proposed plan, source inventory. | Draft body. | Introduction gate passed. | Body follows locked/proposed plan and restricted hierarchy. | Citation and footnote integration. | `REVISE` for hierarchy violations; `PAUSE` only for mandatory plan uncertainty. | `body_hierarchy_map`, `revision_history`. | Plan reviewer and language reviewer. |
| Citation and footnote integration | Link claims, citations, and footnotes. | Draft content, source inventory, citation rules, footnote rules. | Citation records and footnote records. | Body drafting passed. | Claims are supported, unverifiable items are marked, and footnotes link to same-page content where possible. | Bibliography building. | `REVISE` unsupported claims; source verification failure uses `Requires Verification`, not fabrication. | `citation_records`, `footnote_records`, `verification_markers`. | Citation reviewer and footnote reviewer. |
| Bibliography building | Build references from used sources. | Used sources, citation records, bibliography rules. | Bibliography records. | Citation/footnote gate passed. | Cited sources appear in bibliography; metadata is complete or marked. | DOCX formatting preparation. | `REVISE` missing bibliography entries. | `bibliography_records`, `used_sources`. | Bibliography reviewer. |
| DOCX formatting preparation | Prepare layout requirements without claiming generation. | Formatting profile, template status, hierarchy map, output type. | Formatting readiness plan. | Bibliography gate passed. | A4, RTL, margins, headings, footnotes, TOC, page numbers, and profile decisions are specified or limitations recorded. | Internal review. | `REVISE` formatting plan gaps; `PAUSE` only for required missing official template. | `formatting_status`, `delivery_claims_prohibited`. | Formatting reviewer. |
| Internal review | Run documented reviewer contracts. | Draft artifacts, task memory, reviewer contracts. | Reviewer outputs. | Formatting preparation passed. | Required reviewer contracts return PASS, or failures are routed to correction. | Final QA. | `REVISE` for fixable reviewer failures; `PAUSE` for required external input. | `reviewer_findings`, `completed_gates`, `failed_gates`. | All applicable reviewers. |
| Final QA | Check output contract and claim boundaries. | Reviewer outputs, task memory, final artifacts. | Final QA result. | Internal review passed. | Delivery claims are allowed by evidence and limitations are disclosed. | Delivery. | `FAIL` for unsupported final claims; `REVISE` for missing disclosure. | `final_qa_status`, `delivery_claims_allowed`, `delivery_claims_prohibited`. | Final QA reviewer. |
| Delivery | Deliver artifact and concise validation report. | Final QA result, artifacts, disclosure list. | Delivered work and final report. | Final QA passed. | Output is labeled according to validated state. | End. | Do not deliver as final when blockers remain. | `revision_history`, final state snapshot. | Final QA reviewer. |

## Missing Inputs

If required inputs are missing:

1. Identify the missing input.
2. Decide whether it blocks the current state.
3. If it blocks, return `PAUSE` and ask one focused question.
4. If it does not block, continue using best effort and record the assumption.

Never invent missing researcher names, professor names, source data, institutional rules, or source metadata.

## Contradictory Instructions

Apply `rules/priority-hierarchy.md`.

- Higher-priority instructions override lower-priority instructions.
- Same-level conflicts are resolved by specificity, then recency.
- Same-level conflicts unresolved by specificity or recency require `PAUSE`.
- Approved plan conflicts with user drafting preferences require clarification before changing the plan.

## Unverifiable Citations

If a citation cannot be verified:

- Mark it `Requires Verification`.
- Do not present it as verified.
- Do not invent publication data, page numbers, URLs, access times, Quran references, or Hadith references.
- Proceed only if the output can honestly disclose verification gaps.

## Page Count Constraints

If the requested page count cannot contain required front matter, methodology, body, footnotes, conclusion, references, appendices, and table of contents, return `PAUSE` and ask which constraint the user wants to relax. Do not silently remove required sections.
