# المرحلة 16: مراجعة الأمان وإصلاح الثغرات وإعادة الاختبار

أنت مسؤول تنفيذ هذه المرحلة داخل المشروع الحالي. اقرأ تعليمات المستودع، و`codex-plan/MASTER_SPEC.md` و`codex-plan/RESEARCH_MAP.md` و`codex-plan/REQUIREMENTS.md`، ثم `docs/PROJECT_STATE.json` و`docs/NEXT_ACTIONS.md` وقرارات ADR إن وجدت. افحص الموجود وأكمله؛ لا تبدأ تطبيقًا آخر ولا تعِد scaffold ولا تستبدل migrations قائمة.

نفذ الواجهة والخلفية والتخزين والصلاحيات واختبارات السلوك المطلوبة لهذه المرحلة فعليًا. ارجع إلى الوثائق الرسمية للمكتبات والمزودين قبل استخدام API. خذ القيم الافتراضية والحدود من MASTER_SPEC؛ أي تغيير قرار له ADR وتحديث العقود، لا تغيير صامت.

**الاعتماد:** تستكمل المراحل 00 إلى 15. تحقق من الأجزاء السابقة التي تعتمد عليها؛ يمكن تجهيز عمل مستقل عن خدمة محجوبة مع إبقاء اختبار الربط محجوبًا.

**المتطلبات:** R04، R05، R06، R07، R24، R38، R44، R45، R47.

## العمل المطلوب

1. حدّث threat model من الكود الفعلي وحدود الثقة، واربط متطلبات ASVS المنطبقة بهدف Level2 بالأدلة. سجل controls غير المنطبقة أو غير المقاسة بأسباب؛ لا تصف النظام بأنه معتمد.
2. راجع authorization لكل endpoint وjob وSQL/RLS/search/storage/report وadmin feature. اختبر direct object references وbulk operations وrole mutation وcross-tenant relationships وتبديل اتصال pool.
3. راجع Email OTP/MFA/recovery والجلسات والـJWT والـcookies/CSRF وOAuth callback/state وrefresh/revoke. راجع robots/crawler/custom API SSRF وDNS rebinding وredirects وIPv6/metadata endpoints على محاكاة محلية فقط.
4. راجع validation/SQL parameterization وmass assignment وMarkdown XSS وCSP وCORS وpostMessage وuploads/archive bombs/path traversal وCSV injection وروابط downloads. API errors والسجلات والmetrics لا تكشف أسرارًا أو PII.
5. راجع prompt injection داخل مصادر وأسئلة وstyle samples وtool results؛ النموذج لا يقرر permissions أو ينفذ SQL/URLs مفتوحة. اختبر تسرب عبر retrieval caches وإصدارات محذوفة، وclaims أسعار/خصومات كاذبة.
6. نفذ أدوات فعلية مناسبة: Gitleaks للأسرار، Semgrep/SAST، pip-audit وpnpm audit/SCA، Trivy للحاويات، وOWASP ZAP baseline/authenticated scans على staging مملوكة. ثبّت versions/rules وسجل artifacts؛ لا تجعل الواجهة الخارجية هدفًا للفحص.
7. راجع secrets rotation/dependency licenses/lockfiles/SBOM، non-root/container privileges/ports/TLS/headers، limits للتكلفة والـtokens والرفع والزحف، وسجلات audit وretention/backup keys.
8. أصلح النتائج حسب الخطورة وقابلية الاستغلال، وأضف regression test لكل عيب مؤثر ثم rerun. false positive يحتاج دليلًا وتبريرًا، وليس suppression واسعًا. لا «صفر ثغرات» اعتمادًا على فاحص واحد.

## الاختبارات والقبول

تقارير threat model وASVS mapping وscans والاختبارات الهجومية الدفاعية الاصطناعية والإصلاحات. لا high/critical قابلة للاستغلال معلومة غير معالجة ضمن نطاق الإصدار؛ النتائج غير المحسومة تمنع production_ready.

الفحص التلقائي لا يعادل pentest مستقل. اكتب `docs/SECURITY_REVIEW.md` يبين ما فُحص وما لم يُفحص والحدود، وحدث تعليمات الإفصاح والاستجابة للحوادث وتدوير الأسرار دون نشر payloads ببيانات حقيقية.

## طريقة التحقق والتسليم في هذه المرحلة

- اكتب أكواد الاختبارات في المستودع، وشغّل الفحوص المتأثرة فعلًا. تحقق من النتائج وأصلح الفشل ثم أعد الفحوص اللازمة فقط. لا اختبارات تؤكد mock فحسب ولا تعطيل assertions أو security rules لتمرير النتائج.
- سجّل الأمر الفعلي والنتيجة وexit code والبيئة ونسخة الكود ومسار artifact. افصل اختبارات الوحدات والعقود عن اختبار المزود/النموذج الحي. نقص المفاتيح يسجل `blocked_external`، ولا يعادل نجاحًا.
- حدث `docs/REQUIREMENTS_TRACEABILITY.md` و`docs/PROJECT_STATE.json` و`docs/NEXT_ACTIONS.md` و`docs/IMPLEMENTATION_EXPLAINED_AR.md` وتقرير المرحلة في `docs/phase-reports/`. لا تخزن أسرارًا أو بيانات شخصية في الأدلة.
- تقرير Markdown بالعربية يوضح: المشكلة التي حلت، الملفات والوحدات، كيف تتدفق البيانات، القرارات، تعليقات الكود المهمة، أوامر التشغيل والاختبارات، ما نجح وما فشل وما لم يُختبر ولماذا، والجزء التالي بدقة.
- راجع diff واحذف الكود الميت والتكرار والمكتبات التي لم تعد لازمة لهذه المرحلة دون الإضرار بعمل المستخدم. اترك المشروع قابلًا للاستمرار.
- لا تنتقل تلقائيًا إلى مرحلة أخرى. إذا انقطع السياق، احفظ checkpoint للعمل المكتمل وأول خطوة باقية. لا تدّع اكتمال مرحلة أو جاهزية نشر قبل أدلة قبولها.
