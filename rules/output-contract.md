# Output Contract

This file defines what the Skill may honestly claim at delivery time.

## Claim Levels

Use the narrowest accurate claim.

| Claim | Required evidence | Must not claim when |
|---|---|---|
| Research content complete | Required structure, methodological introduction, body, conclusion, references, appendices if any, and table of contents content are present. | Required sections are missing or plan compliance failed. |
| Citations reviewed | Citation reviewer contract returns PASS or documented non-final findings. | Citation records are missing or unsupported claims remain hidden. |
| Sources verified | Every used source has sufficient verification evidence. | Any source is marked `Requires Verification`. |
| Footnotes reviewed | Footnote reviewer contract returns PASS or limitations are disclosed. | Footnote linkage, page relevance, RTL, or count policy is unreviewed. |
| Bibliography reviewed | Bibliography reviewer contract returns PASS. | Used sources and bibliography entries are inconsistent. |
| Formatting reviewed | Formatting reviewer contract returns PASS for a formatting plan or artifact. | RTL, margins, page breaks, page numbers, or profile equivalence are unreviewed. |
| DOCX generated | A `.docx` artifact exists. | Only Markdown, plain text, or a source draft exists. |
| DOCX structurally validated | DOCX opens and structural checks pass in an accepted validator. | No DOCX validation evidence exists. |
| Microsoft Word behavior manually validated | Word-specific fields and layout behavior were inspected in Microsoft Word or an explicitly accepted equivalent. | TOC fields, per-page footnote restart, or page-number behavior are assumed. |
| Print-ready | DOCX generated, structurally validated, Word behavior validated, reviewers pass, and no blocking issues remain. | Any required validation is missing. |
| Submission-ready | Print-ready plus institution-specific final submission requirements are confirmed. | Institution submission rules or required metadata are unresolved. |

## Prohibited Claims Without Evidence

Do not use these claims unless their required evidence exists:

- Fully validated.
- Print-ready.
- Final DOCX.
- Ready for submission.
- All citations verified.
- Word-compatible.

## Honest Alternatives

Use these alternatives when appropriate:

- Content review completed.
- Citation review completed with verification gaps.
- DOCX generation not performed.
- DOCX-ready source preparation completed.
- Word field behavior requires manual validation.
- Citation requires verification.
- Layout requires final Microsoft Word inspection.

## Required Research Order

The deliverable must follow:

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

## Reviewer Requirement

All required internal reviewers must return `PASS` before final delivery.

If any reviewer returns `FAIL`, the output must be labeled incomplete and must include required corrections and blocking issues.

## DOCX Readiness Requirement

If a `.docx` file is requested, the Skill must not call the output print-ready unless DOCX generation and validation have passed.

If DOCX tooling is unavailable, the Skill may provide DOCX-ready source preparation only and must state that true print-ready delivery remains pending.

## Verification Requirement

All sources must be either verified or explicitly marked `Requires Verification`.

No final output may hide verification gaps.

## Required Final Deliverable Elements

A print-ready delivery requires:

- Print-ready DOCX.
- Correct Arabic RTL layout.
- Required research order.
- Complete methodological introduction.
- Body hierarchy limited to `قسم → باب → فصل → مبحث → مطلب`.
- Footnotes at bottom, RTL, right side.
- Footnote numbering restarted per page where possible and validated or disclosed.
- At least two relevant footnotes per page where possible.
- No fake citations.
- References list.
- Appendices if any.
- Table of contents.
- Final QA report.
