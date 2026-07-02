# Arabic Legal Research Production Skill

This Skill guides Claude in producing Arabic legal academic research papers and preparing them for validated Microsoft Word delivery. It must combine legal academic methodology, Arabic RTL formatting, citation discipline, staged execution, internal review, and final quality gates.

Use this Skill when the user asks for an Arabic legal academic paper, research plan, legal methodology introduction, DOCX-ready research document, citation review, footnote validation, or final formatting review.

## Operating Principle

This is not a prompt-only writer. It is a legal research production system.

Treat each research paper as a controlled academic deliverable with:

- Instruction audit before drafting.
- Priority resolution before planning.
- Approved plan protection.
- Source inventory and citation integrity.
- Arabic legal methodology.
- Restricted body hierarchy.
- Internal reviewers.
- Final output contract.

Never claim completion before the output contract is satisfied.

The final deliverable should be a `.docx` file when DOCX generation tooling is available. If DOCX generation is not yet implemented or cannot be validated, produce the closest structured source artifact and clearly report what remains before print readiness.

## Rule Modules

Load and apply these rule files as needed:

- `rules/priority-hierarchy.md` - source and instruction priority.
- `rules/decision-engine.md` - proceed, pause, revise, or fail decisions.
- `rules/task-memory.md` - required working state for the task.
- `rules/error-recovery.md` - safe recovery behavior for common failures.
- `rules/output-contract.md` - final deliverable obligations.
- `rules/terminology.md` - canonical repository terminology and verification marker rules.
- `rules/police-academy-methodology.md` - methodology from the Police Academy guide.
- `rules/structure.md` - document order, introduction components, and body hierarchy.
- `rules/language.md` - academic Arabic style restrictions.
- `rules/citations.md` - direct and indirect quotation rules.
- `rules/footnotes.md` - page-level footnote expectations and validation caveats.
- `rules/formatting.md` - A4, RTL, headings, margins, page borders, and DOCX formatting.
- `rules/bibliography.md` - reference list rules and source metadata.

Use the relevant institution profile:

- `profiles/police-academy/profile.md`
- `profiles/generic-arabic-university/profile.md`

Use these checklists before claiming completion:

- `checklists/methodology-review.md`
- `checklists/citation-review.md`
- `checklists/formatting-review.md`
- `checklists/final-review.md`

Use these reviewer contracts before delivery:

- `validators/plan-reviewer.md`
- `validators/methodology-reviewer.md`
- `validators/language-reviewer.md`
- `validators/citation-reviewer.md`
- `validators/footnote-reviewer.md`
- `validators/bibliography-reviewer.md`
- `validators/formatting-reviewer.md`
- `validators/docx-readiness-reviewer.md`
- `validators/final-qa-reviewer.md`

The Skill must not deliver final work unless all required reviewer contracts pass.

## Phase 3 Executable Validation

When structured research-state JSON is available, the Phase 3 CLI can run text-level and structural checks:

```bash
legal-research-skill validate <input.json>
legal-research-skill schema-check <input.json>
legal-research-skill list-validators
legal-research-skill explain PLAN-001
```

These validators support schema, cross-reference, priority, approved-plan, hierarchy, methodology, citation, footnote, bibliography, verification-marker, output-claim, and gate-readiness checks. They do not generate DOCX files or validate Microsoft Word rendering.

## Execution State Machine

The canonical state machine is defined in `rules/decision-engine.md`. The Skill must follow those states in order:

1. Intake.
2. Source and instruction audit.
3. Priority resolution.
4. Approved plan validation.
5. Research design.
6. Methodological introduction drafting.
7. Body drafting.
8. Citation and footnote integration.
9. Bibliography building.
10. DOCX formatting preparation.
11. Internal review.
12. Final QA.
13. Delivery.

No state may start until the previous state gate permits `PROCEED`. Use `REVISE`, `PAUSE`, or `FAIL` exactly as defined in `rules/decision-engine.md`.

## Mandatory Intake

Before drafting a full paper, collect or infer safely:

- Research title.
- Academic institution and department, if relevant.
- Researcher name and supervisor name, if required.
- Degree/course context, if required.
- Approved research plan, if one exists.
- Required page count or word count.
- Required citation style, if specified by the institution.
- Required source list or source access constraints.
- Whether Quran, Hadith, or quotation page is desired.
- Whether appendices are expected.
- Preferred output style: colored print or black-and-white print.

Ask the user when required information is missing and cannot be reasonably left as a placeholder.

Track all intake and task state according to `rules/task-memory.md`.

## Approved Plan Rule

If the user uploads or pastes a plan approved by the course professor or supervisor:

- Treat it as mandatory.
- Preserve its headings exactly.
- Preserve heading order exactly.
- Do not delete, merge, rename, translate, or reorder headings.
- Do not replace the approved plan with a proposed plan.
- Only modify the plan when the user explicitly requests that change.

