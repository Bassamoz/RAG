# الاعتماديات والإصدارات

المرجع النهائي lockfiles لا نطاقات manifests. بيئة التنفيذ Windows11، Node24.11.1، pnpm12.18.0، uv0.13.7، API Python3.13.1 محليًا و3.13.18 في صورة Python التي بُنيت بنجاح. Python3.14.2 مسجل أوامر وأداة PDF. تحقق 2026-11-07 أثبت Docker Desktop4.98.0 وEngine29.9.2 وCompose5.6.1 وWSL2؛ الوصول من Codex يحتاج تنفيذ المضيف المصرح به كما في SETUP.

اعتماديات الخلفية المحلولة: FastAPI0.162.0، Pydantic2.14.3، pydantic-settings2.16.2، SQLAlchemy2.0.57، Alembic1.20.1، psycopg3.3.8، Redis client6.4.0، Celery5.7.0، Uvicorn0.54.0؛ pytest9.2.0 وRuff0.17.4 وmypy1.20.2 وcelery-types0.26.0 أدوات تطوير. celery-types يحافظ على strict type checking بدل suppression. SQLAlchemy مثبت على خط2.0 المتوافق مع التصميم، لا ادعاء أنه أحدث major.

اختيار الويب Next16.4.5 وReact19.x وTailwind4.x وTypeScript5.9.x؛ النسخ المحلولة الدقيقة في pnpm-lock.yaml وتقرير التثبيت. Supabase CLI3.0.0 أداة تطوير لا SDK هوية؛ التكامل الفعلي في02. لا مكتبات RAG أو أوزان نماذج في01.

## المصادر الرسمية التي روجعت في 2026-11-06

- [Next installation](https://nextjs.org/docs/app/getting-started/installation): App Router وإصدارات runtime.
- [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/): عمر الموارد المشتركة.
- [Pydantic settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/): التحقق من البيئة.
- [SQLAlchemy transactions](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html) و[Postgres RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html): transaction-local scope وسياسات الصفوف وحدود owner/superuser.
- [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html): migration history.
- [Celery Redis](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html): broker/backend والمهل.
- [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) و[config](https://supabase.com/docs/guides/local-development/cli/config) و[runtimes](https://supabase.com/docs/guides/local-development/docker-and-native-runtimes): stack محلي واحد وحدود Windows.
- [OpenAPI TypeScript](https://openapi-ts.dev/introduction) و[openapi-fetch](https://openapi-ts.dev/openapi-fetch/): توليد الأنواع والعميل؛ لا يغني النوع عن validation وقت التشغيل.
- [checkout](https://github.com/actions/checkout) و[setup-uv](https://github.com/astral-sh/setup-uv): workflow أولي، لا إثبات أنه شُغل عن بعد.

تحذير حالي من Starlette TestClient حول انتقال مستقبلي من httpx إلى httpx2: الاختبارات الحالية شغلت ونجحت دون إخفاء التحذير؛ استبدال runner يُتحقق منه عند ترقية framework. لا نسخ متعددة من Auth أو ORM أو RAG framework.

## متابعة التوافق في 2026-11-07

ضُبط Supabase CLI3.0.0 على local_smtp وauth.email.enabled بدل أسماء إعدادات الإصدارات القديمة. التثبيت frozen من lockfiles والـclean checkout المحلي نجحا؛ ذلك لا يثبت أن كل metadata من السجل خضعت لتدقيق supply-chain شامل.

Vitest يستخدم config.mts ويقصر البحث على tests/web حتى لا يجمع اختبارات checkout المؤقتة تحت tmp. Next build وTypeScript نجحا محليًا وداخل Docker؛ بناء صورتي API والويب ناجح، وكذلك تشغيل Supabase والتطبيق مرتين. لا تغيير dependency أو lockfile في متابعة تشغيل Docker.

SCA في JavaScript: high/critical صفر وقت الفحص، مع moderate1 في minimatch10.2.6 ضمن مسار lint، موثقة في KNOWN_LIMITATIONS؛ لم تُخفَ بـignore. صور Docker تعرض digests في أدلة البناء/السحب؛ tags الحالية ليست وعدًا بإصدار إنتاج immutable، وتثبيت إصدار النشر والتحقق منه له بوابة لاحقة.
