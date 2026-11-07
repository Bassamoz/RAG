# قاعدة البيانات الأساسية

Alembic revision `0001` هو أول revision؛ طُبق فعليًا على PostgreSQL17/pgvector معزولة وفارغة في Docker، ثم أعيد upgrade بنجاح في 2026-11-07. طُبق وأعيد كذلك على Supabase المحلي مع تشغيل التطبيق مرتين وحفظ بصمات الصفوف. الأدلة integration-live-fixed-20261107 وdevelopment-restart-final-20261107 وdatabase-cleanup-verified-20261107 في evidence/phase-01؛ pgvector المحلي0.8.2. لا snapshot إصدار سابق للمشروع، لذلك ترقية نسخة منشورة أقدم غير منطبقة؛ هذا لا يلغي اختبار القاعدة الفارغة وإعادة التطبيق اللذين نجحا. التحقق محلي، ولا يثبت حساب مزود سحابي.

`app.users`: UUID داخلي وauth_subject فريد وcreated_at UTC، بلا password_hash. `app.tenants`: منشأة. `app.memberships`: PK مركب tenant/user ودور وحالة. `app.stores`: tenant FK وunique (tenant_id,id) لربط جداول المراحل التالية بعلاقات مركبة. لا جداول catalog/knowledge فارغة في 01. role platform_admin ليس عضوية tenant؛ تفويضه المنفصل يأتي في 02.

ينشئ migration pgvector في schema extensions، ومخطط app خاصًا ودور app_runtime بلا owner/superuser/BYPASSRLS/CREATEROLE/CREATEDB أو inheritance. كلمة مروره تُهيأ خارج migration بسكربت محلي لا يخزنها في التاريخ. grants الحالية SELECT فقط على الجداول الأساسية؛ لا CRUD حتى حراسة الهوية في 02. RLS مفعّل وFORCE RLS على الجداول الأربعة. لا سياق→لا صفوف؛ users يقرأ نفسه، tenant حسب سياقه، memberships لنفس العضو ضمن tenant، stores حسب tenant واختياريًا store.

`db.scoped_session` يضبط GUC عبر set_config(...,true) داخل transaction؛ لا يجري authenticate أو membership validation بنفسه. يجب على مستهلكه في 02 إثبات العضوية قبل بناء السياق؛ لا endpoint حالي يقبل tenant من body. RLS ليس برهان تفويض سياق مزور بواسطة شفرة خادم موثوقة. أُعد اختبار reuse pool باتصال واحد ونطاقَي tenant وثلاثة متاجر.

أوامر: `uv run --project apps/api alembic -c apps/api/alembic.ini upgrade head` بعد حقن MIGRATION_DATABASE_URL إداري محدود لعملية الترحيل. التشغيل يستعمل DATABASE_URL منفصلًا. لا downgrade مدمر؛ فشل محاولة downgrade واضح مع مسار forward migration أو restore معزول. لا تعديل auth/storage schemas أو grant service_role للمتصفح.
