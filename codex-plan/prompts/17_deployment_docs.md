# المرحلة 17: النشر والمراقبة والتوثيق والتراجع

أنت مسؤول تنفيذ هذه المرحلة داخل المشروع الحالي. اقرأ تعليمات المستودع، و`codex-plan/MASTER_SPEC.md` و`codex-plan/RESEARCH_MAP.md` و`codex-plan/REQUIREMENTS.md`، ثم `docs/PROJECT_STATE.json` و`docs/NEXT_ACTIONS.md` وقرارات ADR إن وجدت. افحص الموجود وأكمله؛ لا تبدأ تطبيقًا آخر ولا تعِد scaffold ولا تستبدل migrations قائمة.

نفذ الواجهة والخلفية والتخزين والصلاحيات واختبارات السلوك المطلوبة لهذه المرحلة فعليًا. ارجع إلى الوثائق الرسمية للمكتبات والمزودين قبل استخدام API. خذ القيم الافتراضية والحدود من MASTER_SPEC؛ أي تغيير قرار له ADR وتحديث العقود، لا تغيير صامت.

**الاعتماد:** تستكمل المراحل 00 إلى 16. تحقق من الأجزاء السابقة التي تعتمد عليها؛ يمكن تجهيز عمل مستقل عن خدمة محجوبة مع إبقاء اختبار الربط محجوبًا.

**المتطلبات:** R03، R39، R46، R47.

## العمل المطلوب

1. أكمل Dockerfiles multi-stage وغير root وruntime settings وcompose production أو تعريف مكافئ، reverse proxy/TLS، health/readiness وgraceful shutdown. لا `latest` غير مثبت ولا dev server في الإنتاج.
2. خادم أولي للويب وFastAPI وworker وRedis مع Supabase managed، حدود موارد وpooling وRedis persistence/حماية شبكة وفق الحاجة. migration كعمل منفصل مرة واحدة، وoutbox recovery بعد restart. وثّق حجم الموارد من القياس لا التخمين.
3. CI/CD: lint/typecheck/tests/build/scans، artifact immutability وcommit tag، secrets منفصلة، staging deployment ثم smoke. لا تطلق على URL preview اسم إنتاج متحقق. المستخدم طلب مشروعًا قابلًا للنشر؛ جهز النشر ولا تنشر خدمة مدفوعة/عامة غير مصرح بها تلقائيًا.
4. config check/doctor يتحقق من المتغيرات والنطاقات والروابط والخدمات ويخفي القيم. تهيئة SMTP والنطاق وredirects وOAuth وwebhooks وWhatsApp ومزود AI وfonts؛ missing critical config يمنع إعلان الجاهزية.
5. observability logs/metrics/tracing منزوعة الحساسية، alerts للأخطاء وqueue lag وتعطل الاتصال وفشل النسخ والاستهلاك. أحداث RAG/المزامنة قابلة للتشخيص دون تخزين النصوص الخام بلا سياسة.
6. تمرين backup/restore وrollback على staging. تراجع التطبيق من نفس artifact، ومهاجرات متوافقة؛ لا downgrade يدمر بيانات. إيقاف outbound عند restore، وتطبيق سجل المحو الأحدث قبل فتح الخدمة.
7. أكمل README وSETUP وDEPLOYMENT وOPERATIONS وBACKUP_RESTORE وAPI وDATABASE وARCHITECTURE وTESTING وEVALUATION وSECURITY وKNOWN_LIMITATIONS وشرح التنفيذ العربي. أمثلة Linux وWindows/WSL2، وعناوين ملفات وأوامر تعمل فعلًا.
8. أضف دليل تاجر ودليل موظف بالعربية وبيانات demo موسومة في بيئة منفصلة. `IMPLEMENTATION_EXPLAINED_AR.md` يشرح الوحدات والسبب والـrequest lifecycle والخوارزميات ومسار سؤال ومصادر الإجابة والاختبارات والحدود، لا مجرد قائمة أسماء.

## الاختبارات المطلوبة

clean deploy -> migration -> health -> login OTP -> سؤال -> source update -> handoff -> export، باستخدام staging فعلية حيث توافرت المفاتيح. restart/rollback وفشل secret وDNS/SMTP/webhook configuration بطرق آمنة. لا رسائل إلى غير أرقام وصناديق اختبار مملوكة.

## القبول

يمكن لشخص آخر تشغيل المشروع من README دون خطوات مخفية. يوجد artifact بناء وإعداد نشر ودليل staging إن نُفذ، والتقرير يميز «جاهز محليًا» عن «اختبر حيًا» وعن «نُشر». العوائق الخارجية لا تختفي من التقرير النهائي.

## طريقة التحقق والتسليم في هذه المرحلة

- اكتب أكواد الاختبارات في المستودع، وشغّل الفحوص المتأثرة فعلًا. تحقق من النتائج وأصلح الفشل ثم أعد الفحوص اللازمة فقط. لا اختبارات تؤكد mock فحسب ولا تعطيل assertions أو security rules لتمرير النتائج.
- سجّل الأمر الفعلي والنتيجة وexit code والبيئة ونسخة الكود ومسار artifact. افصل اختبارات الوحدات والعقود عن اختبار المزود/النموذج الحي. نقص المفاتيح يسجل `blocked_external`، ولا يعادل نجاحًا.
- حدث `docs/REQUIREMENTS_TRACEABILITY.md` و`docs/PROJECT_STATE.json` و`docs/NEXT_ACTIONS.md` و`docs/IMPLEMENTATION_EXPLAINED_AR.md` وتقرير المرحلة في `docs/phase-reports/`. لا تخزن أسرارًا أو بيانات شخصية في الأدلة.
- تقرير Markdown بالعربية يوضح: المشكلة التي حلت، الملفات والوحدات، كيف تتدفق البيانات، القرارات، تعليقات الكود المهمة، أوامر التشغيل والاختبارات، ما نجح وما فشل وما لم يُختبر ولماذا، والجزء التالي بدقة.
- راجع diff واحذف الكود الميت والتكرار والمكتبات التي لم تعد لازمة لهذه المرحلة دون الإضرار بعمل المستخدم. اترك المشروع قابلًا للاستمرار.
- لا تنتقل تلقائيًا إلى مرحلة أخرى. إذا انقطع السياق، احفظ checkpoint للعمل المكتمل وأول خطوة باقية. لا تدّع اكتمال مرحلة أو جاهزية نشر قبل أدلة قبولها.
