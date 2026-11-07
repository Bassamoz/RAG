# خطة الشاشات

كل الصفوف عقود شاشات مقصودة، لا واجهات منفذة. الحالات المشتركة: loading/empty/error/no_permission/success، وpartial عند استيراد أو تقرير ناقص، وoffline/reconnect للمحادثة. الخط غير متوفر و`asset_required`؛ fallback نظامي للتطوير. RTL عربي وLTR إنجليزي، 360/390/768/1280/1440px وzoom وkeyboard وWCAG 2.2 AA؛ palette MASTER_SPEC فقط.

| الشاشة | الدور | الإجراء الأساسي | مصدر البيانات المقصود | المرحلة/حالة خاصة |
|---|---|---|---|---|
| تعريف/تجربة | عام | تجربة معلنة ببيانات اختبار | محتوى عام منفصل | 03؛ لا demo مخفي بالإنتاج |
| دخول/OTP | عام | إرسال ثم تحقق الرمز | Supabase عبر BFF | 02–03؛ خطأ/انتهاء/إعادة إرسال |
| MFA/استرداد | مستخدم | challenge أو طلب استرداد مدقق | Auth/AAL | 02–03؛ فقدان العامل |
| منشأة/دعوة/اختيار منشأة | مستخدم متحقق | إنشاء/قبول/تبديل | tenants/memberships/invitations | 02–03؛ دعوة منتهية أو بريد مختلف |
| onboarding | owner/admin | حفظ واستئناف | stores/setup state | 03–06؛ partial |
| overview/usage | owner/admin/analyst | تحديد فترة ومتجر | analytics/usage_events | 12؛ no-data غير صفر |
| متاجر وتكاملات | owner/admin | ربط/مزامنة/فصل | stores/integrations/sync_jobs | 05؛ setup/unavailable/expired |
| كتالوج ومتغيرات | owner/admin | تحرير يدوي/إخفاء خارجي | products/variants | 04؛ مصدر خارجي read-only |
| استيراد | owner/admin | mapping/preview/اعتماد | import job/row errors | 04؛ partial/resume |
| معرفة/مصادر/إصدارات/FAQ/سياسات | owner/admin | معاينة ثم نشر | sources/versions/chunks/policies | 04،06؛ OCR required/conflict |
| مساعد/playground | owner/admin | إعداد وتجربة | settings/retrieval/assistant | 08؛ امتناع ومراجع ومصاريف فعلية |
| inbox/محادثة | owner/admin/agent | takeover/رد | conversations/messages/events | 09،11؛ reconnect/epoch conflict |
| تذاكر/توزيع/ملاحظات داخلية | owner/admin/agent | تعيين/حل | tickets/assignments/comments | 11؛ تعارض متزامن |
| Widget/تثبيت | زائر؛ إعداد owner/admin | سؤال/طلب موظف؛ ضبط origins | visitor session/channel | 09؛ أصل مرفوض |
| WhatsApp | owner/admin | onboarding قناة أعمال | channels/provider status | 10؛ لا تفعيل بإدخال رقم |
| تحليلات/تقارير/CSAT | owner/admin/analyst | فلترة/تصدير | aggregates/export_jobs | 12؛ رابط منته/partial |
| تنبيهات | عضو | قراءة/تفضيلات | notifications | 11؛ unread/empty |
| فريق/أدوار | owner/admin | دعوة وتعديل مسموح | memberships | 02،11؛ حماية آخر مالك |
| حساب/أمان/جلسات/رقم اتصال | كل عضو لنفسه | تحقق تغيير/إبطال جلسة | users/sessions/Auth/phone provider | 02،10؛ رقم غير موثق |
| مهملات/استرجاع/محو/تصدير | owner/admin حسب السياسة | مراجعة النطاق ثم إجراء | lifecycle jobs/audit | 13؛ إعادة اعتماد قبل نشر |
| إدارة المنصة | platform_admin | صحة/تعليق/عملية استعادة مصرح بها | operations/audit | 12،13،17؛ لا تصفح روتيني لمحتوى العملاء |
