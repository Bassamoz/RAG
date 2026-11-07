# خطة التنفيذ بعد تدقيق 00

مصدر الخطة prompts/01–18 ومعايير R01–R48 في سجل التتبع؛ لا تنفيذ تلقائي. تعتمد كل مرحلة على السابقة وأدلتها، ويمكن إنجاز جزء مستقل عند blocked_external دون تمرير gate المحجوب. المرحلة 00 فقط هي المنجزة الآن.

| المهمة/المرحلة | الناتج ومعيار القبول | التحقق المقترح | الملفات/الوحدات المتوقعة |
|---|---|---|---|
| 01 | أساس واحد وlockfiles وmigrations وعقد OpenAPI وCI؛ R03 | clean setup/rerun/migration/build/checks | web/api/worker/infra/contracts |
| 02 | OTP/MFA/BFF وعضوية وعزل؛ R04–07 | invalid/expired/revoked/AAL1/RLS/pool tests ثم بريد حي | identity/tenancy |
| 03 | RTL/LTR وonboarding قابل للاستئناف؛ R08–09 | keyboard/axe/zoom/screenshots وحفظ الرحلة | web/design/onboarding |
| 04 | كتالوج وسياسات واستيراد؛ R10–11 | Decimal/variants/CSV mapping/partial/formula | catalog/import |
| 05 | سلة وزد ومتجر خاص ومزامنة؛ R12–15 | عقود مستقلة + حسابات حقيقية وrefresh/replay/429 | integrations/sync |
| 06 | معرفة وتقسيم وإصدارات ونشر؛ R16–18 | extraction failures/publish/delete race | knowledge/storage |
| 07 | BM25/cosine/FAISS/RRF/Cross-Encoder؛ R19–22 | vectors/scores معروفة وعزل ونموذج ترتيب حقيقي | retrieval/indexes |
| 08 | نيات وأدوات ومصادر وامتناع؛ R23–26،29 | injection/نقص دليل/سعر متغير/تحقق عميل | assistant/tools |
| 09 | widget ومحادثة وتحويل وتوقيت؛ R27–29 | origin/reconnect/epoch/fake clock/E2E | channels/conversations |
| 10 | رقم اتصال مستقل وWhatsApp رسمي؛ R30–32 | تحقق رقم ورسالة sandbox فعلية وunknown send | channels/phone |
| 11 | موظف وتذاكر وتوزيع وتنبيه؛ R28،33–34 | assignment concurrency ومنع رد bot بعد takeover | support/notifications |
| 12 | مقاييس وتقارير واستهلاك؛ R35–36 | denominator/timezone/no-data/export permissions | analytics/reports |
| 13 | حذف ومحو واسترجاع ونسخ؛ R18،37–39 | late jobs/restore checksums/outbound off/erasure replay | lifecycle/backup |
| 14 | provenance وbenchmark؛ R40–41 | frozen test وablations بنفس Llama/FAISS وتقارير فعلية | evaluation/datasets |
| 15 | نظام وحمل وتعافٍ؛ R42–43 | رحلات كل دور وk6/crash/concurrency وفق الميزانيات | tests/e2e/load |
| 16 | تدقيق ومعالجة أمن؛ R44–45 | ASVS item mapping وفحوص فعلية وإعادة اختبار الإصلاح | security/evidence |
| 17 | نشر وrollback وتشغيل؛ R39،46 | staging smoke/TLS/SMTP/restore/rollback | infra/runbooks |
| 18 | قرار إصدار صادق؛ R48 | جميع بوابات النطاق على commit محدد دون pass للمتروك | release/evidence |

R02 وR47 تحديث مستمر بكل مرحلة. كل صف كبير يُقسم في مرحلته إلى شرائح 1–5 ملفات حسب الاعتماديات: عقد/سياسة ثم مسار كامل واختباره، دون كتابة جداول فارغة لكامل المنصة في 01. نقاط المراجعة: بعد 02 العزل والهوية، بعد 07 صحة الاسترجاع، بعد 10 الحسابات والقنوات، بعد 14 المنهج، وبعد 17 الاسترجاع والتشغيل. لا تعني مراجعة التخطيط قبول نتائج لم تُقَس.

## المخاطر والقرارات المفتوحة

أعلى المخاطر: BFF/session وRLS واختبارات pool؛ صلاحيات OAuth وMeta؛ ترخيص dataset وإتاحة Llama وذاكرة reranker؛ أسعار ومخزون متقادمان؛ محو/restore وإرسال مكرر. تُقدّم تجاربها الصغيرة في المراحل المالكة. النسخ الدقيقة وSDK وscopes وhardware/revisions تُحسم بالدليل قبل التنفيذ؛ الاختيار العام محسوم بالمواصفات ولا يعاد فتحه بصمت. ميزانيات الأداء المقترحة في ACCEPTANCE_BUDGETS ليست قياسًا.
