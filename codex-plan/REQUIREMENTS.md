# سجل المتطلبات ومعايير القبول

تُنسخ هذه المصفوفة إلى `docs/REQUIREMENTS_TRACEABILITY.md` في المرحلة 00 وتُحدّث حالة التنفيذ والأدلة هناك؛ لا تغيّر معنى المتطلب لجعل اختبار فاشل ينجح. الاختبارات أدناه حد أدنى قائم على المخاطر، وليست دعوى حصر كل حالة ممكنة.

| ID | المتطلب | المرحلة المالكة | دليل القبول الأدنى |
|---|---|---|---|
| R01 | استخراج البحث وتوثيق التعارضات | 00 | صفحات وADR وفصل research/production |
| R02 | مستودع واحد ومراحل قابلة للاستئناف | 00–18 | حالة وتقرير وnext actions دون تطبيق مكرر |
| R03 | بيئة وتشغيل ومهاجرات قابلة للإعادة | 01 | clean setup ثم rerun ثم DB migration من نسخة أقدم |
| R04 | Email OTP حقيقي | 02 | رمز صحيح/خطأ/منتهي/مكرر، إعادة إرسال وضبط إساءة الاستخدام، بريد حي قبل الإصدار |
| R05 | جلسات آمنة وتسجيل خروج وإبطال | 02 | cookie/CSRF/JWT/refresh races/revocation بعد تبديل دور |
| R06 | TOTP MFA وأدوار ودعوات | 02 | منع AAL1، دعوة منتهية/معادة/ببريد مختلف، منع إزالة آخر مالك |
| R07 | عزل tenant/store شامل | 02 وما بعدها | محاولات API/DB/vector/cache/jobs/files/export بين مستأجرين ممنوعة |
| R08 | UI عربي/إنجليزي وألوان ووصول | 03 | screenshots RTL/LTR، keyboard، contrast، axe، mobile/zoom |
| R09 | onboarding قابل للحفظ والاستمرار | 03–06 | ترك العملية واستئنافها دون ضياع أو تكرار متجر |
| R10 | كتالوج ومتغيرات وسياسات CRUD | 04 | validation/Decimal/currency/variant وoptimistic concurrency |
| R11 | استيراد CSV/XLSX | 04 | mapping/preview/row errors/dedup/formula handling وrollback جزئي موثق |
| R12 | ربط سلة الحقيقي | 05 | OAuth state/scopes/pagination/refresh/revoke، وتجربة متجر حقيقية |
| R13 | ربط زد الحقيقي | 05 | عقود مستقلة وheaders صحيحة وتجربة متجر حقيقية |
| R14 | متجر خاص وقراءة صفحات مصرح بها | 05–06 | تفويض نطاق وcapabilities وحدود جلب وSSRF tests |
| R15 | مزامنة موثوقة | 05 | duplicate/out-of-order/429/retry/resume وحذف منتج وتغير سعر |
| R16 | معرفة FAQ/ملفات/نصوص/صفحات | 06 | رفع وإضافة وتعديل ومعاينة واعتماد مع extraction failures |
| R17 | تقسيم دلالي وتنظيف ونسخ | 06 | الحفاظ على الاستثناءات وSKU والنفي ومراجع الصفحة وإصدار النموذج |
| R18 | نشر ذري وحذف يمنع الاسترجاع | 06–07،13 | إلغاء مصدر أثناء indexing أو query لا يعيد استخدامه |
| R19 | BM25 حقيقي | 07 | مجموعة مرجعية وحساب متوقع/مقارنة مكتبة وtokens عربية/إنجليزية |
| R20 | Cosine + pgvector | 07 | vectors معروفة وzero/empty/dimension mismatch وtenant filters |
| R21 | FAISS أكاديمي | 07،14 | L2 normalization ونتائج cosine مكافئة على corpus صغير معزول |
| R22 | دمج RRF ثم Cross-Encoder | 07 | union/dedup/ties وreranker حقيقي واختبار تغير الترتيب |
| R23 | orchestration ونوايا متعددة الأدوار | 08 | الأنواع الثمانية، ضمير مبهم، SKU ونفي وسياق متجر واحد |
| R24 | مصادر وامتناع وضوابط RAG | 08 | غياب دليل/تعارض/injection/مصدر محذوف/ادعاء سعر غير مدعوم |
| R25 | أسعار ومخزون حديثان | 08 | تغير متغير/خصم/عملة وتعطل المزود يمنع تأكيد بيانات قديمة |
| R26 | تتبع طلب خاص read-only عند توفر التحقق | 08 | رقم طلب أو رقم WhatsApp وحدهما لا يكفيان؛ عزل العميل |
| R27 | Widget قابل للتضمين | 09 | مواقع اختبار مختلفة، origin validation، reconnect، منع XSS |
| R28 | آلة حالات المحادثة والتحويل | 09،11 | takeover أثناء generation/retry، عدم رد البوت بعد الاستلام |
| R29 | نبرة وتوقيت البحث | 08–09،14 | إعداد يدوي/استخراج منزوع الهوية؛ fake-clock أول/لاحق دون تأخير الموظف |
| R30 | تحقق رقم الاتصال وتغييره | 10 | لا verified قبل OTP صحيح؛ إعادة تحقق وتدقيق تغيير الرقم |
| R31 | WhatsApp Business رسمي | 10 | onboarding/WABA ownership/signature ورسالة حية من رقم اختبار |
| R32 | إرسال WhatsApp وحالاته | 10 | dedup/window/template/status ordering وtimeout unknown بلا إرسال مكرر أعمى |
| R33 | مساحة موظف وتذاكر وتوزيع | 11 | assignment/priority/comments/internal notes وعمليات متزامنة وصلاحيات |
| R34 | تنبيهات داخلية وبريد اختياري | 11 | unread/read/preferences وعدم إرسال أسرار أو رسائل لأطراف غير مخولة |
| R35 | تحليلات وCSAT واستهلاك | 12 | تعريف المقاييس وdenominator/timezone وحالات no-data ومنع استنتاجات بلا baseline |
| R36 | تقارير وتصدير | 12 | CSV/XLSX/PDF/MD حسب التقرير، RTL وحقول صحيحة وروابط منتهية وصلاحيات |
| R37 | soft delete/trash/restore | 13 | نطاق متجر وصلاحية وتعارض إصدار وإعادة اعتماد قبل النشر |
| R38 | محو نهائي واحتفاظ | 13 | DB/storage/vector/BM25/cache/jobs؛ لا إحياء بعد job متأخر |
| R39 | backup وrestore فعلي | 13،17 | استعادة DB+files معزولة وchecksums وRPO/RTO مقاسان وحظر outbound |
| R40 | provenance dataset | 14 | revision/hash/schema/license/count، فصل بيانات المحاكاة عن الواقع |
| R41 | benchmark وablations | 14 | Llama نفسه مع/دون RAG، gold labels، dev/test، مقاييس حقيقية بلا fabricated scores |
| R42 | اختبارات وظيفية وE2E | 15 | رحلة كاملة للتاجر والعميل والموظف والإدارة لكل دور |
| R43 | load/resilience/concurrency | 15 | workload محدد وأرقام فعلية و429/timeouts/queue crashes/recovery |
| R44 | threat model وASVS mapping | 00،16 | ضوابط مبكرة ثم مراجعة تغطية المستوى المستهدف دون دعوى اعتماد |
| R45 | SAST/SCA/secrets/container/DAST | 16 | artifacts فعلية وإصلاح وإعادة اختبار؛ staging مصرح به فقط |
| R46 | نشر وإعدادات وخطة rollback | 17 | staging smoke وmigrations وTLS/SMTP/secrets وrollback موثق |
| R47 | شرح عربي MD وتعليقات مفيدة | كل مرحلة | IMPLEMENTATION_EXPLAINED_AR.md محدث بعقود ومثال وتشغيل واختبارات وحدود |
| R48 | بوابة إصدار صادقة | 18 | commit محدد وأدلة جديدة، blockers ظاهرة، لا pass لskipped |

قالب أعمدة الإثبات في نسخة المشروع: `ID | source | phase | implementation_paths | test_ids | evidence_path | environment | result | limitation | verified_at | commit`.

درجات الحالات: planned، in_progress، implemented، verified_local، verified_live، blocked_external، failed، not_applicable_with_reason. `implemented` ليس `verified`.
