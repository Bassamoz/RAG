# مستشار المتجر

منصة عربية/إنجليزية لخدمة عملاء المتاجر باستخدام RAG، تُبنى تدريجيًا وفق `codex-plan`. الموجود الآن أساس المرحلة 01: واجهة إعداد بسيطة، API للصحة والجاهزية، عامل Celery، migration أولى وعقود واختبارات. لا تسجيل دخول أو موصل متجر أو RAG منفذ بعد.

## المتطلبات والتثبيت

Node.js 24، pnpm 12.18.0، Python 3.13، uv 0.13.7. للتشغيل الكامل: Docker مع Compose وLinux containers؛ على Windows يلزم Docker Desktop/WSL2. لا حاجة لحساب Supabase سحابي للتطوير المحلي. لا تضع أسرارًا في المحادثة أو Git.

```powershell
npm install --global pnpm@12.18.0
python -m pip install uv==0.13.7
pnpm install --frozen-lockfile
uv sync --project apps/api --frozen
python scripts/dev.py
```

الأوامر نفسها في Linux بعد توفير Docker وNode وPython/uv. سكربت dev يبدأ Supabase محليًا لقاعدة البيانات/Auth/Storage ثم Alembic ودور التشغيل ثم Redis/API/worker/web. يحتفظ بالبيانات عند تشغيله ثانية، ولا reset أو demo seed. يولد `.env.dev` محليًا فقط. الواجهة `http://127.0.0.1:3000` وAPI `http://127.0.0.1:8000`. تفاصيل العوائق الحالية في [SETUP](docs/SETUP.md).

## الفحوص

```powershell
uv run --project apps/api pytest -c apps/api/pyproject.toml tests/unit tests/smoke -q
uv run --project apps/api mypy --config-file apps/api/pyproject.toml apps/api/src/store_advisor
uv run --project apps/api ruff check --config apps/api/pyproject.toml apps/api tests scripts/export_openapi.py scripts/provision_runtime.py scripts/dev.py scripts/ci-integration.py scripts/record_check.py scripts/smoke_local_http.py scripts/diagnose_runtime.py scripts/verify_development.py scripts/verify_clean_checkout.py
uv run --project apps/api python scripts/export_openapi.py
pnpm contract:generate
pnpm contract:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

ضبط `API_ORIGIN=http://127.0.0.1:8000` في بيئة العملية مطلوب للويب؛ البناء لا يتصل بالمزودين. لتشغيل backend منفردًا اضبط DATABASE_URL بدور app_runtime وREDIS_URL وفق `.env.example`؛ الإعدادات الناقصة تفشل برسالة آمنة. health لا يضمن الجاهزية.

اختبار خدمات فعلي (Docker مطلوب، منفصل عن dev):

```powershell
uv run --project apps/api python scripts/ci-integration.py
```

لتشخيص اختلاف طرفية VS Code عن جلسة Codex: `python -X utf8 scripts/diagnose_runtime.py`. ولإثبات التشغيل المحلي مرتين وحفظ الصفوف القائمة: `uv run --project apps/api python scripts/verify_development.py`. أوامر Docker تحتاج الوصول المصرح به إلى محرك المضيف؛ فشل صلاحية sandbox لا يعني أن Docker غير مثبت. تفاصيل Windows في [SETUP](docs/SETUP.md).

ينشئ بيئة اختبار مؤقتة باسم منفصل وكلمات مرور عشوائية، يطبق migration مرتين، يختبر RLS وإعادة استعمال الاتصال وworker roundtrip ثم يوقف خدمات الاختبار. لا يزرع أو يحذف بيانات dev. راجع [TESTING](docs/TESTING.md) و[تقرير 01](docs/phase-reports/01_foundation.md) للنتائج الفعلية؛ وجود workflow لا يثبت نجاح GitHub Actions.

## التنظيم

`apps/web`: Next.js App Router؛ `apps/api/src/store_advisor`: FastAPI والعامل؛ `apps/api/migrations`: Alembic؛ `packages/api-client`: OpenAPI والأنواع المولدة وwrapper صغير؛ `infra`: حاويات التطوير والاختبار؛ `tests`: وحدة وHTTP smoke وتكامل؛ `docs`: القرارات والأدلة والحالة. لا backend ثانٍ، ولا تعديل لمخطط auth المملوك للمزود.

قبل أي تغيير اقرأ AGENTS.md وdocs/PROJECT_STATE.json وdocs/NEXT_ACTIONS.md والمواصفات. لا تبدأ 02 حتى تثبت بوابة 01 أو يوثّق قرار واضح بشأن العمل المستقل عن العائق.
