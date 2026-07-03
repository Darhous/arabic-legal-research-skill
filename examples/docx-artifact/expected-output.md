<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous -->

# مثال: إنتاج DOCX تنفيذي — الناتج الفعلي (مُلتقَط من تشغيل حقيقي)

هذا الملف **ليس توضيحيًا مُختلَقًا** — هو ملخص حقيقي من تشغيل فعلي لأمر
`legal-research-skill build-artifact` على `examples/fixtures/valid/approved-plan-locked.json` أثناء
كتابة هذا المثال، على إصدار الحزمة `0.3.0`.

## أهم الحقول من `artifact-manifest.json` الناتج

```json
{
  "final_artifact_status": "STRUCTURALLY_VALID",
  "generator_version": "0.3.0",
  "manifest_schema_version": "0.4.0",
  "allowed_claims": [
    "DOCX generated",
    "DOCX structurally validated",
    "RTL structurally applied"
  ],
  "prohibited_claims": [
    "Final legal research accepted",
    "Legal correctness verified",
    "Page numbers updated",
    "Source authenticity verified",
    "TOC updated",
    "Word validated",
    "print-ready"
  ],
  "word_evidence": {
    "availability": "not_checked",
    "status": "NOT_RUN"
  }
}
```

## قسم فحص Phase 3 (اثنا عشر مدققًا، كلهم `pass`)

```text
executed_validators: schema_integrity, cross_reference, priority_resolution,
plan_preservation, hierarchy_compliance, methodology_completeness,
citation_status, footnote_linkage, bibliography_completeness,
verification_markers, output_claims, gate_readiness
overall_status: pass
overall_decision: PROCEED
counts_by_severity: critical=0, high=0, medium=0, low=0, info=0
```

## قسم الفحص البنيوي لـ DOCX

```text
checks: zip_package, required_parts, relationships, document_xml,
styles_outline, rtl_properties, fields, footnotes, page_setup, security
status: pass
findings: []
```

## أهم ما يجب ملاحظته في هذا الناتج الحقيقي

- `word_evidence.status` هو `NOT_RUN` — لأن الأمر شُغّل بدون `--require-word`. هذا **متوقع وصحيح**،
  وليس فشلًا. راجع [`workflows/docx-production.md`](../../workflows/docx-production.md) لتشغيل
  بوابة Word فعليًا.
- `prohibited_claims` يذكر صراحة أن "Word validated" و"print-ready" **ممنوعان** كادّعاء عند هذه
  الحالة تحديدًا — هذا الحقل نفسه جزء من الناتج التنفيذي الحقيقي للأداة، وليس نصًا وثائقيًا فقط.
- `final_artifact_status` هو `STRUCTURALLY_VALID` (فحص بنيوي)، وليس `WORD_VALIDATED` — الفرق موضّح
  في [`docs/limitations.md`](../../docs/limitations.md).
