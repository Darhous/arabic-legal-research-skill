<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# دليل البدء السريع (Quickstart)

اختر مسارك حسب مستواك التقني — كل المسارات موصلة لنفس المنهجية، لكن بعمق تحقق مختلف. راجع
[`docs/framework-vs-skill.md`](framework-vs-skill.md) لفهم الفرق بين المسارات.

## المسار 1 — مستخدم عادي (بدون أي تثبيت)

الأسرع والأبسط، مناسب لأي طالب أو باحث لا يريد التعامل مع أدوات تقنية.

1. افتح ChatGPT أو Claude في المتصفح.
2. أرسل رابط هذا المستودع: `https://github.com/Darhous/arabic-legal-research-skill`
3. اطلب منه الالتزام بتعليمات `SKILL.md` كأنها Skill مفعّلة لديه.
4. اطلب البحث أو المذكرة أو المراجعة القانونية التي تحتاجها.

Prompt جاهز كامل موجود في [`prompts/chatgpt.md`](../prompts/chatgpt.md) وفي قسم README الرئيسي.

## المسار 2 — Claude Code (تطويري، محلي)

1. استنسخ المستودع:
   ```bash
   git clone https://github.com/Darhous/arabic-legal-research-skill.git
   cd arabic-legal-research-skill
   ```
2. شغّل `claude` داخل المجلد.
3. اطلب منه قراءة `SKILL.md` و`CODEX.md` و`CLAUDE.md` أولًا.

التفاصيل الكاملة والـ Prompt الجاهز في [`prompts/claude.md`](../prompts/claude.md).

## المسار 3 — OpenAI Codex (تطويري، محلي)

1. استنسخ المستودع وافتح `codex` داخله.
2. اطلب منه قراءة `README.md` و`SKILL.md` و`CODEX.md` والمجلدات الأساسية أولًا.

التفاصيل الكاملة والـ Prompt الجاهز في [`prompts/codex.md`](../prompts/codex.md).

## المسار 4 — مطوّر (تحقق تنفيذي حقيقي عبر CLI)

هذا المسار الوحيد الذي يُشغّل الفحص التنفيذي الحقيقي (Schema + Validators + DOCX + Word gate).

```bash
git clone https://github.com/Darhous/arabic-legal-research-skill.git
cd arabic-legal-research-skill
python -m venv .venv
```

فعّل البيئة الافتراضية (Windows: `.venv\Scripts\activate`، macOS/Linux: `source .venv/bin/activate`)،
ثم:

```bash
python -m pip install -U pip
pip install -e ".[dev]"
pytest
```

تحقق من نجاح التثبيت:

```bash
legal-research-skill list-validators
```

أول أمر تحقق حقيقي:

```bash
legal-research-skill schema-check examples/fixtures/valid/minimal-valid.json --format json
legal-research-skill validate examples/fixtures/valid/minimal-valid.json --format json
```

المتطلبات: Python `>=3.11`. بوابة Word تتطلب Windows + Microsoft Word + `pywin32` وهي **اختيارية**.
راجع [`docs/limitations.md`](limitations.md) لحدود كل مسار، و[`workflows/`](../workflows/) لسيناريوهات
استخدام كاملة خطوة بخطوة.

## الخطوة التالية حسب دورك

| دورك | اذهب إلى |
|---|---|
| طالب | [`playbooks/student.md`](../playbooks/student.md) |
| محامٍ | [`playbooks/lawyer.md`](../playbooks/lawyer.md) |
| باحث | [`playbooks/researcher.md`](../playbooks/researcher.md) |
| مطوّر | [`playbooks/developer.md`](../playbooks/developer.md) |
| مستخدم عادي | [`playbooks/general-user.md`](../playbooks/general-user.md) |
