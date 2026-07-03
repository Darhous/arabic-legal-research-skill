<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# مسار المطوّر

## لمن هذا المسار؟

لمطوّر يريد استخدام الطبقة التنفيذية الكاملة (CLI، Schema، DOCX Pipeline)، أو دمجها في نظام أكبر،
أو المساهمة في تطوير المشروع نفسه.

## متى أستخدمه؟

- بناء أداة أو خدمة فوق `legal-research-skill` (تحقق آلي، توليد DOCX، بوابة Word).
- المساهمة في الكود، الاختبارات، أو التوثيق التقني للمشروع.
- تشغيل التحقق التنفيذي الكامل بدل الاعتماد على التزام نموذج لغوي فقط.

## خطوات التنفيذ

1. ثبّت المشروع (راجع [`docs/quickstart.md`](../docs/quickstart.md) المسار الرابع):
   ```bash
   git clone https://github.com/Darhous/arabic-legal-research-skill.git
   cd arabic-legal-research-skill
   python -m venv .venv && source .venv/bin/activate   # أو .venv\Scripts\activate على Windows
   pip install -e ".[dev]"
   pytest
   ```
2. اقرأ [`docs/architecture.md`](../docs/architecture.md) لفهم الطبقات قبل أي تعديل.
3. لأي تعديل كود، اقرأ [`CODEX.md`](../CODEX.md) كاملًا — يحدد قواعد صارمة (مزامنة Schema، سجل
   معرّفات القواعد المركزي، عزل أتمتة Word، حظر الادّعاءات غير المدعومة بدليل).
4. أضف اختبارات لأي سلوك جديد أو مُصلَح — حد التغطية المفروض `95%` (`--cov-fail-under=95`).
5. قبل أي Commit: `python -m compileall src && ruff format --check . && ruff check . && pytest`.
6. لا تُنشئ Release أو Tag دون تفويض صريح — راجع سياسة الإصدار في `.github/workflows/release.yml`
   (بناء وتحقق فقط، لا نشر تلقائي).

## Prompt جاهز (لاستخدامه مع Claude Code أو Codex أثناء التطوير)

```text
Read CODEX.md and docs/architecture.md fully before making any change.
Keep schema copies in sync (schemas/*.json and
src/legal_research_skill/schemas/*.json). Add or update tests for any
behavior change and keep coverage >= 95%. Do not add new rule IDs
outside src/legal_research_skill/rules.py. Do not weaken claim-boundary
checks in validators/output_claims.py or rules/output-contract.md.
Run python -m compileall src, ruff format --check ., ruff check ., and
pytest before considering the change complete.
```

## أخطاء يجب تجنبها

- ❌ تعديل `schemas/*.json` دون تحديث النسخة المطابقة في `src/legal_research_skill/schemas/`.
- ❌ إضافة معرّف قاعدة (Rule ID) خارج `src/legal_research_skill/rules.py`.
- ❌ تشغيل أتمتة Word خارج `src/legal_research_skill/word/` أو بدون مهلة زمنية (Timeout).
- ❌ خفض حد التغطية `95%` أو حذف اختبارات لتمرير CI بدل إصلاح السبب الجذري.
- ❌ الدفع (`push`) أو إنشاء Tag/Release دون طلب صريح من المستخدم في نفس الجلسة.

## مخرجات متوقعة

كود يمر بكل بوابات الجودة (compileall، ruff، pytest بتغطية ≥95%)، متسق مع الـ Schema والاختبارات،
ولا يخالف أي حدود ادّعاء موثقة في [`docs/limitations.md`](../docs/limitations.md).