If no approved plan is provided, propose a plan that is modern, non-imitative, balanced, and fully connected to the title and research problem.

## Required Document Order

The paper must follow this order:

1. Cover
2. Cover copy
3. Quran verse, Hadith, or quotation page
4. Dedication
5. Acknowledgements
6. Methodological introduction
7. Research body
8. Conclusion: summary, results, recommendations
9. References list
10. Appendices if any
11. Table of contents

Do not move the table of contents earlier unless the user or institution profile explicitly requires it.

## Methodological Introduction

The methodological introduction must include:

- تمهيد
- مشكلة الدراسة
- أهمية الدراسة
- الدراسات السابقة
- أهداف الدراسة
- نوع ومنهج الدراسة
- حدود الدراسة
- فروض الدراسة
- تساؤلات الدراسة
- أدوات الدراسة
- مفاهيم الدراسة إن وجدت
- صعوبات الدراسة إن وجدت
- خطة الدراسة

If an item is not applicable, either omit it only when the institution permits omission or include a concise justified statement.

## Body Hierarchy

Use only:

```text
قسم → باب → فصل → مبحث → مطلب
```

Do not use:

- فرع
- بند
- أولًا / ثانيًا
- Arabic or Latin numbers as body heading levels
- Letters
- Decorative symbols

Use prohibited levels only if the user explicitly asks for them.

## Citation and Source Integrity

Never invent references.

Direct quotations must:

- Preserve wording.
- Appear between quotation marks.
- Be documented.
- Use `...` for omitted words.
- Use `[ ]` for additions or corrections.

Indirect quotations must:

- Be rewritten in the researcher’s own style.
- Be documented.
- Avoid disguising copied text as paraphrase.

Quranic quotations must preserve wording and include surah and verse. Hadith quotations must be verified from reliable sources and documented. Famous quotations must be verified and documented.

Internet sources must include standard reference metadata, URL, and access date/time.

If verification is impossible, mark the source or citation as `Requires Verification`.

## Footnote Requirements

Every page should have at least two footnotes where possible. Footnotes must be directly related to information on the same page, not decorative, generic, or fake.

Footnotes must:

- Be RTL.
- Appear at the bottom of the page from the right side.
- Restart numbering on each page: page 1 uses ١, ٢; page 2 uses ١, ٢; and so on.
- Use real source information or be marked `Requires Verification`.

Word-level per-page restart may require DOCX field settings, section behavior, or post-processing validation. Do not claim per-page restart is correct unless it has been validated in the generated DOCX.

## Formatting Requirements

The DOCX target must use:

- A4 page size.
- Print-ready margins.
- Arabic RTL throughout.
- Arabic academic font options.
- Page borders.
- Centered bold headings.
- Each `مبحث` starts on a new page.
- Each `مبحث` title appears centered at the top of the page in bold.
- Justified paragraphs.
- Proper paragraph indentation.
- Controlled line spacing.
- RTL footer and footnotes from the right.
- Page numbers.
- Table of contents.
- Bibliography.

Provide two style profiles:

- Colored print version.
- Black-and-white print version.

The two versions must preserve identical structure and differ only in visual styling.

## Language Rules

Use formal Arabic academic legal style. Avoid:

- Excitement style.
- Oratory.
- Imagination.
- Emotional language.
- Sarcasm or mockery.
- Superiority.
- Self-praise or praise of others.
- Absolute categorical wording unless legally and academically supportable.
- Excessive first-person expressions such as `أنا`, `أرى`, `رأيي`, `قلت`.
- Vague expressions.
- Unnecessary verbosity.
- Harmful over-compression where explanation is needed.
- Naming people in criticism unless scientifically necessary.

## Validation Gates

Before final delivery, complete these gates:

- Structure compliance.
- Methodology compliance.
- Language compliance.
- Plan compliance.
- Citation compliance.
- Footnote compliance.
- Bibliography compliance.
- Formatting compliance.
- DOCX readiness.
- Final QA.

If any required gate fails, report the failure and do not claim the paper is final or print-ready.

## Final Output Contract

Final work is complete only when `rules/output-contract.md` is satisfied. Use the narrowest accurate delivery claim: content complete, citations reviewed, DOCX-ready source prepared, DOCX generated, DOCX structurally validated, Microsoft Word behavior manually validated, print-ready, or submission-ready.

If DOCX tooling is not available, do not call the output final or print-ready. Report it as DOCX-ready source or preparation work only.

## Final Response Requirements

When delivering work, include:

- Files or artifacts produced.
- Validation performed.
- Failed or unverified items.
- Sources marked `Requires Verification`.
- Next step needed for true print readiness, if any.
