<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# CLAUDE.md — دليل استخدام المشروع مع Claude

هذا الملف يُقرأ تلقائيًا بواسطة **Claude Code** عند فتح هذا المستودع كمجلد عمل، ويُستخدم أيضًا
كدليل مرجعي لأي استخدام لـ Claude (شات عادي أو Claude Code) مع هذا المشروع.

## ماذا تفعل أولًا (Claude Code)

1. اقرأ [`SKILL.md`](SKILL.md) بالكامل — منهجية البحث القانوني العربي الأساسية.
2. اقرأ [`CODEX.md`](CODEX.md) إن كانت المهمة تطوير الكود نفسه (يحتوي قواعد الصيانة الكاملة).
3. اقرأ [`docs/architecture.md`](docs/architecture.md) لفهم كيف ترتبط طبقات الكود ببعضها قبل أي
   تعديل.
4. إن توفر Python، فضّل التحقق التنفيذي الفعلي عبر:
   ```bash
   pip install -e ".[dev]"
   legal-research-skill validate <file.json> --format json
   pytest
   ```
   بدل الاكتفاء بالمراجعة النصية فقط.

## قواعد صارمة عند العمل بهذا المستودع

- لا تخترع مصادر أو اقتباسات أو أرقام آيات/أحاديث — ضع `Requires Verification` عند عدم اليقين.
- التزم بالتسلسل الهرمي `قسم ← باب ← فصل ← مبحث ← مطلب` فقط، إلا بطلب صريح من المستخدم.
- لا تدّعِ أن أي ناتج نهائي، Word-validated، جاهز للطباعة، أو جاهز للتسليم دون تحقق فعلي مطابق
  للحالات الموضحة في [`docs/limitations.md`](docs/limitations.md) و`rules/output-contract.md`.
- لا تشغّل أتمتة Word خارج العملية المعزولة الموجودة أصلًا في `src/legal_research_skill/word/` —
  لا تقتل عمليات `WINWORD.EXE` بشكل عام؛ راجع `src/legal_research_skill/word/processes.py`.
- عند تعديل الكود: حافظ على مزامنة نسخ الـ Schema، لا تُضِف معرّفات قواعد جديدة إلا عبر
  `src/legal_research_skill/rules.py`، ولا تُنقص حد التغطية البرمجية `95%`.
- لا تنشئ Git tag أو GitHub Release إلا بتفويض صريح ومباشر من المستخدم في نفس المحادثة.

## Prompt جاهز لاستخدام الشات العادي (Claude.ai بدون تثبيت)

راجع [`prompts/claude.md`](prompts/claude.md) للنسخة الكاملة مع خطوات الاستخدام والتحذيرات.

## ملفات مرجعية سريعة

| تحتاج | اذهب إلى |
|---|---|
| منهجية إنتاج البحث القانوني | [`SKILL.md`](SKILL.md) |
| قواعد صيانة وتطوير الكود | [`CODEX.md`](CODEX.md) |
| فهم البنية الداخلية | [`docs/architecture.md`](docs/architecture.md) |
| حدود دقيقة لما يُفحص فعليًا | [`docs/limitations.md`](docs/limitations.md) |
| مسارات استخدام حسب الدور | [`playbooks/`](playbooks/) |
