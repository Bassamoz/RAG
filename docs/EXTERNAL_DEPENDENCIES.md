# قائمة الإعداد الخارجي

المصدر codex-plan/EXTERNAL_SETUP.md؛ لا يُطلب لصق أسرار. لم توجد إعدادات أو أدلة حسابات في مساحة العمل. هذا لا يثبت عدم امتلاك المستخدم حسابًا. كل اختبار حي أدناه blocked_external؛ الخط asset_required. لا إرسال بريد أو رسالة أو إنشاء حساب خلال 00.

| ID | الخدمة | المطلوب محليًا/عند صاحب المشروع | المالك | بوابة الإثبات | الحالة |
|---|---|---|---|---|---|
| EXT-01 | Supabase | مشاريع مفصولة Auth/DB/Storage ودور محدود | 02 | RLS وهوية وملفات بقاعدة حقيقية | blocked_external |
| EXT-02 | SMTP | نطاق إرسال وصندوق اختبار وقالب رمز وSPF/DKIM/DMARC | 02 | وصول رمز والتحقق به دون تسجيله | blocked_external |
| EXT-03 | MFA | Authenticator وسياسة استرداد مدققة | 02 | منع AAL1 والسماح AAL2 | blocked_external |
| EXT-04 | Phone verification | مزود SMS وميزانية وأرقام اختبار مملوكة | 10 | تحقق رقم جديد قبل verified | blocked_external |
| EXT-05 | AI API | حساب وميزانية ومفتاح محدود ونموذج متاح بالمنطقة | 08 | real-model smoke وعزل ومصادر | blocked_external |
| EXT-06 | Cross-Encoder | ترخيص/revision وذاكرة وزمن تنزيل وتشغيل | 07 | أزواج عربية/إنجليزية حقيقية وتغير ترتيب | blocked_external |
| EXT-07 | Llama 3.1 8B | قبول الترخيص وrevision وendpoint أو GPU | 14 | نفس variant مع/دون RAG وFAISS | blocked_external |
| EXT-08 | Salla | Partners/app/scopes/test store/callback | 05 | OAuth/import/update/refresh/revoke فعلية | blocked_external |
| EXT-09 | Zid | Partner app/test store/scopes/callback | 05 | دورة موصل مستقل فعلية | blocked_external |
| EXT-10 | Custom store | تفويض نطاق/API أو ملف مملوك | 05 | مقارنة الحقول والعدد وأخطاء الصفوف | blocked_external |
| EXT-11 | Meta WhatsApp | App/WABA/business phone/test recipient وpermissions | 10 | inbound/reply/status/handoff حية | blocked_external |
| EXT-12 | Hosting | حساب ونطاق وDNS وsecret manager | 17 | staging smoke/TLS/rollback | blocked_external |
| EXT-13 | Backup | وجهة خاصة ومفاتيح منفصلة | 13 | استرجاع DB+files معزول وقياس RPO/RTO | blocked_external |
| EXT-14 | Thmanyah font | ملفات مرخصة بأوزان الويب | 03 | تحميل الخط وRTL screenshots | asset_required |
| EXT-15 | Dataset | revision/hash/schema/count/license قبل توزيع البيانات | 14 | manifest provenance وفصل gold | blocked_external |

## فحص مبكر في 2026-11-06

- [Salla authorization](https://docs.salla.dev/421118m0) و[Zid authorization](https://docs.zid.sa/authorization): استرجعت الوثائق العامة؛ لا اختبار حساب/تطبيق أو موافقة scopes. إعادة مراجعة التفاصيل عند 05.
- [Meta get started](https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started): الصفحة المعادة Not Logged In؛ لا إثبات جاهزية WABA أو رقم أو موافقة.
- [Supabase email OTP](https://supabase.com/docs/guides/auth/auth-email-passwordless): الوثائق متاحة وتصف خطوة الإرسال والتحقق؛ لم يُرسل رمز ولا اختُبر SMTP.
- [Llama model card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct): متاحة؛ الترخيص llama3.1 مع حاجة تحقق الإتاحة الفعلية للحساب. لم تُنزّل أوزان ولم ينفذ inference.
- [Amazon-combined](https://huggingface.co/datasets/randomath/Amazon-combined): العرض العام نحو 2.98k train؛ لم يثبت ترخيص/revision للتنزيل. ليس artifact dataset مثبتًا.

الخطوة العملية التالية لكل مالك خدمة: إعداد sandbox مملوك وأسماء إعدادات في secret manager/ملف مستثنى ثم اختبار حي بالمرحلة المالكة؛ لا تُسجل قيمة token أو OTP أو بيانات عميل في الأدلة.
