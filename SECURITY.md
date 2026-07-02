# Security Policy

## Reporting

Report security concerns privately by email:

`ahmeddarhous@gmail.com`

Do not include secrets, tokens, private keys, cookies, or live credentials in public issues.

## Scope

Security-sensitive areas include:

- DOCX package parsing and relationship validation.
- Path safety for generated artifacts.
- Word worker timeout and process cleanup.
- CLI input handling and JSON parsing.
- Packaging metadata and bundled schemas.

## Current Boundaries

The project does not execute macros, does not fetch sources from the internet during validation, and does not terminate general user Word sessions.
