# تقرير المرحلة 01 — أساس المشروع

التاريخ: 2026-11-06، Asia/Riyadh. نطاق هذه الجلسة المرحلة01 فقط. التنفيذ والتحقق المحلي مستمران حتى إنهاء فحوص الويب؛ بوابة الخدمات الحية محجوبة بغياب Docker/WSL2. لا اعتماد لاكتمال المرحلة أو انتقال02 قبل إثبات تلك البوابة.

## المشكلة وما أُضيف

لم يوجد تطبيق سابق؛ أُضيف أساس واحد مع الحفاظ على y.py ومجلدات المستخدم وcodex-plan وأدلة00. `apps/web` هو Next.js App Router/TypeScript/Tailwind بصفحة إعداد بسيطة وحالة جاهزية حقيقية؛ `apps/api/src/store_advisor` هو FastAPI والعامل Celery من الحزمة نفسها؛ `packages/api-client` عقد OpenAPI وأنواع مولدة وعميل typed؛ `infra` حاويات محلية واختبار منفصلة؛ `tests` وحدة وHTTP smoke وتكامل حقيقي. لا صفحات دخول أو متجر أو مساعد وهمية.

إعدادات بدء التشغيل تُفحص دون طباعة القيم. API health لسلامة العملية، readiness يفحص DB/revision/دور التشغيل وRedis والعامل. middleware يحد body بالبايتات الفعلية، ويولد request_id، ويخرج أخطاء موحدة وسجلات JSON allowlist دون bodies أو secrets. التعليقات توضح سبب حدود الثقة والحراسة، لا تكرر الأسطر.

## قاعدة البيانات والتدفق

أُعد Alembic revision0001 لـapp.users/tenants/memberships/stores وpgvector. RLS وFORCE RLS ودور runtime read-only محدود؛ يُضبط السياق بـtransaction-local لمنع تسرب pool. لا endpoint بيانات محمي حتى تنفذ02 الهوية والعضوية. Alembic autogenerate محصور في app؛ لا تعديل لمخططات auth/storage. كلمة مرور الدور تهيأ خارج migration ولا تدخل history.

مسار dev: Supabase محلي واحد لـPostgres/Auth/Storage → migration/role provisioning → Redis وAPI والعامل والويب. لا reset أو demo seed، ويحفظ .env.dev كلمة مرور الدور لإعادة التشغيل. مسار CI له قاعدة *_test مؤقتة وكلمات مرور مولدة، ولا يعيد استعمال قاعدة dev. تفاصيل العقد والبيئة في API.md وDATABASE.md وSETUP.md.

## الفحوص المثبتة حتى هذه النقطة

الأمر الكامل والوقت والبيئة وexit code وartifact لكل فحص في `docs/evidence/phase-01/*.json`، والنص في الملف المقابل `.txt`. المسجل Python3.14.2؛ API فعلي Python3.13.1، Windows11، Node24.11.1. لا Git أو commit؛ بصمة ملفات الإصدار تحفظ في artifact-manifest عند نهاية العمل.

| الدليل | النتيجة | الحد |
|---|---|---|
| unit-smoke.json | 15 passed، exit0 | 14 وحدة وsmoke1 عبر Uvicorn/TCP؛ لا DB حية |
| lint-python.json / format-python.json / types-python.json | exit0 | Ruff وstrict mypy، دون suppression |
| locked-python.json | exit0 | إعادة uv sync --frozen --offline؛ ليس clean full-stack boot |
| migration-sql.json | exit0 | SQL generation offline فقط، لا migration مطبقة |
| audit-python.json | exit0، No known vulnerabilities found | الاعتماديات التي فحصها pip-audit وقت التشغيل فقط |
| windows-pnpm-shim.json | exit0 | تشغيل pnpm.cmd فعليًا عبر المسار المحلول |
| contract-generate.json / contract-check.json | توليد وتطابق أولي ناجح | تعاد القراءة من أحدث سجل عند إنهاء الويب |
| local-setup.json / integration-launch.json | exit1: Docker غير متاح | blocked_external؛ لا نجاح وهمي |
| integration.json | exit1: حارس البيئة المعزولة رفض التشغيل | لا DB/Redis/worker مثبتة؛ لا skipped محسوب نجاحًا |

فحوص الويب/build/lockfile النهائي وSupabase CLI لم تُعتمد في هذه النسخة من التقرير؛ يتم تحديثها بعد اكتمال التنزيل والتشغيل. GitHub Actions workflow أُعد ولم يُشغّل عن بعد. لا clean checkout أو تشغيل كامل مرتين أو container build ناجح مثبت حتى الآن. لا snapshot سابقة للمشروع؛ الترقية من إصدار منشور أقدم غير منطبقة لهذه البداية، مع بقاء empty DB/rerun مطلوبين.

## الفشل والإصلاح والمراجعة

أخطاء lint/type أثناء الإنشاء أُصلحت بالتنسيق وتعريفات Celery وPydantic plugin، دون إضعاف strict checks. اختبارات regression أظهرت تسرب أجزاء من malformed DSN في مسار API ثم migration (red-config-url/red-migration-url exit1 قبل الإصلاح)، ثم نجحت بعد parser موحد ورسائل آمنة. أُصلح Windows pnpm.cmd، وحُصر Alembic reflection في app. مراجعة مستقلة قراءة فقط موثقة في evidence/phase-01/review.md؛ اختار المستخدم تجاوز cross-model second opinion.

تحذير StarletteTestClient حول انتقال مستقبلي من httpx بقي ظاهرًا ولم يُخفَ. Docker وWSL غير مثبتين؛ لا يمكن لمجرد وجود إعداد Supabase أن يثبت تشغيله أو SMTP. لا سلة/زد/Meta/AI/SMS أو حسابات إنتاجية جُربت في01.

## الحالة والخطوة التالية

R03 تنفيذ موجود مع بوابة acceptance غير متحققة؛ R07 pattern أولي ولا إثبات عزل حي أو هوية؛ R02/R47 التزام مستمر مع تحديث الحالة والشرح. لا production_ready ولا نشر أو commit. أُنجز الممكن المستقل عن الخدمات؛ الخطوة الدقيقة إتاحة runtime ثم تشغيل README مرتين وscripts/ci-integration.py وإصلاح أي فشل يظهر، قبل اعتماد01 أو بدء02.
