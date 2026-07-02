# Citation Reviewer

## Reviewer Name

Citation Reviewer

## Scope

Validate claim-source integrity, quotation handling, and verification status.

## Inputs

- Direct quotations.
- Indirect quotations.
- Quranic quotations.
- Hadith quotations.
- Famous quotations.
- Internet sources.
- Source inventory.
- Used sources.
- `rules/citations.md`.

## Preconditions

- Source inventory exists.
- Draft claims and quotation records exist.
- `Requires Verification` marker rules are available.

## Checks

- Direct quotation handling.
- Indirect quotation handling.
- Sacred and famous text attribution.
- Internet metadata.
- Claim-source linkage.
- Verification marker use.

## Evidence Requirements

- Citation record ids.
- Source record ids.
- Affected claim or quotation locations.
- Verification evidence or marker reason.

## Pass Criteria

- Direct quotations preserve wording, use quotation marks, and are documented.
- Indirect quotations are rewritten and documented.
- Quran quotations include surah and verse.
- Hadith and famous quotations are verified or marked `Requires Verification`.
- Internet sources include URL and access date/time or are marked.
- No fabricated source data appears.

## Fail Criteria

- Unsupported claims requiring citations.
- Direct quotation without quotation marks.
- Paraphrase too close to original wording.
- Invented page numbers, URLs, access dates, or publication data.
- Unverified citations presented as verified.

## Severity Levels

- Critical: Fabricated source data or hidden unverifiable authority.
- High: Unsupported legal claim requiring citation.
- Medium: Incomplete metadata with marker.
- Low: Citation formatting inconsistency.

## Decision Outcomes

- `PROCEED` when citation records pass.
- `REVISE` when claims can be supported, rewritten, or removed.
- `PAUSE` when mandatory source evidence is required from the user.
- `FAIL` when verified-source claims are impossible under current evidence.

## Required Correction Behavior

Add real documentation, rewrite paraphrases, mark unverifiable items, or remove unsupported claims.

## Task-Memory Fields Updated

- `citation_records`
- `source_verification_status`
- `verification_markers`
- `failed_gates`
- `reviewer_findings`
- `revision_history`

## Re-run Conditions

Re-run after source additions, citation edits, quotation edits, or removal of `Requires Verification`.

## Limitations

This reviewer does not check footnote placement, page-level footnote counts, bibliography ordering, or DOCX layout.

## Non-Responsibilities

- Does not validate footnote bottom placement.
- Does not validate bibliography completeness beyond citation-source linkage.
- Does not approve final source formatting.

## Required Output Structure

```yaml
reviewer: "Citation Reviewer"
status: "PASS | FAIL"
decision: "PROCEED | REVISE | PAUSE | FAIL"
findings: []
severity: "Critical | High | Medium | Low"
evidence: []
affected_locations: []
required_corrections: []
verification_required: []
task_memory_updates: []
rerun_required: true
limitations: []
```
