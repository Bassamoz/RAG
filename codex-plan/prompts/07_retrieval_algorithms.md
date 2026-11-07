# المرحلة 07: BM25 والبحث الدلالي وFAISS والدمج وإعادة الترتيب

أنت مسؤول تنفيذ هذه المرحلة داخل المشروع الحالي. اقرأ تعليمات المستودع، و`codex-plan/MASTER_SPEC.md` و`codex-plan/RESEARCH_MAP.md` و`codex-plan/REQUIREMENTS.md`، ثم `docs/PROJECT_STATE.json` و`docs/NEXT_ACTIONS.md` وقرارات ADR إن وجدت. افحص الموجود وأكمله؛ لا تبدأ تطبيقًا آخر ولا تعِد scaffold ولا تستبدل migrations قائمة.

نفذ الواجهة والخلفية والتخزين والصلاحيات واختبارات السلوك المطلوبة لهذه المرحلة فعليًا. ارجع إلى الوثائق الرسمية للمكتبات والمزودين قبل استخدام API. خذ القيم الافتراضية والحدود من MASTER_SPEC؛ أي تغيير قرار له ADR وتحديث العقود، لا تغيير صامت.

**الاعتماد:** تستكمل المراحل 00 إلى 06. تحقق من الأجزاء السابقة التي تعتمد عليها؛ يمكن تجهيز عمل مستقل عن خدمة محجوبة مع إبقاء اختبار الربط محجوبًا.

**المتطلبات:** R18، R19، R20، R21، R22، R47.

## العمل المطلوب

1. interfaces صغيرة لـSparseRetriever وDenseRetriever وReranker وإدارة index versions. استخدمها في البحث والتشغيل دون pipeline مكرر.
2. BM25 حقيقي عبر bm25s مع tokenizer عربي/إنجليزي ومعاملات موثقة. فهرس store/version منفصل، chunk ID mapping وchecksum وatomic swap وcache invalidation. لا تستبدل BM25 بـILIKE أو ts_rank أو cosine.
3. pgvector cosine وقيود scope/visibility/version قبل الاسترجاع؛ اختبر تأثير approximate index بعد الفلترة مقابل exact. FAISS بحثي باستخدام normalized vectors وinner product وخريطة IDs معزولة ومتحقق منها؛ لا تحمل ملف فهرس من مستخدم غير موثوق.
4. نفذ المسارين بالتوازي داخل حدود الموارد، RRF موثق بمعادلة المواصفات، ثم dedup وCross-Encoder حقيقي. حمّل نموذج rerank مرة وبميزانية concurrency/timeout، مع تسجيل version ووقت كل مرحلة.
5. طبق topK/threshold/context budgets، وعدم خلط درجات BM25 وcosine الخام بجمع غير مبرر. المرجحات قابلة للمعايرة على dev فقط. التقييم النهائي يستخدم إعدادًا مثبتًا.
6. أعد التحقق من المصدر المنشور والصلاحية والحذف من DB قبل تسليم المقاطع. أسماء الملفات الخارجية لا تتحول مسارات فهارس خادم. cache key يضم tenant/store/index/model/visibility.
7. شاشة تجريب للتاجر تعرض نتائج البحث ومراجعها ومراتبها ومددها مع تنبيه أن score ليس ثقة معايرة. الواجهة الداخلية لا تكشف corpus لأي متجر آخر.

## الاختبارات المطلوبة

`test_bm25_reference_ranking`، `test_cosine_known_vectors`، `test_faiss_cosine_parity`، `test_rrf_merge`، `test_reranker_contract`، `test_index_version_swap`، `test_retrieval_tenant_isolation`.

اختبر term frequencies/length/rare SKU، متجهات متعامدة/متطابقة/صفرية، lists فارغة/متكررة/ties، normalized query وdocument، عدم تطابق dimensions، مصدر خاص/محذوف، cache قديم وworker متزامن.

شغّل smoke حقيقيًا للـCross-Encoder على أزواج عربية/إنجليزية وتحقق أن النتائج ليست mock؛ اجعل assertions مبنية على corpus موثوق لا وعد ترتيب عالمي. قارن FAISS وpgvector على vectors نفسها ضمن tolerance.

## القبول

كل خوارزمية موجودة ويمكن تتبع أثرها في logs منزوعة الحساسية والتقييم. غياب النموذج يسجل تعطلًا/عائقًا، ولا يسقط reranker صامتًا مع ادعاء تنفيذ البحث كله.

## طريقة التحقق والتسليم في هذه المرحلة

- اكتب أكواد الاختبارات في المستودع، وشغّل الفحوص المتأثرة فعلًا. تحقق من النتائج وأصلح الفشل ثم أعد الفحوص اللازمة فقط. لا اختبارات تؤكد mock فحسب ولا تعطيل assertions أو security rules لتمرير النتائج.
- سجّل الأمر الفعلي والنتيجة وexit code والبيئة ونسخة الكود ومسار artifact. افصل اختبارات الوحدات والعقود عن اختبار المزود/النموذج الحي. نقص المفاتيح يسجل `blocked_external`، ولا يعادل نجاحًا.
- حدث `docs/REQUIREMENTS_TRACEABILITY.md` و`docs/PROJECT_STATE.json` و`docs/NEXT_ACTIONS.md` و`docs/IMPLEMENTATION_EXPLAINED_AR.md` وتقرير المرحلة في `docs/phase-reports/`. لا تخزن أسرارًا أو بيانات شخصية في الأدلة.
- تقرير Markdown بالعربية يوضح: المشكلة التي حلت، الملفات والوحدات، كيف تتدفق البيانات، القرارات، تعليقات الكود المهمة، أوامر التشغيل والاختبارات، ما نجح وما فشل وما لم يُختبر ولماذا، والجزء التالي بدقة.
- راجع diff واحذف الكود الميت والتكرار والمكتبات التي لم تعد لازمة لهذه المرحلة دون الإضرار بعمل المستخدم. اترك المشروع قابلًا للاستمرار.
- لا تنتقل تلقائيًا إلى مرحلة أخرى. إذا انقطع السياق، احفظ checkpoint للعمل المكتمل وأول خطوة باقية. لا تدّع اكتمال مرحلة أو جاهزية نشر قبل أدلة قبولها.
