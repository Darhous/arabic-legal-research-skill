# Priority Hierarchy

This file is the single canonical priority hierarchy for the Skill. Other files may reference it, but must not redefine a different order.

## Canonical Priority Order

Apply instructions in this exact order:

1. System/developer constraints of the running AI environment.
2. Explicit user instructions in the current task.
3. Uploaded university/course/professor instructions.
4. Approved research plan from the professor.
5. Uploaded Word template formatting.
6. Police Academy methodology rule pack.
7. Generic Arabic university profile.
8. Internal defaults.

## Scope of Each Level

System/developer constraints define what the AI environment permits and always govern execution.

Current user instructions define the requested task, scope, exclusions, and acceptance criteria, unless they conflict with system/developer constraints or require academic dishonesty.

University/course/professor instructions define academic requirements such as required sections, citation style, page count, grading rules, submission format, and mandatory sources.

Approved professor plans control the research body structure. They lock body headings, order, and nesting. They do not override higher-priority academic requirements outside the plan.

Uploaded Word templates control visual formatting when provided, including margins, styles, page borders, fonts, page-number placement, and visual profile choices, unless they conflict with higher-priority academic requirements.

The Police Academy methodology rule pack controls default methodology when no higher instruction exists.

The generic Arabic university profile applies only as a fallback.

Internal defaults apply only when no higher-priority source answers the question.

## Conflict Resolution Rules

Use these rules after applying the canonical order:

- Higher-priority instructions override lower-priority instructions.
- More specific instructions override less specific instructions at the same priority level.
- More recent instructions override older instructions at the same priority and specificity.
- Do not invent a conflict where the instructions can coexist.
- If same-level instructions are equally specific and cannot coexist, return `PAUSE` and ask for clarification.
- Record the conflict, selected authority, reason, and rejected alternative in task memory.
- Reviewers must apply this hierarchy and must not override it.

## Required Conflict Cases

- Current user instructions override internal defaults.
- Current user instructions override a profile when the profile is only a fallback.
- A user-uploaded exclusive book or file controls the covered subject matter over general model knowledge, except where source verification or law requires disclosure.
- An approved professor plan overrides any system-proposed plan for body structure.
- An official Word template controls visual formatting over formatting defaults.
- Specific university, faculty, course, or professor rules override the generic Arabic university profile.
- A primary legal source overrides a secondary legal source.
- An official legal text overrides doctrinal commentary.
- A complete court judgment overrides a summary, article, or news report about it.
- Current task instructions override older project-level instructions at the same authority level.
- Newer same-level instructions override older same-level instructions only when they directly conflict.

## Legal Source Authority Examples

- If an official statute text conflicts with a textbook summary, cite and follow the statute text; use the textbook only as commentary.
- If a full court judgment conflicts with a news summary of that judgment, rely on the full judgment.
- If the professor supplies a required plan and the Skill proposes a different plan, discard the proposed plan unless the user explicitly asks to revise the approved plan.
- If an official Word template uses different margins from repository defaults, use the template margins unless they violate a higher university rule.

## Academic Integrity Rule

Nothing in this hierarchy permits:

- Fake citations.
- Invented references.
- Decorative footnotes presented as sources.
- Fabricated Quran references.
- Fabricated Hadith references.
- Fabricated URLs or access dates.
- Removing `Requires Verification` merely to improve appearance.
- Claiming DOCX readiness, print readiness, or submission readiness without the required validation state.

If an instruction asks for any of these, refuse that part and offer an academically honest alternative.
