<!-- تصميم: أحمد درهوس (Ahmed Darhous) — https://github.com/darhous | Instagram: https://www.instagram.com/darhous/ | LinkedIn: https://www.linkedin.com/in/darhous/ -->

# استخدام المشروع مع ChatGPT

## طريقة الاستخدام (بدون أي تثبيت)

1. افتح [ChatGPT](https://chat.openai.com) في المتصفح.
2. الصق الـ Prompt أدناه في محادثة جديدة.
3. استبدل `[اكتب الموضوع هنا]` بموضوعك.

> ملاحظة: إن كان الموديل الذي تستخدمه لا يدعم تصفح الروابط مباشرة (بدون خاصية Browse/Search)،
> افتح [`SKILL.md`](../SKILL.md) بنفسك وانسخ محتواه كاملًا وألصقه في المحادثة بدل الرابط، ثم أكمل
> بنفس التعليمات.

## Prompt جاهز لـ ChatGPT

```text
راجع المستودع التالي والتزم بجميع تعليماته كأنها Skill مفعّلة لديك:
https://github.com/Darhous/arabic-legal-research-skill

اقرأ تحديدًا: SKILL.md وrules/ وchecklists/. التزم بالتسلسل الهرمي
(قسم ← باب ← فصل ← مبحث ← مطلب)، ولا تخترع مصادر أو اقتباسات، وضع علامة
"Requires Verification" على أي مصدر لا يمكنك التحقق منه فعليًا.

بعد ذلك، أعدّ لي: [اكتب الموضوع هنا]

لا تعلن أن الناتج نهائي أو جاهز للتسليم دون تطبيق قوائم المراجعة في checklists/
وإخباري صراحة بما يحتاج مراجعتي أنا أو مراجعة جهة قانونية مختصة.
```

## تحذيرات مهمة عند استخدام ChatGPT تحديدًا

- ChatGPT قد لا يحتفظ بكل تفاصيل `SKILL.md` عبر محادثة طويلة جدًا — إذا لاحظت تراجعًا في الالتزام
  (نسيان قاعدة، أو ترتيب مختلف)، أعد لصق الـ Prompt أو ذكّره بالملف المحدد (مثلًا: "راجع
  rules/footnotes.md مرة أخرى قبل المتابعة").
- بعض إصدارات ChatGPT لا تفتح روابط GitHub تلقائيًا؛ في هذه الحالة الصق محتوى `SKILL.md` مباشرة.
- ChatGPT هنا يعمل بالطبقة الأولى فقط (تعليمات نصية) — لا يشغّل أي فحص تنفيذي حقيقي (`legal-research-skill validate`).
  إن أردت تحققًا تنفيذيًا فعليًا، راجع [`docs/quickstart.md`](../docs/quickstart.md) المسار الرابع
  (المطوّر عبر CLI)، أو استخدم [`prompts/claude.md`](claude.md) أو [`prompts/codex.md`](codex.md)
  مع Claude Code/Codex اللذين يمكنهما تشغيل الأوامر فعليًا.

## الالتزام بـ SKILL.md

راجع [`prompts/general-use.md`](general-use.md) للنسخة العامة الكاملة من هذا الـ Prompt، ولمزيد من
التفاصيل حول حدود ما يفحصه المشروع فعليًا راجع [`docs/limitations.md`](../docs/limitations.md).
