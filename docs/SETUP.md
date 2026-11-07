# إعداد البيئة

## التشغيل المحلي

اتبع README مع Docker Desktop (Linux containers) وWSL2 على Windows أو Docker Engine/Compose على Linux. Supabase CLI مثبت بإصدار محدد ضمن أدوات المشروع. `python scripts/dev.py` يبدأ stack واحدًا فقط لقاعدة التطبيق/Auth/Storage؛ Compose التطوير يحتوي Redis وAPI والعامل والويب دون PostgreSQL ثانية.

`supabase/config.toml` لا يعرض مخطط app عبر Data API، ويعطل migration/seed التطبيق لدى CLI. Alembic وحده يدير app؛ لا `supabase db reset` ولا توليد auth schema. القيم المحلية من `supabase status -o json` تُقرأ دون طباعتها في الأدلة. `.env.dev` مولد ومستثنى، ويحفظ كلمة مرور runtime لإعادة تشغيل آمنة. Admin DSN لا يُمرر إلى API/worker/web.

أسماء الأسرار في `.env.example` بلا قيم. APP_ENV واحد من dev/test/staging/prod، وAPP_PROFILE واحد من research/production. DATABASE_URL مطلوب بصيغة PostgreSQL+psycopg، REDIS_URL مطلوب، MAX_BODY_BYTES محدود. API_ORIGIN خادمي في الويب ولا يدخل NEXT_PUBLIC. التحقق الفعلي من Supabase والهوية في 02؛ نجاح stack محلي لا يثبت SMTP أو حسابًا إنتاجيًا.

## أدوات هذه الجلسة

الأدوات نُزلت محليًا بدل تعديل PATH النظام: uv في `.venv/Scripts/uv.exe`، pnpm في `.tools/node_modules/pnpm/pnpm.exe`؛ API venv مستقل `apps/api/.venv` بـPython 3.13.1 الموجود. .venv الأولى لأداة تدقيق PDF بقيت محفوظة. يمكن إضافة مسارات الأدوات إلى PATH العملية فقط أو استخدام الأوامر المطلقة. lockfiles: `apps/api/uv.lock` و`pnpm-lock.yaml`.

## تشخيص Windows وCodex

تحقق 2026-11-07 أثبت Docker Desktop4.98.0 وEngine29.9.2 وCompose5.6.1، مع WSL2 وLinux containers. مسار هذا التثبيت لكل مستخدم هو `%LOCALAPPDATA%/Programs/DockerDesktop/resources/bin/docker.exe`؛ غيابه من Program Files لا يعني غياب Docker.

نفّذ `python -X utf8 scripts/diagnose_runtime.py` في طرفية VS Code وقارنه بتشغيل Codex. السكربت يسجل الحساب وPATH المحلول والسياق وإتاحة Engine/Compose، دون قراءة credentials. في هذه الجلسة الحساب المقيد `codexsandboxoffline` يتلقى Access denied عند قراءة إعداد Docker وقناة المحرك، فيسقط السياق إلى `default`. التنفيذ المصرح به على المضيف بحساب المستخدم يصل إلى `desktop-linux` و`npipe:////./pipe/dockerDesktopLinuxEngine`. لم توجد متغيرات DOCKER_HOST/DOCKER_CONTEXT تتجاوز الإعداد.

أوامر Docker/WSL والتكامل هنا تحتاج التنفيذ المصرح به خارج sandbox؛ لا تعديل ACL أو مشاركة إعدادات الاعتماد أو تعطيل العزل. راجع [صلاحيات Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-permission-requirements/) و[سياقات Docker](https://docs.docker.com/engine/manage-resources/contexts/). لا تفسر فشل sandbox باعتباره فشل طرفية المستخدم.

لأدوات المشروع المحلية في PowerShell، عدّل PATH للعملية فقط:

```powershell
$env:PATH="$PWD/.tools/node_modules/pnpm;$PWD/.venv/Scripts;$env:PATH"
$env:PYTHONUTF8='1'
python -X utf8 scripts/diagnose_runtime.py
uv run --project apps/api python scripts/ci-integration.py
uv run --project apps/api python scripts/verify_development.py
```

`verify_development.py` يشغل أمر dev الموثق مرتين، ويتحقق من HTTP وCelery ومن بصمات الصفوف القائمة. عند وجود .env.dev، يتطلب قاعدة قابلة للاتصال لأخذ baseline قبل أول تشغيل؛ إذا كانت متوقفة، شغّل Supabase وحده دون reset ثم أعد التحقق. ينشئ صفًا اصطناعيًا واحدًا بمعرف عشوائي داخل dev المحلي ويحذفه في finally؛ لا reset أو truncate أو seed إنتاجي. في bootstrap جديد، إثبات الحفظ يشمل التشغيل الثاني بعد إضافة الصف، ويذكر المخرج هذا النطاق صراحة.

التشكيلة المحلية تبقي DB/Auth/Storage والبريد المحلي وgateway/PostgREST؛ سكربت dev يستبعد Studio/Realtime/Functions/telemetry وخدماتها الاختيارية عبر --exclude الموثق. خدمة vector المستبعدة شاحن سجلات اختياري؛ امتداد PostgreSQL pgvector المطلوب باقٍ، واختبار وجوده نجح فعليًا. لا تعطيل health checks. التنزيل الأول لصور Supabase وPython/Node قد يستغرق وقتًا؛ الاتصال بالمحرك يختلف عن اكتمال تنزيل الصور. راجع تقرير01 للنتيجة الفعلية الأخيرة.

## staging/prod

هذه المرحلة تجهز أسماء البيئات والتحقق فقط. إعداد النشر العام/TLS والمراقبة وSMTP والتفويض الإنتاجي مراحلها لاحقة؛ compose.yaml محلي وRedis منشور على loopback فقط. لا تستعمله كملف نشر إنتاجي. لا تُرسل قنوات خارجية أو بيانات فعلية من research profile.
