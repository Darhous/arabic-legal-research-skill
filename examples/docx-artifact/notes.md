<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous -->

# ملاحظات — مثال إنتاج DOCX تنفيذي

- هذا هو المثال **الوحيد** في `examples/` الذي يعرض ناتجًا حقيقيًا مُلتقَطًا من تشغيل فعلي للأداة
  (وليس نصًا توضيحيًا مكتوبًا يدويًا)، لأنه يعتمد على تنفيذ كود حقيقي وليس محادثة مع نموذج لغوي.
- `digest`/`hash` القيم الظاهرة في التشغيل الفعلي (`input_digest`, `phase3_baseline_hash`, ...)
  حُذفت من الملخص هنا لأنها تفصيلية جدًا وغير ضرورية للفهم؛ التشغيل الفعلي الكامل موجود في
  `manifest_path` الناتج محليًا عند تكرار الأمر بنفسك.
- لإعادة إنتاج هذا الناتج بنفسك تمامًا:
  ```bash
  legal-research-skill build-artifact examples/fixtures/valid/approved-plan-locked.json --output-dir tests_tmp/my-artifact --format json
  ```
  النتيجة ستكون **مطابقة بايتًا لبايت** لملف DOCX الناتج في كل مرة (بناء حتمي، راجع
  [`docs/architecture.md`](../../docs/architecture.md))، رغم اختلاف مسار `--output-dir`.
- `tests_tmp/` مُستثنى من Git (`.gitignore`) — لا تُنشئ مخرجات دائمة هناك.
