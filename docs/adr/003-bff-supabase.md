# ADR-003: هوية Supabase وBFF

## الحالة
قرار تخطيط وفق المواصفات المطلوبة؛ التنفيذ غير متحقق.

## التاريخ
2026-11-06

## السياق
MASTER_SPEC §5 يفصل Email OTP وTOTP ورقم الاتصال وقناة WhatsApp؛ ERD البحث يحوي password_hash.

## القرار
مزود هوية واحد؛ BFF server-only يدير tokens مشفرة وتجديدًا مقفلًا؛ المتصفح معرف جلسة HttpOnly Secure مع CSRF. API يتحقق JWT وعضوية وجلسة فعالة. لا password_hash محلي.

## البدائل
client-readable token flow مختلف عن هذا العقد؛ لا نخلط نموذجَي cookies. auth مخصص يكرر مسؤولية المزود ويزيد المخاطر.

## النتائج والتحقق
PoC الجلسة في 02 شرط حسم SDK/version. إرسال OTP لا ينشئ جلسة قبل التحقق؛ اختبار البريد الحي محجوب حتى إعداد SMTP. https://supabase.com/docs/guides/auth/auth-email-passwordless
