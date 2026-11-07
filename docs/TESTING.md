# مصفوفة الاختبارات وخطة الأدلة

فحص checkpoint المرحلة 00: `python -X utf8 scripts/validate_phase00.py`. يتحقق من اكتمال السجل 48/48 ومعنى المتطلبات وملفات الأدلة و19 مرحلة في الحالة المؤرشفة `evidence/phase-00/planning-state.json` وhash البحث، لا من عمل التطبيق الحالي. قيود الحالة القديمة (كل المراحل اللاحقة planned) تخص snapshot قبل بدء01؛ لا يجوز تطبيقها على الحالة الحية بعد التقدم. نتائج التطبيق الحديثة في evidence/phase-01 وتقرير01، لا في سجل00 التاريخي.

| المستوى | السيناريوهات/المراجع | البيئة/الأداة المخططة | البوابة |
|---|---|---|---|
| وحدة | T-R19..22: scores/vectors/ties؛ T-R29 fake clock؛ intent/normalization | pytest، Vitest؛ deterministic بلا مزود | 06–09 |
| هوية | T-R04..07: OTP invalid/expired/reuse وrefresh races وrevocation/AAL2/RLS/pool | Supabase محلي + Postgres/pgvector حقيقي، httpx | 02 |
| بيانات | T-R10..18: Decimal/import/formula/partial/extract/publish/delete race | pytest وDB/storage/Redis محلي | 04–07 |
| عقود | T-R12..15 وT-R31..32: refresh/revoke/429/duplicate/out-of-order/unknown send | fixtures موثقة عند حد الشبكة؛ لا تعادل نجاح المزود | 05،10 |
| مزود حي | بريد/سلة/زد/Meta/SMS/model: دليل EXTERNAL_DEPENDENCIES | sandbox مملوك؛ blocked_external حاليًا | 02،05،08،10 |
| RAG | T-R23..26: ثمانية أنواع/SKU/نفي/غموض/سعر متغير/تعارض/injection | deterministic policies ثم نموذج حقيقي بميزانية | 08 |
| محادثة ودعم | T-R27..34: origin/XSS/reconnect/takeover/assignment concurrency | API integration ثم Playwright | 09–11 |
| تحليل ودورة حياة | T-R35..39: denominator/timezone/export/restore/tombstone | DB+files حقيقية وoutbound off | 12–13،17 |
| بحث | T-R40..41: provenance/dev-test/gold/ablations | Llama مثبت + FAISS وريرنكر حقيقي؛ human review/RAGAS معلن | 14 |
| نظام | T-R42..43: رحلة تاجر/عميل/موظف/مدير؛ load/crash/migration | Playwright/axe/k6؛ workload ACCEPTANCE_BUDGETS | 15 |
| أمان | T-R44..45: threat abuse وASVS L2 mapping وSAST/SCA/secrets/container/DAST | بيئة staging نملكها فقط | مبكرًا ثم 16 |
| نشر وإصدار | T-R46..48: immutable build/TLS/rollback/restore/fresh evidence | staging ثم gate على commit محدد | 17–18 |

كل requirement له T-Rxx بالتفصيل في REQUIREMENTS_TRACEABILITY؛ fixtures لمستأجرين وثلاثة متاجر وكل الأدوار، ومصدر محذوف وpolicy conflict وwebhook مكرر وملف خبيث مصطنع. الأدلة تحفظ command/exit_code/time/environment/code hash أو commit/artifact/limitation. النتيجة skipped أو غياب السر ليست pass. لا قياس جودة نموذج بالـmock. لا تعديل test set أو عتبة قبول لإخفاء فشل.

## نتائج المرحلة 01 الحالية

في متابعة 2026-11-07 نجح scripts/ci-integration.py على PostgreSQL17/pgvector وRedis7.4 في Docker مع عامل Celery فعلي:4 حالات، exit0 في integration-live-fixed-20261107. طبق Alembic revision0001 على قاعدة فارغة وأعاده؛ تحقق من الدور المحدود وRLS لمستأجرين وثلاثة متاجر، ومسح سياق transaction عند إعادة استخدام pool، ووجود vector. نجح Health200 وReadiness200 وworker roundtrip. فشل DB أو Redis أو غياب مستهلك طابور البيئة أعطى Readiness503؛ Health بقي200 عند فشل DB/العامل. اختبار الطابور المختلف فشل قبل الإصلاح ثم نجح؛ دليل red محفوظ، ولا mock يحل محل الخدمات.

نجح checkout Git محلي مؤقت خالٍ من dependencies والأسرار، مع مقارنة65 ملفًا byte-for-byte: uv/pnpm frozen offline ثم16 Python (15 وحدة وHTTP smoke1) وخمسة TypeScript وtypecheck. clean-checkout-final-isolated-20261107 يذكر commit اختبار محلي وبصمة المصدر؛ مستودع المستخدم الأصلي محفوظ. بعد كشف توريث GIT_* وACL لمجلد Temp، عُزلت بيئة Git ومجلد pytest دون تجاهل اختبار أو تغيير ACL.

نجح بناء صورتي API والويب في Docker، بما فيه Next/TypeScript داخل Linux. development-restart-final-20261107 أثبت baseline قبل أول تشغيل، ثم تشغيلين عبر scripts/dev.py، وHealth200/Readiness200/Web200 وCelery roundtrip، وتطابق بصمات صفوف الجداول الأربعة. حُذف sentinel الخاص بالتحقق فقط، وأثبت database-cleanup-verified-20261107 عودة الصفوف إلى عددها السابق، وrevision0001 وpgvector0.8.2 ووجود مخططي auth/storage. خدمات dev بقيت تعمل، وبيئة التكامل المؤقتة أزيلت.

Ruff/format وstrict mypy وتصدير OpenAPI وتطابق العميل المولد ناجحة. checkpoint00 النهائي نجح بوصفه فحص تخطيط فقط. audit-js من الجلسة السابقة high exit0 مع moderate1 مفتوحة، وpip-audit لم يجد known vulnerabilities وقت الفحص؛ لا ادعاء صفر ثغرات. لا remote CI أو screenshot أو SMTP/OTP خارجي أو RAG. قبول01 متحقق محليًا؛ كل مزود أو ميزة لاحقة يحتفظ بحالته الخاصة.

الأوامر وexit codes والأوقات والبيئة وبصمات المخرجات في evidence/phase-01/*.json و.txt، وبصمات المصدر والوثائق في artifact-manifest.json، والتفاصيل في phase-reports/01_foundation.md. فشل أو إيقاف محاولات التحضير القديمة محفوظ ومصنف، ولا يُحسب نجاحًا.
