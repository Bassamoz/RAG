# العقد الأولي

المصدر FastAPI `create_app().openapi()`؛ تصدير إلى packages/api-client/openapi.json ثم توليد schema.d.ts عبر openapi-typescript. wrapper يستعمل openapi-fetch مع الأنواع المولدة وحارس JSON الفعلي. لا يُحرر الملف المولد يدويًا. فحص CI يقارن التصدير بالملف المحفوظ ويعيد التوليد للمقارنة.

| المسار | الغرض | النتيجة |
|---|---|---|
| GET /api/v1/health | liveness بلا إعدادات حساسة أو اعتماد اتصال | 200 `{status:ok}` |
| GET /api/v1/ready | DB+revision ودور تشغيل محدود، Redis ping وعامل يستجيب عبر active_queues ويستهلك طابور البيئة | 200 أو503 موحد |
| GET /api/v1/openapi.json | عقد public metadata بلا أسرار | schema |

لا endpoints ميزات أو مصادقة في 01. الأخطاء `{error:{code,message,trace_id}}`، ومعرّف الطلب من الخادم ويطابق x-request-id. التحقق من الطلب 422 بلا إعادة عرض قيمه، المسار المفقود404، تجاوز body413، الفشل الداخلي500، غياب خدمة503. تُسجل حقول allowlist JSON (event/entryPoint/request_id/method/status/duration_ms)، بلا body أو query أو tokens أو رسائل exception. Uvicorn access log معطل في أوامر التشغيل حتى لا يسجل query string.

readiness يجري probe للعامل وقد يستغرق عدة ثوان عند الفشل؛ liveness مخصص لفحص العملية، ولا يصنف فشل الاعتماد على أنه موت للعملية. الحدود الأولية max_body_bytes=1MiB؛ parser يراجع bytes الفعلية حتى دون Content-Length. مهلات HTTP على reverse proxy ومراقبة الإنتاج تستكمل في17.
