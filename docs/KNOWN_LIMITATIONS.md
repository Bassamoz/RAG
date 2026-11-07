# الحدود المعروفة

آخر مراجعة: 2026-11-07. أساس المرحلة01 متحقق محليًا؛ لا وظائف هوية أو متاجر أو RAG منفذة بعد، ولا جاهزية إنتاجية.

- حُلّ `ENV-01` في 2026-11-07: Docker Desktop وWSL2 مثبتان ويعمل Engine29.9.2 وCompose5.6.1 خارج sandbox. جلسة Codex المقيدة تعمل بحساب `codexsandboxoffline` ولا تقرأ إعداد Docker ولا تصل إلى named pipe؛ التنفيذ المصرح به على المضيف يعمل بحساب المستخدم وسياق `desktop-linux`. لا يتطلب الحل إعادة تثبيت Docker أو تعطيل العزل. الأدلة: runtime-identity-{restricted,host}-20261107.
- نجح تكامل PostgreSQL/pgvector وAlembic وRLS وRedis/Celery وHealth/Readiness بأربع حالات حقيقية، ونجح تشغيل Supabase والـstack مرتين وحفظ الصفوف وبناء الصور. قبول01 متحقق محليًا؛ لا يثبت ذلك هوية البريد أو الحسابات السحابية أو جاهزية الإنتاج.
- منافذ Supabase التي ينشرها CLI المحلي تستمع على0.0.0.0/IPv6 كما في services-final-20261107؛ API والويب وRedis على loopback. هذا إعداد تطوير محلي، وليس إعداد نشر عام. لم تُغير إعدادات firewall أو Docker العامة.
- أداة CUA أفادت No browser is available؛ لا DevTools MCP متصل. تحقق الويب كان build وTypeScript واختبارات HTTP وSSR HTML؛ لا screenshot أو قياس بصري أو وصول يدوي مثبت.
- لا Git أو commit للمجلد الأصلي ولا remote CI run. commits الـcheckout المؤقتة للاختبار المحلي فقط. بصمة الملفات والأدلة تعرف النسخة محليًا، وليست إصدارًا منشورًا.
- Starlette TestClient يحذر من انتقال مستقبلي من httpx إلى httpx2. التحذير ظاهر، والاختبارات الحالية ناجحة؛ يُراجع مسار runner عند ترقية المكتبات.
- تنبيه SCA متوسط `GHSA-g3hv-75wg-m249` في minimatch10.2.6 ضمن eslint-config-next→typescript-eslint→typescript-estree، وهو مسار أدوات lint. [تنبيه المشروع](https://github.com/advisories/GHSA-g3hv-75wg-m249) يحدد الإصلاح في11.0.1 (major مختلف عن نطاق المستهلك). التطبيق لا يقبل glob patterns من API أو مستخدم؛ الأثر المباشر هنا موارد عملية lint عند إدخال pattern خبيث، وCI محدود بمهلة25 دقيقة. التنبيه ما زال مفتوحًا، وتحديث المستهلك أو scoped override يحتاج تحقق توافق. المالك operations/dependencies قبل الإصدار، ومرحلة16 تعيد الفحص. فحص `pnpm audit --audit-level=high` exit0 مع moderate1، وليس «صفر ثغرات». التفاصيل في audit-js-detail.txt.
- حسابات SMTP/Supabase/Salla/Zid/Meta/AI/SMS وإتاحة Llama/ترخيص dataset والخط تبقى غير متحققة كما في سجل الإعداد الخارجي. لا تعادل اختبارات الحدود اتصالًا حيًا.
