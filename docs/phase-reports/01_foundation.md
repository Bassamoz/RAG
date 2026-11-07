# تقرير المرحلة 01 — الأساس والتحقق المحلي

التاريخ: 2026-11-07، Asia/Riyadh. **الحالة: verified_local للمرحلة01 فقط**. اكتملت شروط قبولها محليًا: تكامل PostgreSQL/Redis/Celery/Alembic حقيقي، Health/Readiness بحالات النجاح والفشل، تثبيت من checkout نظيف، بناء الحاويات وتشغيل التطوير مرتين مع حفظ البيانات. لم تبدأ02؛ لا اعتماد لجاهزية المنتج الكاملة أو الإنتاج أو التكاملات السحابية.

## المشكلة وما تغير

استؤنف المشروع القائم دون scaffold أو backend أو قاعدة تطبيق ثانية. احتُفظ بـy.py والبحث وcodex-plan وأدلة00 وإعدادات المستخدم. بقيت البنية apps/web وapps/api وpackages/api-client وinfra وscripts وtests وdocs. نسخ الحالة والتقرير قبل المتابعة محفوظة في evidence/phase-01/*before-runtime-followup-20261107.*.

الفشل السابق في الوصول إلى Docker داخل Codex لم يكن غياب تثبيت Docker بعد تجهيز المستخدم البيئة. التنفيذ Windows أصلي64bit، وليس داخل WSL. الحساب المقيد codexsandboxoffline لا يقرأ إعداد Docker ولا يصل إلى named pipe، فيظهر السياق default؛ التنفيذ المصرح به على المضيف بحساب المستخدم يصل إلى desktop-linux. الأدلة runtime-identity-{restricted,host}-20261107 تسجل الفرق دون credentials. لم نغير ACL أو إعداد Docker أو firewall أو سياق المستخدم.

الأدوات الفعلية: Docker Desktop4.98.0، Engine29.9.2 API1.56 linux/amd64، Compose5.6.1، WSL2 docker-desktop. التثبيت لكل مستخدم في LocalAppData؛ غيابه من Program Files لا يعني أنه غير مثبت. المسجل Python3.14.2، API محليًا Python3.13.1 وفي صورة البناء3.13.18، وNode المحلي24.11.1. تفسير الصلاحيات والسياق متسق مع [وثائق Desktop](https://docs.docker.com/desktop/setup/install/windows-permission-requirements/) و[سياقات Docker](https://docs.docker.com/engine/manage-resources/contexts/).

التغيير السلوكي في apps/api/src/store_advisor/main.py: ping لأي عامل على broker كان يعطي Readiness200 حتى إن كان العامل يستمع لطابور بيئة أخرى. أظهر اختبار تكامل فاشل الخلل؛ استُبدل بفحص active_queues ومطابقة task_default_queue بمهلة محددة، ثم نجحت الحالات الأربع. فحص الطابور يثبت وجود مستهلك يستجيب؛ اختبار roundtrip منفصل يثبت تنفيذ المهمة. [مرجع Celery](https://docs.celeryq.dev/en/stable/userguide/monitoring.html).

أضيفت scripts/diagnose_runtime.py وverify_development.py وverify_clean_checkout.py، واختبارات الرجوع في tests/integration/test_services.py وtests/unit/test_verification_environment.py. حُدّثت قوائم Ruff في README وCI. سكربت dev يبقي خدمات Supabase المطلوبة ويستبعد Studio/Realtime/Functions/telemetry وخدماتها الاختيارية؛ لا تعطيل health checks. خدمة vector الاختيارية شاحن سجلات، بينما امتداد pgvector المطلوب باقٍ ومثبت بالاختبار.

## التدفق وحدود المسؤولية

Supabase محلي واحد يوفر PostgreSQL/Auth/Storage والبريد المحلي وgateway/PostgREST. Alembic يدير app.users/tenants/memberships/stores وrevision0001 وpgvector؛ لا يدير auth/storage المملوكين للمزوّد. تهيئة كلمة مرور app_runtime خارج migration، وملف .env.dev محلي مستثنى من Git ولا تطبع قيمه. API والعامل يأخذان دور تشغيل محدودًا؛ Admin DSN مخصص للمهاجرات والتدقيق المحلي.

RLS وFORCE RLS يطبقان سياق transaction-local حتى لا ينتقل بين اتصالات pool. لا سياق => لا صفوف، ومتجر مستأجر آخر => لا صفوف. ربط هذا السياق بهوية وعضوية موثوقتين من مسؤولية02؛ لا API بيانات محمية أو هوية وهمية مضافة في01.

الويب Next يقرأ الجاهزية عبر عميل TypeScript مولد من OpenAPI. الصفحة العربية RTL تعرض حالة فعلية؛ Health لسلامة العملية، وReadiness لدور DB وrevision وRedis ومستهلك طابور البيئة. الأخطاء موحدة بمعرف طلب، والسجل allowlist دون bodies أو tokens أو secrets.

## الأدلة والنتائج الفعلية

كل سجل JSON أدناه يحفظ الأمر الكامل وexit code والوقت والبيئة وبصمة المخرج النصي، وله ملف txt مقابل في docs/evidence/phase-01. فحوص الخدمات تحتاج الوصول المصرح به لمحرك المضيف؛ فشل sandbox يسجل نتيجة تشخيصية، لا فشل تثبيت.

| الدليل | النتيجة | النطاق |
|---|---|---|
| runtime-identity-host-20261107؛ docker-engine-20261107؛ docker-compose-20261107 | exit0 | Engine/Compose/WSL متاحة فعليًا |
| runtime-identity-restricted-20261107 | exit1 متوقع | اختلاف حساب وصلاحيات sandbox |
| integration-queue-red-20261107 | 1 failed،3 passed، exit1 | إثبات خلل الطابور قبل الإصلاح |
| integration-live-fixed-20261107 | 4 passed، exit0 | PostgreSQL17/pgvector، migration من DB فارغة وإعادتها، RLS/pool، Redis، worker roundtrip، Health/Readiness والحالات السلبية |
| checkout-env-red-20261107 ثم checkout-env-green-20261107 | exit1 ثم exit0 | توريث GIT_DIR كان يختار مستودعًا آخر؛ عُزلت متغيرات GIT_* |
| clean-checkout-final-isolated-20261107 | exit0؛16 Python و5 TypeScript |65 ملفًا مطابقًا byte-for-byte؛ uv/pnpm frozen offline؛ typecheck؛ root Git HEAD/index محفوظان |
| container-api-build-20261107؛ container-web-build-20261107 | exit0 لكليهما | بناء Linux فعلي؛ Next16.4.5 وتجميع TypeScript ناجحان |
| container-images-20261107 | exit0 | IDs وOS/architecture ومستخدم app/node دون ENV أو أسرار |
| development-restart-minimal-20261107 | exit0 | bootstrap جديد ثم تشغيل ثانٍ وsentinel محفوظ؛ أول إثبات للـstack الكامل |
| development-restart-final-20261107 | exit0 | baseline قبل أول تشغيل، ثم تشغيلان وHealth200/Readiness200/Web200 وCelery roundtrip وحفظ الصفوف؛ preservation_scope=both_starts |
| database-cleanup-verified-20261107 | exit0 | إزالة sentinel فقط؛ الصفوف عادت إلى0 كما كانت؛ revision0001، pgvector0.8.2، ومخططا auth/storage موجودان |
| services-final-20261107 | exit0 | API/Redis وSupabase ذات health checks سليمة؛ العامل والويب يعملان |
| lint-final-20261107؛ format-final-20261107؛ types-followup-20261107 | exit0 | Ruff وstrict mypy دون suppression |
| openapi-export-final-20261107؛ contract-after-export-20261107 | exit0 | التصدير من API الحالية وتطابق العميل المولد |
| phase00-final-20261107 | exit0 | سلامة checkpoint التخطيط ومعاني المتطلبات؛ ليس اختبار منتج |

المجموع الوظيفي دون تكرار تشغيل الحالات نفسها:16 Python (15 وحدة وHTTP smoke1)، و4 تكامل، و5 TypeScript. الاختبارات لا تستبدل PostgreSQL أو Redis أو worker بـmock. الحالات السلبية تشمل فشل DB وRedis وغياب مستهلك لطابور البيئة، فلا تعطي Readiness200؛ Health يبقى200 عند فشل الاعتماد. بيئة التكامل *_test بكلمات مرور مولدة وtmpfs؛ أزيلت حاوياتها وشبكتها فقط، وبقيت خدمات dev وبياناتها.

آخر checkout محفوظ في tmp/foundation-checkout-079a4707d3/checkout، commit اختبار محلي 2d9df46f78e71133e36495cf847f07f32468ac32. بصمة مصدر65 ملفًا: e735fe25df9c7af61c00f30becb84028b692577a25657e47f03146226abbbfb4. هذا يطابق المصدر الحالي؛ وثائق الأدلة اللاحقة لها بصماتها في artifact-manifest. لا Git/commit للمجلد الأصلي، ولا push أو remote CI run.

## التشغيل وإعادة التحقق

تفاصيل التثبيت في README وSETUP. في جلسة Windows الحالية يمكن إضافة أدوات المشروع إلى PATH العملية فقط:

~~~powershell
$env:PATH="$PWD/.tools/node_modules/pnpm;$PWD/.venv/Scripts;$env:PATH"
$env:PYTHONUTF8='1'
python -X utf8 scripts/diagnose_runtime.py
uv run --project apps/api python scripts/ci-integration.py
uv run --project apps/api python scripts/verify_development.py
~~~

verify_development يأخذ baseline قبل أول تشغيل عندما توجد .env.dev وقاعدة قابلة للاتصال؛ يرفض المتابعة إن تعذر ذلك. عند bootstrap جديد يذكر صراحة أن إثبات الحفظ يتعلق بالتشغيل الثاني المعبأ. ينشئ sentinel بمعرف عشوائي ويحذف ذلك المعرف في finally فقط؛ لا reset أو truncate أو demo seed. المقارنة تشمل بصمات الصفوف المرتبة في الجداول الأربعة، لا مجرد عددها. اختبار checkout الحالي خاص بأدوات Windows المحلية؛ workflow Linux موجود لكنه لم يُشغّل عن بعد.

خدمات التطوير تُركت تعمل: الواجهة http://127.0.0.1:3000، Health http://127.0.0.1:8000/api/v1/health وReadiness http://127.0.0.1:8000/api/v1/ready. API والويب وRedis منشورة على loopback. منافذ Supabase المحلية التي نشرها CLI تستمع على0.0.0.0/IPv6 كما في services-final؛ هذه بيئة تطوير محلية، وليست إعداد نشر عام أو إنتاج.

## الأخطاء والإصلاحات وحدود الاعتماد

استغرق تنزيل الصور والحزم وقتًا طويلًا. أُوقفت المحاولة الأولى أثناء التنزيل لتقليل الخدمات الاختيارية (development-restart-first-20261107، ليس نتيجة اختبار تطبيق)، ثم نجحت المحاولتان اللاحقتان. الصور المطلوبة كلها اكتملت؛ عائق Docker القديم محلول. أداة crane نُزل جزء منها للتشخيص ثم أُوقف قبل الاستخدام؛ ليست dependency أو مسار تشغيل للمشروع.

فشل checkout أولًا بسبب autocrlf ثم بسبب ACL لمجلد pytest Temp بين حسابي sandbox والمضيف. أُصلح autocrlf ضمن أوامر fixture فقط، وعُزل مجلد pytest داخل fixture فريد؛ لم تتغير إعدادات Git العامة أو ACL أو assertions. فشل أمر تدقيق cleanup إضافي بسبب اقتباس PowerShell؛ أُعيد من ملف Python ثابت ونجح. جميع أدلة الفشل بقيت محفوظة.

مراجعة مستقلة بسياق جديد كشفت خطر متغيرات Git وفجوة baseline قبل التشغيل الأول؛ أُصلحا وأعيدت المراجعة دون ملاحظات إضافية. التفاصيل runtime-review-20261107.md. احترمنا اختيار المستخدم تجاوز رأي ثانٍ بنموذج مختلف.

تحذير Starlette حول httpx بقي ظاهرًا. تنبيه minimatch متوسط في أدوات lint مفتوح كما في KNOWN_LIMITATIONS؛ فحص high/critical من الجلسة السابقة exit0 مع moderate1 وpip-audit لم يجد known vulnerabilities وقت فحصه، وليست نتيجة «صفر ثغرات». لا ترقية dependency في هذه المتابعة. لا snapshot إصدار سابق قبل0001، لذلك ترقية إصدار منشور أقدم غير منطبقة؛ DB فارغة ثم rerun مثبتان.

لا تحقق بصري بمتصفح، ولا SMTP/OTP خارجي أو حساب Supabase سحابي أو سلة/زد/Meta/AI/SMS. صحة Auth/Storage المحلية لا تثبت تدفقات الهوية أو مزودًا إنتاجيًا. لا RAG أو تسجيل دخول أو نشر منفذ. R03 متحقق محليًا في نطاق01، وR07 نمط DB جزئي مثبت؛ R02/R47 مستمران.

## الخطوة التالية

المرحلة01 معتمدة محليًا، والمرحلة02 ما زالت planned. عند طلبها اقرأ AGENTS والمواصفات والحالة وNEXT_ACTIONS وprompts/02_identity_tenancy.md، ثم نفذ الهوية والجلسات والتفويض فوق الموجود. لا scaffold ولا إعادة reset لقاعدة dev، ولا بدء تلقائي للمرحلة التالية.
