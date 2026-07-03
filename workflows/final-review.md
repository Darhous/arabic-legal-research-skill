<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# Workflow: المراجعة النهائية قبل التسليم

## لمن هذا المسار؟

لأي مستخدم (طالب، باحث، محامٍ، مطوّر) وصل لمسودة شبه نهائية ويريد التأكد من جاهزيتها قبل التسليم
أو الاستخدام الرسمي.

## متى أستخدمه؟

دائمًا كخطوة أخيرة، بعد أي مسار آخر (`legal-research`, `legal-memo`, `contract-review`,
`case-analysis`, `docx-production`) — لا تتخطَّ هذه الخطوة أبدًا.

## خطوات التنفيذ (المسار النصي — بدون تثبيت)

1. اطلب من النموذج تطبيق قوائم المراجعة الأربع صراحة، واحدة تلو الأخرى:
   - [`checklists/methodology-review.md`](../checklists/methodology-review.md)
   - [`checklists/citation-review.md`](../checklists/citation-review.md)
   - [`checklists/formatting-review.md`](../checklists/formatting-review.md)
   - [`checklists/final-review.md`](../checklists/final-review.md)
2. اطلب قائمة صريحة بكل عنصر لم يجتز إحدى القوائم، مع السبب.
3. لا تقبل عبارات عامة مثل "كل شيء جيد" — اطلب تفصيلًا لكل بند من كل قائمة.

## خطوات التنفيذ (المسار التنفيذي — مع تثبيت CLI)

1. شغّل التحقق الشامل بأعلى مستوى حساسية:
   ```bash
   legal-research-skill validate my-research.json --fail-on warning --format json
   ```
2. إن كنت تنتج DOCX، شغّل الفحص البنيوي:
   ```bash
   legal-research-skill validate-docx out/draft.docx --format json
   ```
3. راجع حقل النتيجة والقواعد المخالفة (`rule_id`) واحدة واحدة عبر:
   ```bash
   legal-research-skill explain <RULE-ID>
   ```
4. لا تعتبر العمل جاهزًا إلا إذا كانت كل النتائج ذات الخطورة `warning` فأعلى صفرًا، أو مُبررة صراحة.

## Prompt جاهز

```text
طبّق الآن قوائم المراجعة الأربع بالترتيب على العمل السابق:
methodology-review, citation-review, formatting-review, final-review.

لكل قائمة: اذكر كل بند اجتاز الفحص، وكل بند لم يجتز مع السبب الدقيق.
لا تقل "كل شيء جاهز" دون تفصيل كل بند. في النهاية اذكر الحالة النهائية
الدقيقة: مسودة تحتاج مراجعة، أم جاهزة للمراجعة البشرية، أم لا شيء أكثر
من ذلك (لا تدّعِ "جاهز للطباعة" أو "جاهز للتسليم" أبدًا في هذا السياق
النصي).
```

## أخطاء يجب تجنبها

- ❌ قبول "المراجعة اجتازت" دون رؤية تفصيل كل بند فعليًا.
- ❌ إعلان أن العمل "جاهز للتسليم النهائي" استنادًا فقط لمراجعة نصية دون تحقق تنفيذي عند توفره.
- ❌ تخطي أي من القوائم الأربع لتوفير الوقت.
- ❌ الخلط بين "اجتاز الفحص الشكلي" و"صحيح قانونيًا أو أكاديميًا" — راجع
  [`docs/limitations.md`](../docs/limitations.md).

## مخرجات متوقعة

تقرير مراجعة صريح ببنود ناجحة وبنود فاشلة لكل قائمة من القوائم الأربع، وحالة نهائية دقيقة الصياغة
لا تتجاوز ما تم فحصه فعليًا.
