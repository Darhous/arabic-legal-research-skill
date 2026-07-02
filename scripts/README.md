# Scripts

This directory currently contains no executable scripts. It documents future implementation boundaries for generation and validation tooling.

## Future Implementation Areas

- DOCX generator from structured research source.
- Structure validator.
- Methodology validator.
- Citation validator.
- Footnote validator.
- Bibliography validator.
- Formatting validator.
- Profile comparison validator for colored and black-and-white outputs.
- Final QA report generator.

## Future Generator Behavior

The DOCX generator should:

- Read structured input.
- Apply institution profile.
- Apply selected style profile.
- Generate Arabic RTL DOCX.
- Insert cover, cover copy, dedication, acknowledgements, introduction, body, conclusion, references, appendices, and table of contents.
- Apply heading styles.
- Start each `مبحث` on a new page.
- Insert real footnotes only.
- Mark unverified sources as `Requires Verification`.

## Future Executable Validator Behavior

Future executable validators should fail clearly when:

- Required data is missing.
- Approved plan headings are changed.
- Prohibited heading levels appear.
- Citations are missing or unverifiable.
- Footnotes are fake, unrelated, or insufficient without explanation.
- Bibliography metadata is incomplete.
- RTL or print formatting is missing.
- DOCX readiness cannot be confirmed.

## DOCX Caveat

Some Word features, including table of contents field updates and footnote numbering restart per page, may require Microsoft Word or compatible post-processing. Future scripts must report unvalidated behavior rather than claiming success.
