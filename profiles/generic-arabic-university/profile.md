# Generic Arabic University Profile

This profile supports Arabic legal academic research when no institution-specific profile is supplied.

## Priority

Apply the canonical priority hierarchy in `rules/priority-hierarchy.md`. This profile is a fallback and never overrides current user instructions, uploaded university/course/professor instructions, approved plans, or official templates.

## Default Structure

Use the repository required order unless the user supplies a different official requirement:

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

## Body Hierarchy

Use only:

```text
قسم → باب → فصل → مبحث → مطلب
```

Do not introduce alternative subdivisions unless the user explicitly requests them.

## Formatting Defaults

Use:

- A4 page.
- Arabic RTL throughout.
- Print-ready margins.
- Centered bold headings.
- Justified paragraphs.
- Controlled line spacing.
- Page numbers.
- Table of contents.
- Bibliography.

## Style Profiles

Support:

- Colored print version.
- Black-and-white print version.

Both versions must preserve identical structure.

## Validation

If university rules conflict with repository defaults, report the conflict and follow the user-provided official rule only when it is explicit.
