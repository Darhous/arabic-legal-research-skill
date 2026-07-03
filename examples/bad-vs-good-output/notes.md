<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous -->

# ملاحظات — مثال الناتج السيء مقابل الجيد

- كل تفاصيل "الناتج السيء" هنا (اسم الكتاب، اسم المؤلف، الاقتباس المنسوب لـ"أحد كبار الفقهاء")
  **مُختلَقة عمدًا** لغرض التوضيح فقط — هذا بالضبط نوع الاختراع (Hallucination) الذي يحذّر منه
  المشروع في `rules/citations.md` و`LICENSE`. لا تستخدم هذه التفاصيل كمصدر حقيقي بأي حال.
- هذا المثال هو الأنسب لفهم **لماذا** لا يكفي الاعتماد على تعليمات نصية وحدها (طبقة Skill)، ولماذا
  الطبقة التنفيذية (Framework) مهمة لمن يريد تحققًا حقيقيًا وليس ثقة فقط.
- إن أردت رؤية الفحص التنفيذي الفعلي لهذا النوع من الأخطاء، جرّب:
  ```bash
  legal-research-skill validate examples/fixtures/invalid/hierarchy-level-jump.json --format json
  legal-research-skill validate examples/fixtures/invalid/dangling-citation-source.json --format json
  ```
  وهذه ملفات اختبار حقيقية موجودة في `examples/fixtures/invalid/` تُستخدم فعليًا في اختبارات
  المشروع.
