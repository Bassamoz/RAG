# مصادر التحقق والتنفيذ

تاريخ مراجعة هذه الحزمة: 2026-11-05. هذه روابط رسمية أو صفحات المالك/المؤلف. على Codex مراجعة صفحة التكامل وقت التنفيذ وتثبيت النسخ الفعلية؛ الرابط لا يثبت توافر الخدمة لحساب الفريق.

| الموضوع | المرجع | استخدامه |
|---|---|---|
| البحث المرفق | `references/research.pdf` | المتطلبات والخوارزميات والبيانات وخطة التقييم؛ الصفحات في RESEARCH_MAP.md |
| Next.js | https://nextjs.org/docs | الواجهات والتشغيل |
| FastAPI | https://fastapi.tiangolo.com/ | API والتحقق؛ لا نضع الاستيراد الطويل في دورة request |
| Celery مع FastAPI | https://fastapi.tiangolo.com/tutorial/background-tasks/ | فصل المهام الثقيلة |
| Supabase Email OTP | https://supabase.com/docs/guides/auth/auth-email-passwordless | رمز بريد حقيقي وتحقق ينشئ جلسة |
| Supabase MFA | https://supabase.com/docs/guides/auth/auth-mfa | TOTP وفرض مستوى الضمان |
| Supabase RAG permissions | https://supabase.com/docs/guides/ai/rag-with-permissions | صلاحيات الوصول للمقاطع |
| Supabase Storage | https://supabase.com/docs/guides/storage | ملفات خاصة وروابط مقيدة |
| PostgreSQL pgvector | https://github.com/pgvector/pgvector | cosine والفهرسة والفلاتر |
| BM25S، مستودع المؤلف | https://github.com/xhluca/bm25s | BM25 وحفظ فهارس وإعادة تحميلها؛ راجع variant وlicense |
| FAISS، مستودع Meta | https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances | تطبيع المتجهات وعلاقة inner product بـcosine |
| Cross-Encoder | https://sbert.net/docs/package_reference/cross_encoder/model.html | تقييم أزواج سؤال/مقطع |
| النموذج المرشح للترتيب | https://huggingface.co/BAAI/bge-reranker-v2-m3 | نموذج متعدد اللغات؛ ثبّت revision واختبر العربية والأداء |
| مرجع Llama | https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct | مرشح محدد لعائلة البحث؛ قبول الشروط والإتاحة والvariant يحتاج توثيقًا |
| بيانات البحث | https://huggingface.co/datasets/randomath/Amazon-combined | فحص schema/count/revision؛ الترخيص لم يتضح في صفحة العرض التي قرأناها |
| OpenAI embeddings | https://developers.openai.com/api/docs/guides/embeddings | فصل التضمين عن نموذج التوليد |
| OpenAI tools | https://developers.openai.com/api/docs/guides/function-calling | استدعاء وظائف محددة ينفذها الخادم ويضبط صلاحياتها |
| Salla OAuth | https://docs.salla.dev/421118m0 | تفويض المتجر والمتجر التجريبي |
| Salla products | https://docs.salla.dev/product/list-product | مزامنة الكتالوج والحقول |
| Salla webhooks | https://docs.salla.dev/421119m0 | التحقق والأحداث |
| Salla widget | https://docs.salla.dev/2220706m0 | App Snippets |
| Zid authorization | https://docs.zid.sa/authorization | تفويض المتجر وheaders الحالية |
| Zid products | https://docs.zid.sa/retrieve-a-list-of-products | مزامنة المنتجات |
| Zid webhooks | https://docs.zid.sa/webhooks | الأحداث المدعومة |
| Zid scripts | https://docs.zid.sa/storefront-events-649611m0 | تضمين واجهة المحادثة |
| WhatsApp onboarding | https://www.postman.com/meta/whatsapp-business-platform/documentation/du6gzjv/embedded-signup | مجموعة Meta الرسمية؛ متطلبات الشريك والمراجعة |
| Meta docs | https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started | نقطة البدء؛ صفحة الويب طلبت دخولًا وقت المراجعة، لذلك يعاد التحقق أثناء الإعداد |
| Meta Embedded Signup | https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/overview | الإعداد الحي يحتاج حسابًا وصلاحيات؛ لم يمكن استرجاع الصفحة كاملة وقت إعداد الحزمة |
| OWASP ASVS | https://asvs.owasp.org/ | إطار ربط الضوابط بالاختبارات؛ الإصدار الظاهر وقت المراجعة 5.0.0 |
| OWASP SSRF | https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html | حماية استيراد الروابط والاتصالات الصادرة |
| OWASP Prompt Injection | https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html | عزل التعليمات والبيانات والدفاع متعدد الطبقات |
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ | الوصول والتباين ولوحة المفاتيح وإعادة التدفق |

ملاحظات: القيم المقترحة للتقسيم وRRF وميزانيات الأداء قرارات تصميم لهذه الحزمة، وليست نتائج تجريبية منشورة. لا يُنسخ كود مثال إنجليزي للبحث ثم يُوصف بأنه اختبار عربي. لا تعني نتيجة فحص آلي اجتياز جميع متطلبات ASVS أو WCAG.
