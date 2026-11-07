# ADR-005: BM25 وRRF وCross-Encoder

## الحالة
قرار تخطيط وفق المواصفات المطلوبة؛ التنفيذ غير متحقق.

## التاريخ
2026-11-06

## السياق
PDF 41–48 و99 و102 يفرض المسارين والدمج ثم إعادة الترتيب، لكنه لا يسمي RRF.

## القرار
bm25s حقيقي؛ cosine ثم union/dedup وRRF k=60 ثم Cross-Encoder متعدد اللغات مرشح bge-reranker-v2-m3. k1=1.2 b=0.75 و30 مرشحًا ثم 5–8 سياق قيم بدء من MASTER_SPEC، IDF/tokenizer/revision توثق في 07.

## البدائل
ts_rank أو cosine باسم reranker غير مطابقين. concatenation دون fusion لا يحدد ties. RRF إضافة هندسية لعدم قابلية scores للمقارنة مباشرة.

## النتائج والتحقق
رقميًا: empty/ties/ranks/dedup وreranker حقيقي؛ ablations بنفس النموذج والأسئلة في 14؛ لا scores أو نتائج الآن.
