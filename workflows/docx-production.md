<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# Workflow: إنتاج ملف DOCX تنفيذي

## لمن هذا المسار؟

للمطوّر أو الباحث الذي ثبّت الأداة فعليًا (راجع [`docs/quickstart.md`](../docs/quickstart.md)
المسار الرابع) ويريد ملف DOCX حقيقيًا ومفحوصًا بنيويًا، وليس مجرد نص من محادثة.

## متى أستخدمه؟

عندما تملك بيانات بحث منظمة (JSON مطابقة لـ `schemas/research-state.schema.json`) وتريد تحويلها
إلى ملف Word فعلي مع فحص بنيوي حقيقي — وربما فحص Word نفسه إن كان متاحًا.

## خطوات التنفيذ

1. تأكد أن بيانات بحثك مطابقة للـ Schema:
   ```bash
   legal-research-skill schema-check my-research.json --format json
   ```
2. شغّل التحقق المنهجي الكامل قبل توليد أي ملف:
   ```bash
   legal-research-skill validate my-research.json --fail-on high --format json
   ```
3. ولّد ملف DOCX مسودة:
   ```bash
   legal-research-skill render-docx my-research.json --output out/draft.docx --format json
   ```
4. افحص بنية الملف الناتج (OPC/OOXML):
   ```bash
   legal-research-skill validate-docx out/draft.docx --format json
   ```
5. **أو نفّذ الخطوتين 3 و4 معًا** عبر أمر واحد ينتج أيضًا بيان ملفات (Manifest):
   ```bash
   legal-research-skill build-artifact my-research.json --output-dir out/artifact --format json
   ```
6. **اختياري**: إن كان لديك Windows وMicrosoft Word مثبتين فعليًا، شغّل بوابة Word للحصول على
   حالة `WORD_VALIDATED` الحقيقية (تحديث الحقول، إعادة الترقيم، حفظ داخل Word نفسه):
   ```bash
   legal-research-skill build-artifact my-research.json --output-dir out/artifact --require-word --word-timeout-seconds 60 --format json
   ```
   إن لم يتوفر Word، ستحصل على حالة `NOT_AVAILABLE` أو `BLOCKED` — **وهذا سلوك متوقع وصحيح**، وليس
   خطأً في الأداة.

## Prompt جاهز (لطلب تشغيل هذا المسار عبر Claude Code أو Codex)

```text
I have research-state JSON at <path>. Run schema-check, then validate
with --fail-on high, then build-artifact with --output-dir out/artifact
and --format json. Report the exact result state (STRUCTURALLY_VALID,
BLOCKED, TIMEOUT, FAILED, NOT_RUN, or NOT_AVAILABLE) -- do not claim
success unless the reported state actually says so.
```

## أخطاء يجب تجنبها

- ❌ الإعلان أن الملف "جاهز للطباعة" أو "Word-validated" لمجرد نجاح `validate-docx` البنيوي —
  هذا فحص بنيوي فقط، راجع [`docs/limitations.md`](../docs/limitations.md).
- ❌ تجاهل حالة `BLOCKED` أو `TIMEOUT` من بوابة Word واعتبار الملف صالحًا رغم ذلك.
- ❌ تشغيل `--require-word` على جهاز بدون Microsoft Word فعلي متوقعًا نجاحًا.
- ❌ الكتابة فوق ملف الإدخال نفسه كمسار إخراج — الأداة ترفض ذلك أصلًا كحماية أمان.

## مخرجات متوقعة

ملف `.docx` فعلي RTL كامل، تقرير فحص بنيوي JSON حتمي، بيان ملفات (Manifest) بتجزئة SHA-256 لكل
ملف ناتج، وحالة نتيجة صريحة واحدة من: `STRUCTURALLY_VALID`, `WORD_VALIDATED`, `NOT_AVAILABLE`,
`TIMEOUT`, `FAILED`, `BLOCKED`.
