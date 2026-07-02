# Footnote Rules

This file defines page-level footnote expectations for Arabic legal research DOCX output.

## Required Footnote Policy

Every page must have at least two footnotes where possible.

This is a quality requirement, not permission to invent references. If a page does not contain enough cite-worthy material for two real footnotes, the final report must explain that the requirement could not be satisfied without fake or decorative notes.

## Relevance Rule

Footnotes must be directly related to information on the same page.

Do not use:

- Decorative footnotes.
- Generic bibliography notes.
- Fake citations.
- Repeated irrelevant references.
- Footnotes added only to satisfy a numeric count.

## Verification Rule

If a source cannot be verified, mark the footnote `Requires Verification`.

Do not turn unverified sources into apparently verified references.

## RTL and Placement

Footnotes must:

- Use Arabic RTL text direction.
- Appear at the bottom of the page.
- Align from the right.
- Use Arabic-Indic numbering where possible.

## Numbering Restart Rule

Footnote numbering must restart on each page:

```text
Page 1: ١, ٢
Page 2: ١, ٢
Page 3: ١, ٢
```

Microsoft Word per-page restart may require DOCX section or footnote property behavior and post-processing validation. Generation scripts must not claim this is correct unless the DOCX has been validated.

## Footnote Failure Conditions

Fail footnote review if:

- A page has fewer than two footnotes and no legitimate exception is reported.
- A footnote is unrelated to same-page content.
- A footnote contains invented source data.
- Footnote text is not RTL.
- Footnote numbering does not restart per page and the output claims it does.
- Unverified footnotes are not marked `Requires Verification`.
