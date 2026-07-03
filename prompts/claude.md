<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# استخدام المشروع مع Claude

يوجد مساران لاستخدام هذا المشروع مع Claude: **الشات العادي بدون تثبيت**، و**Claude Code** (تطويري،
يقرأ الملفات محليًا ويمكنه تشغيل أوامر CLI فعليًا).

## المسار 1 — Claude (الشات العادي، بدون تثبيت)

1. افتح [claude.ai](https://claude.ai) في المتصفح.
2. الصق الـ Prompt أدناه في محادثة جديدة.
3. استبدل `[اكتب الموضوع هنا]` بموضوعك.

```text
راجع المستودع التالي والتزم بجميع تعليماته كأنها Skill مفعّلة لديك:
https://github.com/Darhous/arabic-legal-research-skill

اقرأ تحديدًا: SKILL.md وrules/ وchecklists/ وvalidators/. التزم بالتسلسل
الهرمي (قسم ← باب ← فصل ← مبحث ← مطلب)، ولا تخترع مصادر، وضع علامة
"Requires Verification" على أي مصدر غير مؤكد.

بعد ذلك، أعدّ لي: [اكتب الموضوع هنا]

اذكر في النهاية ما التزمت به فعليًا، وما لا يزال يحتاج مراجعتي أو مراجعة
جهة قانونية مختصة قبل أي استخدام رسمي.
```

## المسار 2 — Claude Code (تطويري، محلي)

Claude Code يقرأ ملف `CLAUDE.md` الموجود في جذر هذا المستودع تلقائيًا عند فتح المجلد، بالإضافة إلى
`SKILL.md` إن طُلب منه صراحة.

**الخطوات:**

1. استنسخ المستودع:
   ```bash
   git clone https://github.com/Darhous/arabic-legal-research-skill.git
   cd arabic-legal-research-skill
   ```
2. افتح Claude Code داخل مجلد المشروع:
   ```bash
   claude
   ```
3. استخدم الـ Prompt التالي:

```text
Read CLAUDE.md, SKILL.md, and CODEX.md first. Treat this repository as
the active legal research skill and framework. Follow all rules,
checklists, templates, and validation steps before producing any legal
output. If Python is installed, use the `legal-research-skill` CLI
(validate, schema-check, render-docx, validate-docx, build-artifact) to
verify structural correctness before claiming any result is valid.
```

4. للتحقق التنفيذي الفعلي، اطلب من Claude Code تشغيل:
   ```bash
   pip install -e ".[dev]"
   legal-research-skill validate <your-file.json> --format json
   ```

## الفرق بين المسارين

| | الشات العادي | Claude Code |
|---|---|---|
| يحتاج تثبيت؟ | ❌ لا | ✅ استنساخ + Python اختياري للتحقق التنفيذي |
| يشغّل فحصًا تنفيذيًا حقيقيًا؟ | ❌ لا، تعليمات نصية فقط | ✅ نعم، عبر أوامر CLI |
| مناسب لمن؟ | مستخدم عادي، طالب، محامٍ | مطوّر، باحث يريد تحققًا آليًا |

## تحذير من الهلوسة

حتى مع Claude، **راجع كل مصدر واستشهاد** ذُكر في الناتج قبل استخدامه. علامة "Requires
Verification" تعني أن النموذج نفسه لم يستطع التحقق — وغيابها لا يعني تلقائيًا أن المصدر صحيح 100%.

## الالتزام بـ SKILL.md

راجع [`docs/framework-vs-skill.md`](../docs/framework-vs-skill.md) لفهم لماذا التحقق التنفيذي عبر
Claude Code أقوى من الالتزام النصي وحده في الشات العادي.
