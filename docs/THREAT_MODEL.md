# نموذج تهديد أولي

الأصول: جلسات وtokens مزودين، محتوى العملاء، معرفة المتجر، صحة السعر، صلاحيات النشر والمحو، ميزانية النموذج. الجهات: زائر مسيء، عضو مستأجر آخر، عضو محدود، مستند/مزود خبيث، job متأخر، مشغل ذو امتياز. لا ضوابط منفذة بعد.

حدود الثقة: browser→BFF/API؛ قناة→webhook/inbox؛ API→DB/RLS/storage؛ outbox→worker؛ worker→URL/provider/model؛ document→parser/index/prompt؛ cache/vector/export→recipient؛ backup→restore. LLM output والمستندات بيانات غير موثوقة، وليس مصدر تفويض.

| STRIDE/الخطر | الضبط المخطط | اختبار إساءة ومالك |
|---|---|---|
| S/E: OTP/session/JWT/MFA abuse | مزود واحد، AAL2، CSRF، قفل refresh، revocation، حدود إعادة إرسال | رمز معاد/منتهي وAAL1 وlogout/race، 02 |
| E/I: BOLA/BFLA وتسرب pool | عضوية فعالة، tenant/store RLS وFK مركبة وtransaction-local؛ دور بلا BYPASSRLS | معرف متجر آخر وconnection reuse وكل دور، 02 ثم كل وحدة |
| T: injection/mass assignment | schemas/allowlists وSQL parameters ونسخة optimistic | حقول دور إضافية وSQL payload، 01–04 |
| I/T: XSS/Markdown/widget/CSRF | encoding وsanitization وCSP وorigin checks وCSRF token | روابط script/postMessage خاطئ/طلب cross-site، 03،09 |
| S/T/R: webhook/OAuth replay | state one-use مرتبط بالجلسة، تحقق خاص بالمزود، durable inbox ودقة idempotency | callback معاد أو tenant مختلف وتوقيع خاطئ/out-of-order، 05،10 |
| I/E: SSRF/traversal/rebinding | تفويض نطاق وegress pinning؛ منع private IPv4/IPv6 وredirect؛ storage paths خادمية | metadata/DNS switch/redirect/path escape، 05–06 |
| D/T: ملف خبيث/zip bomb/formula | حجر magic/type/size/expansion/time؛ no macros؛ CSV neutralization | ملف مصطنع كبير وصيغة export، 04،06،12 |
| T/I/E: prompt injection/poisoning | فصل policy/data؛ نشر بمراجعة؛ أدوات محدودة؛ فحص مصادر/أرقام قبل إرسال | مستند يطلب أسرارًا/سعرًا مزورًا/مصدر محذوف، 06–08 |
| I: vector/cache/file/export leak | مفاتيح store/version/permissions وروابط خاصة منتهية وإعادة تحقق authoritative | بحث متجرين وrevocation قبل export، 07،12–13 |
| D/R: cost abuse/queue failures | quotas/timeouts/backoff/outbox/checkpoints وقياس structured redacted | crash/retry/429/unknown send، 05،10،15 |
| T/E: takeover أو حذف يتسابق مع job | epoch/version وفحص نهائي قبل إرسال؛ tombstone وموانع إحياء | takeover أثناء generation وحذف أثناء indexing، 09،13 |
| I/R: logs/backup/restore | allowlist logs وrequest_id/entryPoint؛ encryption؛ minimal audit؛ outbound off | فحص عدم تسريب OTP وإعادة تطبيق المحو في restore، 13،17 |

## ASVS

الهدف ASVS 5.0.0 Level 2 وفق [الإصدار الرسمي](https://asvs.owasp.org/). الربط هنا على مستوى فئات الضوابط تمهيدي: authentication/session→02؛ authorization→02 وكل وحدة؛ validation/encoding/files→04/06/09؛ API/OAuth→05/10؛ data protection/cryptography/configuration/logging→01/13/17؛ business logic/concurrency→08/09/13/15. في 16 تُستورد قائمة المتطلبات الرسمية بإصدارها وتُربط معرفات البنود الدقيقة بأدلة واختبارات؛ لا معرفات مخترعة أو دعوى تغطية كاملة الآن. مدفوعات وتخزين password_hash محلي غير منطبقين لهذا النطاق، مع بقاء تفويض الهوية وحماية tokens منطبقين.

مخاطر متبقية: موافقات المزودين، لغة النموذج ودقته، سلامة parser، صلاحيات operators، حذف النسخ الاحتياطية. تعالج بالاختبارات والأدلة لا بوصف «آمن» مطلق. لا فحص هجومي لمزود خارجي.
