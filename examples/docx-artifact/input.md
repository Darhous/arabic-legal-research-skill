<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous -->

# مثال: إنتاج DOCX تنفيذي — المدخل

مثال تعليمي مرافق لـ [`workflows/docx-production.md`](../../workflows/docx-production.md)، يستخدم
ملف اختبار حقيقي موجود بالفعل في المستودع (وليس بيانات جديدة).

## المدخل

ملف بيانات بحث JSON موجود فعليًا:

```text
examples/fixtures/valid/approved-plan-locked.json
```

## الأوامر الفعلية (بعد تثبيت المطورين — راجع docs/quickstart.md)

```bash
legal-research-skill schema-check examples/fixtures/valid/approved-plan-locked.json --format json
legal-research-skill validate examples/fixtures/valid/approved-plan-locked.json --fail-on high --format json
legal-research-skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/examples-docx-artifact --format json
```
