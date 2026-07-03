<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# استخدام المشروع مع OpenAI Codex

Codex هو الواجهة التطويرية من OpenAI التي تعمل من سطر الأوامر وتقرأ ملفات مشروعك محليًا، بنفس
منطق Claude Code تقريبًا.

## الخطوات

1. استنسخ المستودع وافتحه في Codex:
   ```bash
   git clone https://github.com/Darhous/arabic-legal-research-skill.git
   cd arabic-legal-research-skill
   codex
   ```
2. اجعله يقرأ `README.md` و`SKILL.md` و`CODEX.md` والمجلدات الأساسية أولًا.
3. استخدم الـ Prompt الجاهز أدناه.
4. استخدمه بعدها لتطوير المشروع نفسه، أو لإنتاج مستندات بحث قانوني وفق قواعد المشروع.

## Prompt جاهز لـ Codex

```text
Before doing anything, read README.md, SKILL.md, CODEX.md, rules/,
checklists/, validators/, and tests/. Then explain the project in
simple Arabic and follow the skill instructions exactly in any
generated legal research output.

Do not invent sources, citations, Quran verse numbers, or Hadith
references. Mark anything unverifiable as "Requires Verification".
Follow the mandatory heading hierarchy: قسم -> باب -> فصل -> مبحث ->
مطلب. Do not claim a result is print-ready or submission-ready unless
the checklists in checklists/ and the executable CLI validators in
src/legal_research_skill/ both pass.

If you are modifying the codebase itself, read CODEX.md fully first --
it defines the maintainer development rules (rule ID registry, schema
sync, claim-boundary enforcement, Word automation isolation rules) that
must not be violated.
```

## الفرق بين استخدام Codex لإنتاج بحث واستخدامه لتطوير الكود

| الاستخدام | الملف المرجعي الأساسي |
|---|---|
| إنتاج بحث قانوني عربي | `SKILL.md` + `rules/` + `checklists/` |
| تطوير أو صيانة الكود نفسه | `CODEX.md` (قواعد الصيانة الكاملة) |

إن طلبت من Codex تطوير الكود، يجب أن يلتزم بكل قواعد `CODEX.md` — تحديدًا: عدم كسر مزامنة الـ
Schema، عدم إضافة معرّفات قواعد جديدة إلا عبر `src/legal_research_skill/rules.py`، وعدم تشغيل
أتمتة Word خارج العملية المعزولة الموجودة في `src/legal_research_skill/word/`.

## تحذير من الهلوسة

Codex — مثل أي نموذج لغوي — قد يخترع تفاصيل تبدو منطقية عن بنية المشروع إن لم يقرأ الملفات فعليًا
أولًا. الـ Prompt أعلاه يفرض القراءة الفعلية قبل أي عمل؛ تأكد أنه فعلًا فتح الملفات (وليس فقط ادّعى
قراءتها) قبل الوثوق بأي وصف يقدّمه للمشروع.
