# Formatting Rules

This file defines Arabic RTL print formatting requirements for DOCX output.

## Page Setup

Use:

- A4 page size.
- Print-ready margins.
- Page borders.
- Page numbers.
- Table of contents.
- Bibliography.

Margins may be profile-specific, but they must be suitable for printing and binding.

## Direction and Language

Arabic RTL must apply throughout:

- Paragraphs.
- Headings.
- Footnotes.
- Footer.
- Page number placement where supported.
- Table of contents entries.
- Bibliography entries.

Mixed-language content may use LTR runs only for URLs, Latin titles, or technical identifiers.

## Fonts

Use Arabic academic font options such as:

- Traditional Arabic.
- Simplified Arabic.
- Arial.
- Times New Roman with Arabic support.
- Amiri, if available and institutionally acceptable.

The selected font must support Arabic shaping and diacritics.

## Paragraphs

Paragraphs must be:

- Justified.
- Properly indented.
- Consistent in spacing before and after.
- Controlled in line spacing.
- Free from layout shifts caused by manual spaces.

## Headings

Headings must be:

- Centered.
- Bold.
- RTL.
- Consistent across the document.

Each `مبحث` must:

- Start on a new page.
- Have its title centered at the top of the page.
- Use bold styling.

## Output Style Profiles

The repository supports two print profiles:

- Colored print version.
- Black-and-white print version.

Both must preserve identical academic structure and differ only in visual styling. A style change must not alter headings, order, citations, footnotes, bibliography, or page content.

## Formatting Failure Conditions

Fail formatting review if:

- Page size is not A4.
- Margins are not print-ready.
- RTL is missing from Arabic paragraphs, footnotes, or bibliography.
- Headings are not centered and bold.
- `مبحث` sections do not start on new pages.
- Page borders are missing when required.
- Paragraphs are ragged where justification is required.
- Colored and black-and-white profiles differ structurally.
